

import logging
import threading
import queue
import sys
import pickle
import sys
import queue
import os
import signal
from gevent.server import StreamServer
import FetchAgent.MessageProcessor
import traceback
import logSetup
import mprpc
import gevent.monkey
import gevent

# from graphitesend import graphitesend
import statsd

import settings
import time

# import rpyc
# rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True
# from rpyc.utils.server import ThreadPoolServer





INTERRUPTS = 0

TO_EXIT = []


def build_mprpc_handler(server):
	global TO_EXIT
	TO_EXIT.append(server)

	def handler(signum=-1, frame=None):
		global INTERRUPTS
		INTERRUPTS += 1
		print('Signal handler called with signal %s for the %s time' % (signum, INTERRUPTS))
		if INTERRUPTS > 2:
			print("Raising due to repeat interrupts")
			raise KeyboardInterrupt
		for server in TO_EXIT:
			server.close()
	return handler

def base_abort():
	print("Low level keyboard interrupt")
	for server in TO_EXIT:
		server.close()


class FetchInterfaceClass(mprpc.RPCServer):


	def __init__(self, interface_dict, rpc_prefix):

		mp_conf = {"use_bin_type":True}
		super().__init__(
				pack_params  = {
						"use_bin_type":True
					},
				# unpack_param = {
				# 		'raw'             : True,
				# 		'max_buffer_size' : sys.maxint,
				# 		'max_str_len'     : sys.maxint,
				# 		'max_bin_len'     : sys.maxint,
				# 		'max_array_len'   : sys.maxint,
				# 		'max_map_len'     : sys.maxint,
				# 		'max_ext_len'     : sys.maxint,
				# 	},
			)

		self.log = logging.getLogger("Main.{}-Interface".format(rpc_prefix))
		self.mdict = interface_dict
		self.log.info("Connection")



	def __check_have_queue(self, out_basename, in_basename, queuename):
		if not queuename in self.mdict['outq']:
			with self.mdict['qlock']:
				self.mdict[out_basename][queuename] = queue.Queue()
				self.mdict[in_basename][queuename] = queue.Queue()

	def __check_rss_queue(self, queuename):
		if not queuename in self.mdict['feed_outq']:
			with self.mdict['qlock']:
				self.mdict['feed_outq'][queuename] = queue.Queue()
				self.mdict['feed_inq'][queuename] = queue.Queue()

	#########################################################################################################################

	def _putJob(self, out_basename, in_basename, queuename, job):
		self.__check_have_queue(out_basename, in_basename, queuename)
		self.log.info("Putting job item in  queue (%s->%s) with size: %s (Queue size: %s)!", out_basename, queuename, len(job), self.mdict[out_basename][queuename].qsize())
		self.mdict[out_basename][queuename].put(job)

	def _getJob(self, out_basename, in_basename, queuename):
		self.__check_have_queue(out_basename, in_basename, queuename)
		self.log.info("Get job call for '%s' -> '%s' -> %s", in_basename, queuename, self.mdict[in_basename][queuename].qsize())
		try:
			tmp = self.mdict[in_basename][queuename].get_nowait()
			return tmp
		except queue.Empty:
			return None

	def _getJobNoWait(self, out_basename, in_basename, queuename):
		self.__check_have_queue(out_basename, in_basename, queuename)
		self.log.info("Get job call for '%s' -> '%s' -> %s", in_basename, queuename, self.mdict[in_basename][queuename].qsize())
		try:
			return self.mdict[in_basename][queuename].get_nowait()
		except queue.Empty:
			return None


	#########################################################################################################################
	# Wrapper stubs with queue names
	#########################################################################################################################

	def putJob(self, queuename, job):
		self._putJob('outq', 'inq', queuename, job)

	def getJob(self, queuename):
		return self._getJob('outq', 'inq', queuename)

	def getJobNoWait(self, queuename):
		return self._getJobNoWait('outq', 'inq', queuename)

	#########################################################################################################################

	def putIndependentJob(self, queuename, job):
		self._putJob('independent_outq', 'independent_inq', queuename, job)

	def getIndependentJob(self, queuename):
		return self._getJob('independent_outq', 'independent_inq', queuename)

	def getIndependentJobNoWait(self, queuename):
		return self._getJobNoWait('independent_outq', 'independent_inq', queuename)

	#########################################################################################################################

	def putLowrateJob(self, queuename, job):
		self._putJob('lowrate_outq', 'lowrate_inq', queuename, job)

	def getLowrateJob(self, queuename):
		return self._getJob('lowrate_outq', 'lowrate_inq', queuename)

	def getLowrateJobNoWait(self, queuename):
		return self._getJobNoWait('lowrate_outq', 'lowrate_inq', queuename)

	#########################################################################################################################

	def putRss(self, message):
		feed_q_name = 'rss_queue'
		self.__check_rss_queue(feed_q_name)
		self.log.info("Putting rss item with size: %s (qsize: %s)!", len(message), self.mdict['feed_outq'][feed_q_name].qsize())
		self.mdict['feed_outq'][feed_q_name].put(message)

	def putManyRss(self, messages):
		feed_q_name = 'rss_queue'
		self.__check_rss_queue(feed_q_name)
		for message in messages:
			self.log.info("Putting rss item with size: %s!", len(message))
			self.mdict['feed_outq'][feed_q_name].put(message)

	def getRss(self):
		feed_q_name = 'rss_queue'
		self.__check_rss_queue(feed_q_name)
		self.log.info("Get job call for rss queue -> %s", self.mdict['feed_inq'][feed_q_name].qsize())
		try:
			ret = self.mdict['feed_inq'][feed_q_name].get_nowait()
			return ret
		except queue.Empty:
			return None

	def checkOk(self):
		"""
		Check the connection is OK, and we can pass binary data
		"""
		return (True, b'wattt\0')


sock_path = '/tmp/rwp-fetchagent-sock'




def run_rpc(interface_dict):
	print("MpRPC server Started.")
	server_instance = FetchInterfaceClass(interface_dict, "MpRPC")
	mprpc_server = StreamServer(('0.0.0.0', 4315), server_instance)

	gevent.signal(signal.SIGINT, build_mprpc_handler(mprpc_server))
	mprpc_server.serve_forever()


def initialize_manager(interface_dict):

	# interface_dict.qlock = pickle.dumps(mgr.Lock())
	interface_dict['qlock'] = threading.Lock()

	print("Manager lock: ", interface_dict['qlock'])
	interface_dict['outq'] = {}
	interface_dict['inq'] = {}

	interface_dict['feed_outq'] = {}
	interface_dict['feed_inq'] = {}

	interface_dict['independent_outq'] = {}
	interface_dict['independent_inq'] = {}


def run():

	interface_dict = {}

	logSetup.initLogging()

	# Make sure the socket does not already exist
	try:
		os.unlink(sock_path)
	except OSError:
		if os.path.exists(sock_path):
			raise

	initialize_manager(interface_dict)
	amqp_interface = FetchAgent.MessageProcessor.MessageProcessor(interface_dict)

	print("AMQP Interfaces have started. Launching RPC threads.")

	t2 = threading.Thread(target=run_rpc, args=(interface_dict, ))

	t2.start()

	try:
		while INTERRUPTS == 0:
			amqp_interface.run()
			time.sleep(0.1)
	except AssertionError:
		print("Main worker encountered assertion failure!")
		traceback.print_exc()
		base_abort()
	except KeyboardInterrupt:
		print("Main worker abort")
		base_abort()

	except Exception:
		print("Wat?")
		traceback.print_exc()
		with open("Manager error %s.txt" % time.time(), "w") as fp:
			fp.write("Manager crashed?\n")
			fp.write(traceback.format_exc())


	print("Joining on worker threads")
	t2.join(timeout=60)

	print("Terminating AMQP interface.")
	amqp_interface.terminate()


def main():
	print("Preloading cache directories")

	# print("Testing reload")
	# server.tree.tree.reloadTree()
	# print("Starting RPC server")
	try:
		run()

	except:
		# abort /hard/ if we exceptioned out of the main run.
		# This should (hopeully) cause the OS to terminate any
		# remaining threads.
		# As it is, I've been having issues with the main thread failing
		# with 'OSError: [Errno 24] Too many open files', killing the main thread
		# and leaving some of the amqp interface threads dangling.
		# Somehow, it's not being caught in the `except Exception:` handler
		# in run(). NFI how.
		import ctypes
		ctypes.string_at(0)


if __name__ == '__main__':
	main()
