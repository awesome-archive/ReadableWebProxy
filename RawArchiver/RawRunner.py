
import time
import os
import multiprocessing
import signal
import logging
import logSetup
import cProfile
import traceback
import threading
import sys
import queue

# from pympler.tracker import SummaryTracker, summary, muppy
# import tracemalloc


if __name__ == "__main__":
	logSetup.initLogging()

import runStatus

import common.util.urlFuncs as urlFuncs
import RawArchiver.RawEngine
import RawArchiver.RawJobDispatcher as njq


import common.stuck
import common.database
import common.process


import RawArchiver.RawActiveModules


class RawRunInstance(object):
	def __init__(self, num, total_worker_count, worker_num, response_queue, new_job_queue, cookie_lock, nosig=True):
		# print("RawRunInstance %s init!" % num)
		if nosig:
			# signal.signal(signal.SIGINT, handler)
			signal.signal(signal.SIGINT, signal.SIG_IGN)
		self.num = num
		self.log = logging.getLogger("Main.Text.Web")
		self.resp_queue         = response_queue
		self.cookie_lock        = cookie_lock
		self.new_job_queue      = new_job_queue
		self.total_worker_count = total_worker_count
		self.worker_num         = worker_num

		# print("RawRunInstance %s MOAR init!" % num)

	def __del__(self):
		common.database.delete_db_session()

	def do_task(self):


		hadjob = False
		archiver = RawArchiver.RawEngine.RawSiteArchiver(
				total_worker_count = self.total_worker_count,
				worker_num         = self.worker_num,
				cookie_lock        = self.cookie_lock,
				new_job_queue      = self.new_job_queue,
				response_queue     = self.resp_queue,
			)
		hadjob = archiver.taskProcess()


		return hadjob

	def go(self):

		self.log.info("RawRunInstance starting!")
		loop = 0
		# We have to only let the child threads run for a period of time, or something
		# somewhere in sqlalchemy appears to be leaking memory.
		for dummy_x in range(250):

			if runStatus.run_state.value == 1:
				# objgraph.show_growth(limit=3)
				hadjob = self.do_task()
			else:
				self.log.info("Thread %s exiting.", self.num)
				break
			loop += 1

			# If there was nothing to do, sleep 30 seconds and recheck.
			# This is because with 50 workers with a sleep-time of 5 seconds on job-miss,
			# it was causing 100% CPU usage on the DB just for the getjob queries. (I think)
			if not hadjob:
				sleeptime = 10
				self.log.info("Nothing for thread %s to do. Sleeping %s seconds.", self.num, sleeptime)
				for _x in range(sleeptime):
					time.sleep(1)
					if runStatus.run_state.value != 1:
						self.log.info("Thread %s saw exit flag while waiting for jobs. Runstate: %s", self.num, runStatus.run_state.value)
						return

		if runStatus.run_state.value:
			self.log.info("Thread %s restarting. Runstate: %s", self.num, runStatus.run_state.value)
		else:
			self.log.info("Thread %s halting. Runstate: %s", self.num, runStatus.run_state.value)




	@classmethod
	def run_prof(cls, num, total_worker_count, worker_num, response_queue, new_job_queue, cookie_lock, nosig=True):

		logSetup.resetLoggingLocks()
		common.process.name_process("raw fetcher processing worker w-profiling")

		pid = os.getpid()
		try:
			cProfile.runctx('cls.run(num, response_queue, new_job_queue, cookie_lock, nosig)', globals(), locals(), 'prof%d.prof' % pid)
		except Exception as e:
			print("Wat?")
			print("Wat?")
			print("Wat?")
			print("Wat?")
			print("Wat?")
			print("Wat?")
			print("Wat?")
			traceback.print_exc()
			raise e

	@classmethod
	def run(cls, num, total_worker_count, worker_num, response_queue, new_job_queue, cookie_lock, nosig=True):
		logSetup.resetLoggingLocks()
		common.process.name_process("raw fetcher processing worker")

		try:
			run = cls(num, total_worker_count, worker_num, response_queue, new_job_queue, cookie_lock, nosig)
			# print("Class instantiated: ", run)
			run.go()
		except Exception:
			print()
			print("Exception in sub-process!")
			traceback.print_exc()


if __name__ == "__main__":
	runner = Crawler()
	runner.run()
	print(runner)

