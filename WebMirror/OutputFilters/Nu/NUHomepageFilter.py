

import WebMirror.OutputFilters.FilterBase

import common.database as db

import WebMirror.OutputFilters.util.MessageConstructors  as msgpackers
from WebMirror.OutputFilters.util.TitleParsers import extractTitle

from . import NUBaseFilter

import sqlalchemy.exc
import bs4
import re
import calendar
import traceback
import datetime
import time
import json
import cssutils
import WebRequest
import common.util.urlFuncs

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




class NuHomepageFilter(NUBaseFilter.NuBaseFilter):


	wanted_mimetypes = ['text/html']
	want_priority    = 95

	loggerPath = "Main.Text.NUHpProc"
	statsd_prefix = 'ReadableWebProxy.Nu.PageProcessor'


	@staticmethod
	def wantsUrl(url):
		if re.search(r"^https?://(?:www\.)?novelupdates\.com/?(?:\?pg=\d+)?$", url):
			print("NovelUpdates Homepage filter Wants url: '%s'" % url)
			return True

		return False


	def __init__(self, **kwargs):

		self.kwargs     = kwargs


		self.pageUrl    = kwargs['pageUrl']

		self.content    = kwargs['pgContent']
		self.type       = kwargs['type']
		self.db_sess    = kwargs['db_sess']

		# Don't do AMQP
		self._needs_amqp = False

		self.log.info("Processing NovelUpdates Homepage!")
		super().__init__(**kwargs)




	def __addNewLinks(self, link_items):

		'''
		Example release sections:
		{
		    'seriesname': 'Gate of Revelation',
		    'releaseinfo': 'c203',
		    'groupinfo': 'daoseekerblog',
		    'referrer': 'http://www.novelupdates.com/',
		    'outbound_wrapper': 'http://www.novelupdates.com/extnu/327682/',
		    'actual_target': None
		}, {
		    'seriesname': 'Mai Kitsune Waifu',
		    'releaseinfo': 'c174',
		    'groupinfo': 'subudai11',
		    'referrer': 'http://www.novelupdates.com/',
		    'outbound_wrapper': 'http://www.novelupdates.com/extnu/327678/',
		    'actual_target': None
		}, {
		    'seriesname': 'Mai Kitsune Waifu',
		    'releaseinfo': 'c174',
		    'groupinfo': 'subudai11',
		    'referrer': 'http://www.novelupdates.com/',
		    'outbound_wrapper': 'http://www.novelupdates.com/extnu/327674/',
		    'actual_target': None
		}

		'''

		commit_each = False
		while 1:
			try:
				new_count = 0
				for item in link_items:
					have = self.db_sess.query(db.NuReleaseItem)                                     \
						.filter(db.NuReleaseItem.outbound_wrapper==item['outbound_wrapper']) \
						.scalar()

					if not have:
						self.log.info("New: '%s' -> '%s' : '%s'", item['seriesname'], item['releaseinfo'], item['groupinfo'])
						have = db.NuReleaseItem(
								validated        = False,
								reviewed         = 'unverified',
								seriesname       = item['seriesname'].strip(),
								releaseinfo      = item['releaseinfo'].strip(),
								groupinfo        = item['groupinfo'].strip(),
								referrer         = item['referrer'],
								outbound_wrapper = item['outbound_wrapper'],
								first_seen       = datetime.datetime.now(),
								release_date     = datetime.datetime.now(),
								fetch_attempts   = 0,
							)
						self.db_sess.add(have)
						new_count += 1
						if commit_each:
							self.db_sess.commit()

						self.mon_con.incr('new-urls', 1)

				self.db_sess.commit()
				break

			except (sqlalchemy.exc.InvalidRequestError, sqlalchemy.exc.OperationalError, sqlalchemy.exc.IntegrityError):
				if commit_each == False:
					lfunc = self.log.warning
				else:
					lfunc = self.log.error

				lfunc("Error when inserting items!")
				if not commit_each:
					lfunc("Retrying with commit_each")
				if commit_each:
					for line in traceback.format_exc().strip().split("\n"):
						lfunc("%s", line.rstrip())
				self.db_sess.rollback()
				commit_each = True

		self.log.info("Found %s release links on page, %s of which were new!", len(link_items), new_count)



	def extractSeriesReleases(self, currentUrl, soup):

		container = soup.find('div', class_='l-content')

		assert container is not None

		masked_classes = self.getMaskedClasses(soup)

		release_tables = container.find_all('table', class_='tablesorter')

		ref_pages = set()
		releases = []
		for table_div in release_tables:
			for item in table_div.find_all("tr"):
				tds = item.find_all('td')
				if len(tds) == 3:
					series, release, group = tds
					referrer = series.a['href']

					assert not (referrer == "http://www.novelupdates.com" or
						referrer == "https://www.novelupdates.com" or
						referrer == "https://www.novelupdates.com/" or
						referrer == "http://www.novelupdates.com/")

					linkas = release.find_all('a', class_='chp-release')

					try:
						sname = series.a['title'].strip()
						gname = group.a['title'].strip()
					except Exception:
						sname = series.get_text().strip()
						gname = group.get_text().strip()

					for link in linkas:
						bad = any([tmp in masked_classes for tmp in link['class']])
						if not bad:
							self.log.info("Using %s for referrer for %s -> %s -> %s, %s, %s", referrer, sname, gname, link.get_text().strip(), link['class'], bad)
							self.log.info("Intermediate URL: %s", link['href'])

							linkfq = link['href']
							if linkfq.startswith("//"):
								linkfq = "https:"+linkfq
							if "http://" in linkfq:
								linkfq = linkfq.split("http://")[0]

							release = {
								'seriesname'       : sname,
								'releaseinfo'      : link.get_text().strip(),
								'groupinfo'        : gname,
								'referrer'         : referrer,
								'outbound_wrapper' : linkfq,
								'actual_target'    : None,
							}

							# Don't bother triggering qidian stuff, I track that better externally.
							if 'Qidian International' not in gname:
								releases.append(release)

							ref_pages.add(referrer)

		self.high_priority_links_trigger(ref_pages)

		return releases


	def processPage(self, url, content):
		soup = WebRequest.as_soup(self.content)
		releases = self.extractSeriesReleases(self.pageUrl, soup)
		if releases:
			self.__addNewLinks(releases)
			# self.retrigger_pages(releases)



	def extractContent(self):
		# print("Call to extract!")
		# print(self.amqpint)

		self.processPage(self.pageUrl, self.content)

