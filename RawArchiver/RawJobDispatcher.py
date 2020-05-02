import sys
import multiprocessing
import threading
import time
import traceback
import queue
import random
import datetime
import signal
import socket

import settings
import WebMirror.JobUtils
import RawArchiver.misc

import common.NetlocThrottler
import common.get_rpyc
import common.util.urlFuncs
import common.process
import common.LogBase as LogBase
import common.StatsdMixin as StatsdMixin


# import sqlalchemy.exc
# from sqlalchemy.sql import text

if '__pypy__' in sys.builtin_module_names:
	import psycopg2cffi as psycopg2
else:
	import psycopg2


########################################################################################################################
#
#	##     ##    ###    #### ##    ##     ######  ##          ###     ######   ######
#	###   ###   ## ##    ##  ###   ##    ##    ## ##         ## ##   ##    ## ##    ##
#	#### ####  ##   ##   ##  ####  ##    ##       ##        ##   ##  ##       ##
#	## ### ## ##     ##  ##  ## ## ##    ##       ##       ##     ##  ######   ######
#	##     ## #########  ##  ##  ####    ##       ##       #########       ##       ##
#	##     ## ##     ##  ##  ##   ###    ##    ## ##       ##     ## ##    ## ##    ##
#	##     ## ##     ## #### ##    ##     ######  ######## ##     ##  ######   ######
#
########################################################################################################################


NO_JOB_TIMEOUT_MINUTES = 15


largv = [tmp.lower() for tmp in sys.argv]
if "twoprocess" in largv or "oneprocess" in largv:
	MAX_IN_FLIGHT_JOBS = 2
else:
	# MAX_IN_FLIGHT_JOBS = 5
	# MAX_IN_FLIGHT_JOBS = 15
	# MAX_IN_FLIGHT_JOBS = 40
	MAX_IN_FLIGHT_JOBS = 75
	# MAX_IN_FLIGHT_JOBS = 250
	# MAX_IN_FLIGHT_JOBS = 500
	# MAX_IN_FLIGHT_JOBS = 1000
	# MAX_IN_FLIGHT_JOBS = 3000


LOCAL_ENQUEUED_JOB_RESPONSES = 5

class RawJobFetcher(LogBase.LoggerMixin, StatsdMixin.StatsdMixin):

	loggerPath = "Main.RawJobFetcher"
	statsd_prefix = 'ReadableWebProxy.Proc.RawDispatcherManager'

	def __init__(self):
		# print("Job __init__()")
		super().__init__()

		self.last_rx = datetime.datetime.now()
		self.active_jobs = 0
		self.jobs_out    = 0
		self.jobs_in     = 0

		self.run_flag = multiprocessing.Value("b", 1, lock=False)

		self.ratelimiter = common.NetlocThrottler.NetlockThrottler(key_prefix='raw', fifo_limit = 100 * 1000)

		self.count_lock = threading.Lock()
		self.limiter_lock = threading.Lock()
		self.local = threading.local()

		# This queue has to be a multiprocessing queue, because it's shared across multiple processes.
		self.normal_out_queue  = multiprocessing.Queue(maxsize=MAX_IN_FLIGHT_JOBS * 2)
		self.fetch_procs = {
			"filler-priority"  : threading.Thread(target=self.filler_run_shim, args=('priority', )),
			"filler-new_fetch" : threading.Thread(target=self.filler_run_shim, args=('new_fetch', )),
			"filler-random"    : threading.Thread(target=self.filler_run_shim, args=('random', )),
			"consumer"         : threading.Thread(target=self.drainer_run_shim),
			"consumer"         : threading.Thread(target=self.drainer_run_shim),
			"consumer"         : threading.Thread(target=self.drainer_run_shim),
		}

		for proc in self.fetch_procs.values():
			proc.start()

		self.print_mod = 0


	def filler_run_shim(self, mode):


		try:
			self.queue_filler_proc(mode)

		except KeyboardInterrupt:
			print("Saw keyboard interrupt. Breaking!")
			return

		except Exception:
			print("Error!")
			print("Error!")
			print("Error!")
			print("Error!")
			traceback.print_exc()
			with open("error %s - %s.txt" % ("rawjobdispatcher", time.time()), "w") as fp:
				fp.write("Manager crashed?\n")
				fp.write(traceback.format_exc())
			raise


	def drainer_run_shim(self):

		self.local.db_interface = psycopg2.connect(
				database = settings.DATABASE_DB_NAME,
				user     = settings.DATABASE_USER,
				password = settings.DATABASE_PASS,
				host     = settings.DATABASE_IP,
			)

		try:
			self.queue_drainer_proc()

		except KeyboardInterrupt:
			print("Saw keyboard interrupt. Breaking!")
			return

		except:
			print("Error!")
			print("Error!")
			print("Error!")
			print("Error!")
			traceback.print_exc()
			with open("error %s - %s.txt" % ("rawjobdispatcher", time.time()), "w") as fp:
				fp.write("Manager crashed?\n")
				fp.write(traceback.format_exc())
			raise



	def outbound_job_wanted(self, netloc, joburl):

		bad = common.util.urlFuncs.hasDuplicateSegments(joburl)
		if bad:
			self.log.warn("Unwanted URL (pathchunks): '%s' - %s", joburl, bad)
			return False

		if joburl.startswith("data:"):
			self.log.warn("Data URL: '%s' - %s", joburl, netloc)
			return False
		if joburl.startswith("mailto:"):
			self.log.warn("Email URL: '%s' - %s", joburl, netloc)
			return False
		if not joburl.startswith("http"):
			self.log.warn("Non HTTP URL: '%s' - %s", joburl, netloc)
			return False
		for module in RawArchiver.RawActiveModules.ACTIVE_MODULES:
			if module.cares_about_url(joburl):
				return True

		self.log.warn("Unwanted URL: '%s' - %s", joburl, netloc)

		return False

	def outbound_job_disabled(self, netloc, joburl):

		for module in RawArchiver.RawActiveModules.ACTIVE_MODULES:
			if module.cares_about_url(joburl):
				if module.is_disabled(netloc, joburl):
					self.log.warn("Disabled fetching for URL: '%s' - %s", joburl, netloc)
					return True
		return False

	def get_queue(self):
		return self.normal_out_queue

	def join_proc(self):
		self.run_flag.value = 0

		for _ in range(60 * 5):
			for proc in self.fetch_procs.values():
				proc.join(1)
				if any([tmp.is_alive() for tmp in self.fetch_procs.values()]) is False:
					return
				self.log.info("Waiting for job dispatcher to join. Currently active jobs in queue: %s, states: %s",
						self.normal_out_queue.qsize(),
						[tmp.is_alive() for tmp in self.fetch_procs.values()]
					)

		while True:
			for proc in self.fetch_procs.values():
				proc.join(1)
				if any([tmp.is_alive() for tmp in self.fetch_procs.values()]) is False:
					return
				self.log.error("Timeout when waiting for join. Bulk consuming from intermediate queue. States: %s",
						[tmp.is_alive() for tmp in self.fetch_procs.values()],
					)
				try:
					while 1:
						self.normal_out_queue.get_nowait()
				except queue.Empty:
					pass


	def put_outbound_job(self, jobid, joburl, netloc=None):
		with self.count_lock:
			self.log.info("Dispatching new job (active jobs: %s of %s)", self.active_jobs, MAX_IN_FLIGHT_JOBS)
		raw_job = WebMirror.JobUtils.buildjob(
			module         = 'SmartWebRequest',
			call           = 'smartGetItem',
			dispatchKey    = "fetcher",
			jobid          = jobid,
			args           = [joburl],
			kwargs         = {},
			additionalData = {'mode' : 'fetch', 'netloc' : netloc},
			postDelay      = 0
		)

		# Recycle the rpc interface if it ded
		while 1:
			try:
				self.local.rpc_interface.put_job(raw_job)
				with self.count_lock:
					self.active_jobs += 1
					self.jobs_out += 1
					with self.mon_con.pipeline() as pipe:
						pipe.gauge('active_jobs', self.active_jobs)
						pipe.gauge('jobs_out',    self.jobs_out)
						pipe.gauge('jobs_in',     self.jobs_in)
						pipe.gauge('qsize',       self.normal_out_queue.qsize())


				return
			except TypeError:
				self.open_rpc_interface()
			except KeyError:
				self.open_rpc_interface()
			except socket.timeout:
				self.open_rpc_interface()
			except ConnectionRefusedError:
				self.open_rpc_interface()

	def fill_jobs(self, mode):

		if 'drain' in sys.argv:
			return
		escape_count = 0

		with self.count_lock:
			current_active = self.active_jobs

		while current_active < MAX_IN_FLIGHT_JOBS and escape_count < 25 and self.normal_out_queue.qsize() < LOCAL_ENQUEUED_JOB_RESPONSES:
			old = self.normal_out_queue.qsize()
			num_new = self._get_task_internal(mode)
			with self.count_lock:
				current_active = self.active_jobs
				self.log.info("Need to add jobs to the job queue (%s active, %s added)!", self.active_jobs, self.active_jobs-old)

			if self.run_flag.value != 1:
				return

			with self.limiter_lock:
				new_j_l =self.ratelimiter.get_available_jobs()

			for rid, joburl, netloc in new_j_l:
				self.put_outbound_job(rid, joburl, netloc)

			# If there weren't any new items, stop looping because we're not going anywhere.
			if num_new == 0:
				break

			escape_count += 1

	def open_rpc_interface(self):
		try:
			self.local.rpc_interface.close()
		except Exception:   # pylint: disable=W0703
			pass

		for x in range(100):
			try:
				self.local.rpc_interface = common.get_rpyc.RemoteJobInterface("RawMirror")
				return

			except (TypeError, KeyError, socket.timeout, ConnectionRefusedError):
				for line in traceback.format_exc().split("\n"):
					self.log.error(line)
				if x > 90:
					raise RuntimeError("Could not establish connection to RPC remote!")

		raise RuntimeError("Could not establish connection to RPC remote!")

	def process_responses(self):
		while 1:

			# Something in the RPC stuff is resulting in a typeerror I don't quite
			# understand the source of. anyways, if that happens, just reset the RPC interface.
			try:
				tmp = self.local.rpc_interface.get_job()

				with self.count_lock:
					# print("Handling response!")
					self.active_jobs -= 1
					self.jobs_in += 1
					if self.active_jobs < 0:
						self.active_jobs = 0

			except queue.Empty:
				return

			except TypeError:
				self.open_rpc_interface()
				return
			except KeyError:
				self.open_rpc_interface()
				return
			except socket.timeout:
				self.open_rpc_interface()
				return
			except ConnectionRefusedError:
				self.open_rpc_interface()
				return
			except OSError:
				self.open_rpc_interface()
				return

			if tmp:

				nl = None
				if 'extradat' in tmp and 'netloc' in tmp['extradat']:
					nl = tmp['extradat']['netloc']

				if nl:
					with self.limiter_lock:
						if 'success' in tmp and tmp['success']:
							self.ratelimiter.netloc_ok(nl)
						else:
							print("Success val: ", 'success' in tmp, list(tmp.keys()))
							self.ratelimiter.netloc_error(nl)
				else:
					self.log.warning("Missing netloc in response extradat!")

				with self.count_lock:
					self.log.info("Job response received. Jobs in-flight: %s (qsize: %s)", self.active_jobs, self.normal_out_queue.qsize())

				self.last_rx = datetime.datetime.now()
				self.blocking_put_response(("processed", tmp))
			else:
				self.print_mod += 1
				if self.print_mod > 20:
					self.log.info("No job responses available.")
					self.print_mod = 0
				time.sleep(1)
				break

	def blocking_put_response(self, item):
		while self.run_flag.value == 1:
			try:
				self.normal_out_queue.put_nowait(item)
				return
			except queue.Full:
				self.log.warning("Response queue full (%s items). Sleeping", self.normal_out_queue.qsize())
				time.sleep(1)

	def queue_filler_proc(self, mode):

		common.process.name_process("raw job filler worker")
		self.open_rpc_interface()

		try:
			signal.signal(signal.SIGINT, signal.SIG_IGN)
		except ValueError:
			self.log.warning("Cannot configure job fetcher task to ignore SIGINT. May be an issue.")

		self.log.info("Job queue fetcher starting.")

		msg_loop = 0
		retries = 0
		while self.run_flag.value == 1:
			try:
				self.local.db_interface = psycopg2.connect(
						database = settings.DATABASE_DB_NAME,
						user     = settings.DATABASE_USER,
						password = settings.DATABASE_PASS,
						host     = settings.DATABASE_IP,
					)

				while self.run_flag.value == 1:
					self.fill_jobs(mode)

					msg_loop += 1
					time.sleep(0.2)
					if msg_loop > 25:

						with self.count_lock:
							self.log.info("Job queue filler process (%s). In-Flight: %s, waiting: %s (out: %s, in: %s). Runstate: %s",
								mode,
								self.active_jobs,
								self.normal_out_queue.qsize(),
								self.jobs_out,
								self.jobs_in,
								self.run_flag.value==1)
						retries  = 0
						msg_loop = 0
			except psycopg2.Error:
				self.log.error("Exception in psycopg2 in filler process!")
				for line in traceback.format_exc().split("\n"):
					self.log.error(line)
				retries += 1
				if retries > 5:
					raise


		self.log.info("Job queue fetcher saw exit flag. Halting.")
		self.local.rpc_interface.close()

		# Consume the remaining items in the output queue so it shuts down cleanly.
		try:
			while 1:
				self.normal_out_queue.get_nowait()
		except queue.Empty:
			pass

		with self.count_lock:
			self.log.info("Job queue filler process. Current job queue size: %s. ", self.active_jobs)
		self.log.info("Job queue fetcher halted.")


	def queue_drainer_proc(self):

		common.process.name_process("raw job filler worker")
		self.open_rpc_interface()

		try:
			signal.signal(signal.SIGINT, signal.SIG_IGN)
		except ValueError:
			self.log.warning("Cannot configure job fetcher task to ignore SIGINT. May be an issue.")

		self.log.info("Job queue fetcher starting.")

		msg_loop = 0
		while self.run_flag.value == 1:
			# print("Drainer looping@")
			self.process_responses()

			msg_loop += 1
			time.sleep(0.2)
			if msg_loop > 25:

				with self.count_lock:
					self.log.info("Job queue filler process. Current job queue size: %s (out: %s, in: %s). Runstate: %s", self.active_jobs, self.jobs_out, self.jobs_in, self.run_flag.value==1)
				msg_loop = 0
				with self.limiter_lock:
					self.ratelimiter.job_reduce()


		self.log.info("Job queue fetcher saw exit flag. Halting.")
		self.local.rpc_interface.close()

		# Consume the remaining items in the output queue so it shuts down cleanly.
		try:
			while 1:
				self.normal_out_queue.get_nowait()
		except queue.Empty:
			pass

		with self.count_lock:
			self.log.info("Job queue filler process. Current job queue size: %s. ", self.active_jobs)
		self.log.info("Job queue fetcher halted.")

	def _get_task_internal(self, mode):

		cursor = self.local.db_interface.cursor()

		# Hand-tuned query, I couldn't figure out how to
		# get sqlalchemy to emit /exactly/ what I wanted.
		# TINY changes will break the query optimizer, and
		# the 10 ms query will suddenly take 10 seconds!
		if mode == 'priority':
			raw_query = '''
					UPDATE
					    raw_web_pages
					SET
					    state = 'fetching'
					WHERE
					    raw_web_pages.id IN (
					        SELECT
					            raw_web_pages.id
					        FROM
					            raw_web_pages
					        WHERE
					            raw_web_pages.state = 'new'
					        AND
					            raw_web_pages.priority <= (
					               SELECT
					                    min(priority)
					                FROM
					                    raw_web_pages
					                WHERE
					                    state = 'new'::dlstate_enum
					            ) + 1
					        LIMIT {in_flight}
					    )
					AND
					    raw_web_pages.state = 'new'
					RETURNING
					    raw_web_pages.id, raw_web_pages.netloc, raw_web_pages.url;
				'''.format(in_flight=min((MAX_IN_FLIGHT_JOBS, 150)))

		elif mode == 'new_fetch':
			raw_query = '''
					UPDATE
					    raw_web_pages
					SET
					    state = 'fetching'
					WHERE
					    raw_web_pages.id IN (
					        SELECT
					            raw_web_pages.id
					        FROM
					            raw_web_pages
					        WHERE
					            raw_web_pages.state = 'new'
					        AND
					            raw_web_pages.fspath IS NULL
					        LIMIT {in_flight}
					    )
					AND
					    raw_web_pages.state = 'new'
					RETURNING
					    raw_web_pages.id, raw_web_pages.netloc, raw_web_pages.url;
				'''.format(in_flight=min((MAX_IN_FLIGHT_JOBS, 150)))

		elif mode == 'random':
			raw_query = '''
					UPDATE
					    raw_web_pages
					SET
					    state = 'fetching'
					WHERE
					    raw_web_pages.id IN (
					        SELECT
					            raw_web_pages.id
					        FROM
					            raw_web_pages
					        WHERE
					            raw_web_pages.state = 'new'
					        LIMIT {in_flight}
					    )
					AND
					    raw_web_pages.state = 'new'
					RETURNING
					    raw_web_pages.id, raw_web_pages.netloc, raw_web_pages.url;
				'''.format(in_flight=min((MAX_IN_FLIGHT_JOBS, 150)))
		else:
			self.log.error("Unknown dispatch mode: '%s'" % mode)
			return


		start = time.time()

		while self.run_flag.value == 1:
			try:
				cursor.execute("""SET statement_timeout TO 900000;""")
				cursor.execute(raw_query)
				rids = cursor.fetchall()
				self.local.db_interface.commit()
				break
			except psycopg2.Error:
				delay = random.random() / 3
				# traceback.print_exc()
				self.log.warn("Error getting job (psycopg2.Error)! Delaying %s.", delay)
				time.sleep(delay)
				self.local.db_interface.rollback()

		if self.run_flag.value != 1:
			return 0

		if not rids:
			return 0

		rids = list(rids)
		# If we broke because a user-interrupt, we may not have a
		# valid rids at this point.
		if self.run_flag.value != 1:
			return 0

		xqtim = time.time() - start

		if not rids:
			self.log.warning("No jobs available! Sleeping for 5 seconds waiting for new jobs to become available!")
			for dummy_x in range(5):
				if self.run_flag.value == 1:
					time.sleep(1)
			return 0

		if xqtim > 0.5:
			self.log.error("Query execution time: %s ms. Fetched job IDs = %s", xqtim * 1000, len(rids))
		elif xqtim > 0.1:
			self.log.warn("Query execution time: %s ms. Fetched job IDs = %s", xqtim * 1000, len(rids))
		else:
			self.log.info("Query execution time: %s ms. Fetched job IDs = %s", xqtim * 1000, len(rids))

		dispatched = 0
		for rid, netloc, joburl in rids:
			try:

				# If we don't have a thread affinity, do distributed fetch.
				# If we /do/ have a thread affinity, fetch locally.

				if not self.outbound_job_wanted(netloc, joburl):
					self.delete_job(rid, joburl)
					continue

				if self.outbound_job_disabled(netloc, joburl):
					self.disable_job(rid, joburl)
					continue

				dispatched += 1

				threadn = RawArchiver.misc.thread_affinity(joburl, 1)
				if threadn is True:
					with self.limiter_lock:
						self.ratelimiter.put_job(rid, joburl, netloc)
					# self.put_outbound_job(rid, joburl, netloc=netloc)
				else:
					self.blocking_put_response(("unfetched", rid))

			except RawArchiver.misc.UnwantedUrlError:
				self.log.warning("Unwanted url in database? Url: '%s'", joburl)
				self.log.warning("Deleting entry.")
				cursor.execute("""DELETE FROM raw_web_pages WHERE url = %s AND id = %s;""", (joburl, rid))
				self.local.db_interface.commit()


		cursor.execute("""RESET statement_timeout;""")
		cursor.close()

		return dispatched

	def delete_job(self, rid, joburl):
		self.log.warning("Deleting job for url: '%s'", joburl)
		cursor = self.local.db_interface.cursor()
		cursor.execute("""DELETE FROM raw_web_pages WHERE raw_web_pages.id = %s AND raw_web_pages.url = %s;""", (rid, joburl))
		self.local.db_interface.commit()


	def disable_job(self, rid, joburl):
		self.log.warning("Disabling job for url: '%s'", joburl)
		cursor = self.local.db_interface.cursor()
		cursor.execute("""UPDATE raw_web_pages SET state = %s WHERE raw_web_pages.id = %s AND raw_web_pages.url = %s;""", ('disabled', rid, joburl))
		self.local.db_interface.commit()

	def get_status(self):
		if any([tmp.is_alive() for tmp in self.fetch_procs.values()]):

			with self.count_lock:
				return "Worker: %s, alive: %s, control: %s, last_rx: %s, active_jobs: %s, jobs_out: %s, jobs_in: %s." % (
						[tmp.ident for tmp in self.fetch_procs.values()],
						[tmp.is_alive() for tmp in self.fetch_procs.values()],
						self.run_flag.value,
						self.last_rx,
						self.active_jobs,
						self.jobs_out,
						self.jobs_in,
					)



		return "Worker is none! Error!"

def test2():
	import logSetup
	import pprint
	logSetup.initLogging()

	agg = RawJobAggregator()
	outq = agg.get_queues()
	for x in range(20):
		print("Sleeping, ", x)
		time.sleep(1)
		try:
			j = outq.get_nowait()
			print("Received job! %s", len(j))
			with open("jobs.txt", "a") as fp:
				fp.write("\n\n\n")
				fp.write(pprint.pformat(j))
			print(j)
		except queue.Empty:
			pass
	print("Joining on the aggregator")
	agg.join_proc()
	print("Joined.")

if __name__ == "__main__":
	test2()


