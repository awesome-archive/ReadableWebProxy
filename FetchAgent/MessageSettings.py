
import ssl
import os.path
import settings as settings_file


def getSslOpts():
	'''
	Verify the SSL cert exists in the proper place.
	'''
	certpath = './rabbit_pub_cert/'

	caCert = os.path.abspath(os.path.join(certpath, './cacert.pem'))
	cert = os.path.abspath(os.path.join(certpath, './cert1.pem'))
	keyf = os.path.abspath(os.path.join(certpath, './key1.pem'))

	assert os.path.exists(caCert), "No certificates found on path '%s'" % caCert
	assert os.path.exists(cert), "No certificates found on path '%s'" % cert
	assert os.path.exists(keyf), "No certificates found on path '%s'" % keyf

	ret = {"cert_reqs" : ssl.CERT_REQUIRED,
			"ca_certs" : caCert,
			"keyfile"  : keyf,
			"certfile"  : cert,
		}

	return ret


RPC_AMQP_SETTINGS = {
		'worker_threads'                         : 6,

		'userid'                                 : settings_file.RPC_RABBIT_LOGIN,
		'password'                               : settings_file.RPC_RABBIT_PASWD,
		'host'                                   : settings_file.RPC_RABBIT_SRVER,
		'virtual_host'                           : settings_file.RPC_RABBIT_VHOST,
		'sslopts'                                : getSslOpts(),
		'master'                                 : True,
		'prefetch'                               : 25,
		# 'prefetch'                             : 5,
		'task_exchange_type'                     : 'direct',
		'response_exchange_type'                 : 'direct',

		'task_queue_name'                        : 'task.q',
		'response_queue_name'                    : 'response.q',

		'heartbeat'                              :  45,
		'socket_timeout'                         :  90,

		'taskq_name'                             : 'outq',
		'respq_name'                             : 'inq',

		'task_exchange'                          : 'tasks.e',
		'response_exchange'                      : 'resps.e',
		'response_exchange_routing'              : 'resps',

	}

LOWRATE_RPC_AMQP_SETTINGS = {
		'worker_threads'                         : 2,

		'userid'                                 : settings_file.RPC_RABBIT_LOGIN,
		'password'                               : settings_file.RPC_RABBIT_PASWD,
		'host'                                   : settings_file.RPC_RABBIT_SRVER,
		'virtual_host'                           : settings_file.RPC_RABBIT_VHOST,
		'sslopts'                                : getSslOpts(),
		'master'                                 : True,
		'prefetch'                               : 25,
		# 'prefetch'                             : 5,
		'task_exchange_type'                     : 'direct',
		'response_exchange_type'                 : 'direct',

		'task_queue_name'                        : 'task.q',
		'response_queue_name'                    : 'lowrate_response.q',

		'heartbeat'                              :  45,
		'socket_timeout'                         :  90,

		'taskq_name'                             : 'outq',
		'respq_name'                             : 'inq',

		'task_exchange'                          : 'tasks.e',
		'response_exchange'                      : 'resps.e',

		'response_exchange_routing'              : 'lowrate_resps',
	}


INDEPENDENT_RPC_AMQP_SETTINGS = {
		'worker_threads'                         : 2,

		'userid'                                 : settings_file.RPC_RABBIT_LOGIN,
		'password'                               : settings_file.RPC_RABBIT_PASWD,
		'host'                                   : settings_file.RPC_RABBIT_SRVER,
		'virtual_host'                           : settings_file.RPC_RABBIT_VHOST,
		'sslopts'                                : getSslOpts(),
		'master'                                 : True,
		'prefetch'                               : 25,
		# 'prefetch'                             : 5,
		'task_exchange_type'                     : 'direct',
		'response_exchange_type'                 : 'direct',

		'task_queue_name'                        : 'independent_task.q',
		'response_queue_name'                    : 'independent_response.q',

		'heartbeat'                              :  45,
		'socket_timeout'                         :  90,

		'taskq_name'                             : 'independent_task',
		'respq_name'                             : 'independent_response',

		'task_exchange'                          : 'independent_tasks.e',
		'response_exchange'                      : 'independent_resps.e',

		'response_exchange_routing'              : 'independent_resps',
	}


FEED_AMQP_SETTINGS = {
		'worker_threads'                         : 3,

		'userid'                                 : settings_file.RABBIT_LOGIN,
		'password'                               : settings_file.RABBIT_PASWD,
		'host'                                   : settings_file.RABBIT_SRVER,
		'virtual_host'                           : settings_file.RABBIT_VHOST,
		'sslopts'                                : getSslOpts(),
		'master'                                 : True,
		'prefetch'                               : 25,
		# 'prefetch'                             : 5,
		'task_exchange_type'                     : 'fanout',
		'task_queue_name'                        : 'task.q',
		'response_queue_name'                    : 'response.q',
		'response_exchange_type'                 : 'direct',

		'heartbeat'                              :  45,
		'socket_timeout'                         :  90,

		'taskq_name'                             : 'feed_outq',
		'respq_name'                             : 'feed_inq',

		'task_exchange'                          : 'tasks.e',
		'response_exchange'                      : 'resps.e',

	}
