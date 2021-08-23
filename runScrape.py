#!flask/bin/python

if __name__ == "__main__":
	import logSetup
	import logging
	logSetup.initLogging()
	# logSetup.initLogging(logging.WARNING)

	# Shut up fucking annoying psycopg2 vomit every exec.
	import warnings
	from sqlalchemy import exc as sa_exc
	warnings.filterwarnings("ignore", category=UserWarning, module='psycopg2')
	warnings.simplefilter("ignore", category=sa_exc.SAWarning)


# This HAS to be included before the app, to prevent circular dependencies.
# import WebMirror.runtime_engines


import settings
import multiprocessing
import time
import json
import common.RunManager
import WebMirror.rules
import WebMirror.Runner
import WebMirror.UrlUpserter
import RawArchiver.RawRunner
import RawArchiver.RawUrlUpserter
import common.stuck
import common.process
import psutil
import Misc.ls_open_file_handles

import common.redis
import common.management.WebMirrorManage

from settings import NO_PROCESSES
from settings import RAW_NO_PROCESSES
from settings import MAX_DB_SESSIONS

import common.LogBase as LogBase
import common.StatsdMixin as StatsdMixin

class MemoryTracker(LogBase.LoggerMixin, StatsdMixin.InfluxDBMixin):

	loggerPath                = "Main.MemStats"
	influxdb_type             = "memory_stats"
	influxdb_measurement_name = "server_ram_free"

	def save_mem_stats(self):
		v = psutil.virtual_memory()

		params = {
			'mem_total'     : v.total,
			'mem_available' : v.available,
			'mem_percent'   : v.percent,
			'mem_used'      : v.used,
			'mem_free'      : v.free,
			'mem_active'    : v.active,
			'mem_inactive'  : v.inactive,
			'mem_buffers'   : v.buffers,
			'mem_cached'    : v.cached,
			'mem_shared'    : v.shared,
			'mem_slab'      : v.slab,
		}

		self.log.info("Memory stats: %s", params)

		points = [
			{
					'measurement' : self.influxdb_measurement_name,
					"tags": {
							'type' : self.influxdb_type,
						},
					'time' : int(time.time() * 1e9),
					'fields' : params
				}
			]

		self.influx_client.write_points(points)



def go(args):

	largv = [tmp.lower() for tmp in args]

	common.redis.config_redis()
	rules = WebMirror.rules.load_rules()

	lowrate = "lowrate" in largv

	runner = common.RunManager.Crawler(
		main_thread_count = NO_PROCESSES,
		raw_thread_count  = RAW_NO_PROCESSES,
		lowrate           = lowrate,
		)

	if "raw" in largv:
		common.process.name_process("raw fetcher management thread")
		print("RAW Scrape!")
		RawArchiver.RawUrlUpserter.check_init_func()

		if not "noreset" in largv:
			print("Resetting any in-progress downloads.")
			RawArchiver.RawUrlUpserter.resetRawInProgress()
		else:
			print("Not resetting in-progress downloads.")

		RawArchiver.RawUrlUpserter.initializeRawStartUrls()
		runner.run_raw()
	else:

		common.process.name_process("fetcher management thread")



		if "noreset" not in largv and not lowrate:
			print("Resetting any in-progress downloads.")
			WebMirror.UrlUpserter.resetInProgress()
			WebMirror.UrlUpserter.resetRedisQueues()
		else:
			print("Not resetting in-progress downloads.")

		#if not "noreset" in largv:
		#	print("Dropping fetch priority levels.")
		#	common.management.WebMirrorManage.exposed_drop_priorities()

		#else:
		#	print("Not resetting fetch priority levels.")


		WebMirror.UrlUpserter.initializeStartUrls(rules)


		runner.run()
		print("Main runner returned!")


	# print("Thread halted. App exiting.")

def dump_active_items():

	print("Dumping active URLs")
	active = {
		'fetching'   : [tmp.decode("utf-8") for tmp in common.redis.get_fetching_urls()],
		'processing' : [tmp.decode("utf-8") for tmp in common.redis.get_processing_urls()],
	}

	with open("active_jobs_at_start_%s.json" % time.time(), "w") as fp:
		json.dump(active, fp, sort_keys=True, indent=4)

	common.redis.clear_fetching_urls()
	common.redis.clear_processing_urls()

def run_in_subprocess():
	if 'raw' not in sys.argv:
		dump_active_items()

	# mon = MemoryTracker()
	proc = multiprocessing.Process(target=go, args=(sys.argv, ))
	proc.start()
	while proc.is_alive():
		time.sleep(4)
		# mon.save_mem_stats()
		# print("Base Subprocessor Runner: %s, %s" % (proc.is_alive(), proc.pid))

	print("Main runner has gone away. Committing Suicide")

	# If the subprocess has gone away, die hard.
	import ctypes
	ctypes.string_at(1)
	import os
	os.kill(0,4)

if __name__ == "__main__":
	import sys

	largv = [tmp.lower() for tmp in sys.argv]

	if "scheduler" in sys.argv:
		print("Please use runScheduler.py instead!")
		sys.exit(1)
	else:

		started = False
		if not started:
			started = True
			run_in_subprocess()
