

# import WebMirror.OutputFilters.AmqpInterface
import config
import common.get_rpyc
import traceback
import sqlalchemy.exc
import urllib.parse
import datetime
import time
import common.database as db
import WebMirror.UrlUpserter
from WebMirror.processor.ProcessorBase import PageProcessor
import WebMirror.misc

class FilterBase(PageProcessor):

	# Filters don't return anything, so turn off that checking.
	_no_ret = True
	_needs_amqp = True

	def __init__(self, **kwargs):
		super().__init__()

		self._no_ret = True

		self.kwargs = kwargs
		self.db_sess = kwargs['db_sess']



	# Lazy-load the remote interface construction.
	def __getattr__(self, name):
		if name == "rpc_interface" and not name in self.__dict__:
			self.rpc_interface = common.get_rpyc.RemoteJobInterface("FeedUpdater")
			self.rpc_interface.check_ok()
			return self.rpc_interface

		else:
			raise AttributeError("No attribute named '%s'" % name)

	# def __del__(self):
	# 	if "rpc_interface" in self.__dict__:
	# 		self.rpc_interface.close()


	def _put_page_links(self, links, priority):
		if not 'job' in self.kwargs:
			self.log.warning("Cannot upsert URL due to no job passed to filters!")
			return

		links_out = []

		for link in links:
			start = urllib.parse.urlsplit(link).netloc

			assert link.startswith("http")
			assert start
			new = {
				'url'               : link,
				'starturl'          : self.kwargs['job'].starturl,
				'netloc'            : start,
				'distance'          : self.kwargs['job'].distance+1,
				'is_text'           : True,
				'priority'          : self.kwargs['job'].priority,
				'maximum_priority'  : db.DB_IDLE_PRIORITY,
				'type'              : self.kwargs['job'].type,
				'state'             : "new",
				'addtime'           : datetime.datetime.now(),
				'epoch'             : WebMirror.misc.get_epoch_for_url(link),
				}
			links_out.append(new)

		WebMirror.UrlUpserter.do_link_batch_update_sess(self.log, self.db_sess, links_out)

	def high_priority_links_trigger(self, links):
		self._put_page_links(links=links, priority=db.DB_HIGH_PRIORITY)

	def normal_priority_links_trigger(self, links):
		self._put_page_links(links=links, priority=db.DB_MED_PRIORITY)

	def low_priority_links_trigger(self, links):
		self._put_page_links(links=links, priority=db.DB_LOW_PRIORITY)

	def idle_priority_links_trigger(self, links):
		self._put_page_links(links=links, priority=db.DB_IDLE_PRIORITY)


	def amqp_put_many(self, items):

		if not self._needs_amqp:
			raise ValueError("Plugin declared to not require AMQP connectivity, and yet AMQP call used?")

		if config.C_DO_RABBIT:
			self.log.info("Putting %s items into AMQP queue.", len(items))
			self.rpc_interface.put_many_feed_job(items)
		else:
			self.log.info("NOT Putting item in to AMQP queue!")


	def amqp_put_item(self, item):


		if not self._needs_amqp:
			raise ValueError("Plugin declared to not require AMQP connectivity, and yet AMQP call used?")

		if config.C_DO_RABBIT:
			self.log.info("Putting item in to AMQP queue!")
			self.rpc_interface.put_feed_job(item)
		else:
			self.log.info("NOT Putting item in to AMQP queue!")

		# if config.C_DO_RABBIT:
		# 	self.log.info("Putting item in to AMQP queue!")
		# 	if self.msg_q:
		# 		items_in_queue = self.msg_q.qsize()
		# 		if items_in_queue > 100:
		# 			self.log.warning("AMQP Message queue too large? Items in queue: %s", items_in_queue)

		# 		self.msg_q.put(("amqp_msg", item))

		# 	else:
		# 		self._amqpint.put_item(item)
		# else:
		# 	self.log.info("NOT Putting item in to AMQP queue!")


	def retrigger_page(self, release_url):

		trigger_priority = db.DB_MED_PRIORITY

		if self.db_sess is None:
			return
		while 1:
			try:
				have = self.db_sess.query(db.WebPages) \
					.filter(db.WebPages.url == release_url)   \
					.scalar()

				# If we don't have the page, ignore
				# it as the normal new-link upsert mechanism
				# will add it.
				if not have:
					self.log.info("New: '%s'", release_url)
					break

				# Also, don't reset if it's in-progress
				if (
						have.state in ['new', 'fetching', 'processing', 'removed']
						and have.priority <= trigger_priority
						and have.distance > 1
						and have.epoch <= WebMirror.misc.get_epoch_for_url(release_url)
					):
					self.log.info("Skipping: '%s' (%s, %s)", release_url, have.state, have.priority)
					break

				self.log.info("Retriggering page '%s' (%s, %s)", release_url, have.state, have.priority)
				have.state           = 'new'
				have.epoch           = WebMirror.misc.get_epoch_for_url(release_url) - 1
				have.distance        = 1
				have.priority        = trigger_priority
				self.db_sess.commit()
				break


			except sqlalchemy.exc.InvalidRequestError:
				print("InvalidRequest error!")
				self.db_sess.rollback()
				traceback.print_exc()
			except sqlalchemy.exc.OperationalError:
				print("InvalidRequest error!")
				self.db_sess.rollback()
			except sqlalchemy.exc.IntegrityError:
				print("[upsertRssItems] -> Integrity error!")
				traceback.print_exc()
				self.db_sess.rollback()

