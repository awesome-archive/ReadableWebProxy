#!flask/bin/python

import sys
import os.path

os.environ['NDSCHEDULER_SETTINGS_MODULE'] = 'settings_sched'
addpath = os.path.abspath("./ndscheduler")
if addpath not in sys.path:
	sys.path.append(os.path.abspath("./ndscheduler"))

import traceback
import datetime
import threading
import time
import apscheduler.triggers.interval
import apscheduler.triggers.cron

# Shut up fucking annoying psycopg2 vomit every exec.
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='psycopg2')


import ndscheduler
import ndscheduler.server.server
import common.stuck
import activeScheduledTasks


class SimpleServer(ndscheduler.server.server.SchedulerServer):

	def post_scheduler_start(self):
		# New user experience! Make sure we have at least 1 job to demo!

		active_jobs = set()
		current_jobs = self.scheduler_manager.get_jobs()

		# import pdb
		# pdb.set_trace()

		start_date = datetime.datetime.now()

		for job in current_jobs:
			job_str, job_id = job.args
			active_jobs.add(job_str)

			# We only actively manage jobs that start with "AUTO". That lets us
			# have manually added jobs that exist outside of the management interface.
			if not job.name.startswith("AUTO: "):
				continue

			if job_str not in activeScheduledTasks.target_jobs:
				print("Removing job: %s -> %s" % (job_str, job_id))
				self.scheduler_manager.remove_job(job_id)

			else:
				job_params = activeScheduledTasks.target_jobs[job_str]
				if job_params.get('interval'):
					trig = apscheduler.triggers.interval.IntervalTrigger(
							seconds    = job_params.get('interval'),
							start_date = start_date,
						)
					start_date = start_date + datetime.timedelta(minutes=5)
				else:
					trig = apscheduler.triggers.cron.CronTrigger(
							month       = job_params.get('month', None),
							day         = job_params.get('day', None),
							day_of_week = job_params.get('day_of_week', None),
							hour        = job_params.get('hour', None),
							minute      = job_params.get('minute', None),
						)

				if job.name != job_params['name']:
					self.scheduler_manager.remove_job(job_id)

				# So the apscheduler CronTrigger class doesn't provide the equality
				# operator, so we compare the stringified version. Gah.
				elif str(job.trigger) != str(trig):
					print("Removing trigger:", str(job.trigger), str(trig))
					self.scheduler_manager.remove_job(job_id)


		start_date = datetime.datetime.now()

		current_jobs = self.scheduler_manager.get_jobs()
		for job_name, params in activeScheduledTasks.target_jobs.items():
			if job_name not in active_jobs:
				assert params['name'].startswith("AUTO: ")
				print("Adding job: %s" % job_name)

				if params.get('interval'):
					trig = apscheduler.triggers.interval.IntervalTrigger(
							seconds    = params.get('interval'),
							start_date = start_date,
						)
					start_date = start_date + datetime.timedelta(minutes=5)
				else:
					trig = apscheduler.triggers.cron.CronTrigger(
							month       = params.get('month', None),
							day         = params.get('day', None),
							day_of_week = params.get('day_of_week', None),
							hour        = params.get('hour', None),
							minute      = params.get('minute', None),
						)

				self.scheduler_manager.add_trigger_job(
						job_class_string = job_name,
						name             = params['name'],
						trigger          = trig,
					)


def run_scheduler():
	common.stuck.install_pystuck()
	SimpleServer.run()


if __name__ == "__main__":
	import logSetup
	logSetup.initLogging()
	run_scheduler()

