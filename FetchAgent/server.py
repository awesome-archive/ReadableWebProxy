

import logging
import threading
import queue
import threading
import pickle
import sys
import queue
import os
import signal
from gevent.server import StreamServer
import FetchAgent.AmqpInterface
import logSetup
import zerorpc
import mprpc
import gevent.monkey
import gevent
import multiprocessing

# from graphitesend import graphitesend
import statsd

import settings
import time

# import rpyc
# rpyc.core.protocol.DEFAULT_CONFIG['allow_pickle'] = True
# from rpyc.utils.server import ThreadPoolServer


INTERRUPTS_1 = 0
INTERRUPTS_2 = 0

TO_EXIT = []

def build_zerorpc_handler(server):
	global TO_EXIT
	TO_EXIT.append(server)

	def handler(signum=-1, frame=None):
		global INTERRUPTS_1
		INTERRUPTS_1 += 1
		print('Signal handler called with signal %s for the %s time' % (signum, INTERRUPTS_1))
		if INTERRUPTS_1 > 2:
			print("Raising due to repeat interrupts")
			raise KeyboardInterrupt
		for server in TO_EXIT:
			server.close()
		# server.stop()
	return handler

def build_mprpc_handler(server):
	global TO_EXIT
	TO_EXIT.append(server)

	def handler(signum=-1, frame=None):
		global INTERRUPTS_2
		INTERRUPTS_2 += 1
		print('Signal handler called with signal %s for the %s time' % (signum, INTERRUPTS_2))
		if INTERRUPTS_2 > 2:
			print("Raising due to repeat interrupts")
			raise KeyboardInterrupt
		for server in TO_EXIT:
			server.close()
	return handler

def base_abort():
	print("Low level keyboard interrupt")
	for server in TO_EXIT:
		server.close()


# import gevent.socket as gsocket
# import socket
# from bsonrpc import BSONRpc, ThreadingModel
# from bsonrpc import rpc_request, request, service_class
# from common.fixed_bsonrpc import Fixed_BSONRpc


class FetchInterfaceClass(mprpc.RPCServer):


	def __init__(self, interface_dict, interface_lock, rpc_prefix):

		super().__init__()

		self.log = logging.getLogger("Main.{}-Interface".format(rpc_prefix))
		self.mdict = interface_dict
		self.mlock = interface_lock
		self.log.info("Connection")



	def __check_have_queue(self, queuename):
		print("Queue:", self.mdict)
		with self.mlock:
			print("Locked")
			if not queuename in self.mdict['outq']:
				print("Setting key in outq to %s" % queuename)
				self.mdict['outq'].setdefault('queuename', [])
			if not queuename in self.mdict['inq']:
				print("Setting key in inq to %s" % queuename)
				self.mdict['inq'].setdefault('queuename', [])

		print(type(self.mdict))
		print("Queue_after:", self.mdict['inq'], self.mdict['outq'])

	def putJob(self, queuename, job):
		self.__check_have_queue(queuename)
		self.log.info("Putting item in queue %s with size: %s (Queue size: %s)!", queuename, len(job), len(self.mdict['outq'][queuename]))
		with self.mlock:
			self.mdict['outq'][queuename].append(job)

	def getJob(self, queuename):
		self.__check_have_queue(queuename)
		self.log.info("Get job call for '%s' -> %s", queuename, len(self.mdict['inq'][queuename]))

		with self.mlock:
			if self.mdict['inq'][queuename]:
				tmp = self.mdict['inq'][queuename].pop()
				return tmp
			else:
				return None

	def getJobNoWait(self, queuename):
		self.__check_have_queue(queuename)
		self.log.info("Get job call for '%s' -> %s", queuename, len(self.mdict['inq'][queuename]))

		with self.mlock:
			if self.mdict['inq'][queuename]:
				tmp = self.mdict['inq'][queuename].pop()
				return tmp
			else:
				return None

	def putRss(self, message):
		self.log.info("Putting rss item with size: %s (qsize: %s)!", len(message), len(self.mdict['feed_outq']))
		with self.mlock:
			self.mdict['feed_outq'].append(message)

	def putManyRss(self, messages):
		for message in messages:
			self.log.info("Putting rss item with size: %s!", len(message))
			with self.mlock:
				self.mdict['feed_outq'].append(message)

	def getRss(self):
		self.log.info("Get job call for rss queue -> %s", len(self.mdict['feed_inq']))

		with self.mlock:
			if self.mdict['feed_inq']:
				tmp = self.mdict['feed_inq'].pop()
				return tmp
			else:
				return None

	def checkOk(self):
		return (True, b'wattt\0')


sock_path = '/tmp/rwp-fetchagent-sock'


def run_zerorpc_server(interface_dict, interface_lock):
	print("ZeroRPC server Started.")
	try:
		with interface_lock:
			interface_dict['t1_state'] = "starting"
		served_class = FetchInterfaceClass(interface_dict, interface_lock, "ZeroRPC")
		server = zerorpc.Server(served_class, heartbeat=30)

		server.bind("ipc://{}".format(sock_path))
		server.bind("tcp://*:4316")

		with interface_lock:
			interface_dict['t1_state'] = "running"
		gevent.signal(signal.SIGINT, build_zerorpc_handler(server))

		server.run()
	except Exception:
		with interface_lock:
			interface_dict['t1_state'] = "aborted"
		raise

	print("ZeroRPC worker thread has exited")


def run_mprpc_server(interface_dict, interface_lock):
	print("MpRPC server Started.")
	try:
		with interface_lock:
			interface_dict['t2_state'] = "starting"
		server_instance = FetchInterfaceClass(interface_dict, interface_lock, "MpRPC")
		mprpc_server = StreamServer(('0.0.0.0', 4315), server_instance)

		gevent.signal(signal.SIGINT, build_mprpc_handler(mprpc_server))

		with interface_lock:
			interface_dict['t2_state'] = "running"
		mprpc_server.serve_forever()

	except Exception:
		with interface_lock:
			interface_dict['t2_state'] = "aborted"
		raise

	print("MpRPC worker thread has exited")

def run_amqp_thread(interface_dict, interface_lock):

	try:
		with interface_lock:
			interface_dict['t3_state'] = "starting"
		FetchAgent.AmqpInterface.startup_interface(interface_dict, interface_lock)

		with interface_lock:
			interface_dict['t3_state'] = "running"
		keep_running = True
		while keep_running:
			with interface_lock:
				keep_running = not interface_dict['threads_exit']
			time.sleep(1)

		print("Terminating AMQP interface.")
		FetchAgent.AmqpInterface.shutdown_interface(interface_dict, interface_lock)
	except Exception:
		with interface_lock:
			interface_dict['t3_state'] = "aborted"
		raise


def initialize_manager():

	# interface_dict.qlock = pickle.dumps(mgr.Lock())
	manager = multiprocessing.Manager()

	interface_dict = manager.dict()

	interface_dict['outq'] = {}
	interface_dict['inq'] = {}

	interface_dict['feed_outq'] = []
	interface_dict['feed_inq'] = []

	interface_dict['t1_state'] = "not started"
	interface_dict['t2_state'] = "not started"
	interface_dict['t3_state'] = "not started"

	interface_dict['threads_exit'] = False

	return interface_dict

def run():



	logSetup.initLogging()

	# Make sure the socket does not already exist
	try:
		os.unlink(sock_path)
	except OSError:
		if os.path.exists(sock_path):
			raise


	interface_lock = multiprocessing.Lock()
	interface_dict = initialize_manager()

	print("System ready. Creating worker threads.")

	# t1 = threading.Thread(target=run_zerorpc_server,      args=(interface_dict, ))
	# t2 = threading.Thread(target=run_mprpc_server,       args=(interface_dict, ))
	# t3 = threading.Thread(target=run_amqp_thread, args=(interface_dict, ))

	t1 = multiprocessing.Process(target=run_zerorpc_server, args=(interface_dict, interface_lock))
	t2 = multiprocessing.Process(target=run_mprpc_server,   args=(interface_dict, interface_lock))
	t3 = multiprocessing.Process(target=run_amqp_thread,    args=(interface_dict, interface_lock))

	t1.daemon = True
	t2.daemon = True
	t3.daemon = True

	print("Starting threads")
	t1.start()
	t2.start()
	t3.start()

	print("blocking while threads initialize")
	try:
		not_started = True
		while not_started:
			with interface_lock:
				statesd = {
						'zerorpc_thread' : interface_dict['t1_state'],
						'mprpc_thread'   : interface_dict['t2_state'],
						'amqp_thread'    : interface_dict['t3_state'],
					}
			not_started = any([tmp != 'running' for tmp in statesd.values()])
			time.sleep(1)
			print("Waiting for threads to start! Thread states: %s" % statesd)

		print("RPC system active. Entering idle loop.")
		while 1:
			time.sleep(5)

			with interface_lock:
				states = [interface_dict['t1_state'], interface_dict['t2_state'], interface_dict['t3_state']]


			if any([tmp == 'aborted' for tmp in states]):
				print("Worker thread has aborted: %s" % states)
			else:
				print("Worker threads states: %s" % states)

	except KeyboardInterrupt:
		print("Main worker keyboard interrupt")
	except Exception:
		# we often exit without proper cleanup, and things are messy. If so,
		# abort *hard*, so everything restarts properly
		os._exit(1)

	print("Exiting. Telling threads to stop.")
	with interface_lock:
		interface_dict['threads_exit'] = True
	print("Sending exit command to RPC servers")
	base_abort()
	print("Joining on worker threads")

	t1.join(timeout=30)
	t2.join(timeout=30)
	t3.join(timeout=30)

	# Make sure the socket does not already exist
	try:
		os.unlink(sock_path)
	except OSError:
		if os.path.exists(sock_path):
			raise

	# Finally, die hard
	os._exit(0)

def main():
	print("Preloading cache directories")
	run()


if __name__ == '__main__':
	main()
