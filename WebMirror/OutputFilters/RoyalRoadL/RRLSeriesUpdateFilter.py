


import WebMirror.OutputFilters.FilterBase

import common.database as db

import WebMirror.OutputFilters.util.MessageConstructors  as msgpackers
from WebMirror.OutputFilters.util.TitleParsers import extractTitle

import bs4
import re
import calendar
import traceback
import datetime
import time
import json
import WebRequest
import common.util.urlFuncs
MIN_RATING = 5

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




class RRLSeriesUpdateFilter(WebMirror.OutputFilters.FilterBase.FilterBase):


	wanted_mimetypes = [

							'text/html',
						]
	want_priority    = 50

	loggerPath = "Main.Filter.RoyalRoad.Series"


	@staticmethod
	def wantsUrl(url):
		want = set([
			'http://royalroadl.com/fictions/active-popular',
			'http://royalroadl.com/fictions/active-top-50',
			'http://royalroadl.com/fictions/best-rated',
			'http://royalroadl.com/fictions/latest-updates',
			'http://royalroadl.com/fictions/new-releases',
			'http://royalroadl.com/fictions/weekly-popular',
			'http://royalroadl.com/fictions/weekly-views-top-50',
			'http://www.royalroadl.com/fictions/active-top-50',
			'http://www.royalroadl.com/fictions/best-rated',
			'http://www.royalroadl.com/fictions/latest-updates',
			'http://www.royalroadl.com/fictions/new-releases',
			'http://www.royalroadl.com/fictions/weekly-views-top-50',

			'https://royalroadl.com/fictions/active-popular',
			'https://royalroadl.com/fictions/active-top-50',
			'https://royalroadl.com/fictions/best-rated',
			'https://royalroadl.com/fictions/latest-updates',
			'https://royalroadl.com/fictions/new-releases',
			'https://royalroadl.com/fictions/weekly-popular',
			'https://royalroadl.com/fictions/weekly-views-top-50',
			'https://www.royalroadl.com/fictions/active-top-50',
			'https://www.royalroadl.com/fictions/best-rated',
			'https://www.royalroadl.com/fictions/latest-updates',
			'https://www.royalroadl.com/fictions/new-releases',
			'https://www.royalroadl.com/fictions/weekly-views-top-50',

			'http://royalroad.com/fictions/active-popular',
			'http://royalroad.com/fictions/active-top-50',
			'http://royalroad.com/fictions/best-rated',
			'http://royalroad.com/fictions/latest-updates',
			'http://royalroad.com/fictions/new-releases',
			'http://royalroad.com/fictions/weekly-popular',
			'http://royalroad.com/fictions/weekly-views-top-50',
			'http://www.royalroad.com/fictions/active-top-50',
			'http://www.royalroad.com/fictions/best-rated',
			'http://www.royalroad.com/fictions/latest-updates',
			'http://www.royalroad.com/fictions/new-releases',
			'http://www.royalroad.com/fictions/weekly-views-top-50',

			'https://royalroad.com/fictions/active-popular',
			'https://royalroad.com/fictions/active-top-50',
			'https://royalroad.com/fictions/best-rated',
			'https://royalroad.com/fictions/latest-updates',
			'https://royalroad.com/fictions/new-releases',
			'https://royalroad.com/fictions/weekly-popular',
			'https://royalroad.com/fictions/weekly-views-top-50',
			'https://www.royalroad.com/fictions/active-top-50',
			'https://www.royalroad.com/fictions/best-rated',
			'https://www.royalroad.com/fictions/latest-updates',
			'https://www.royalroad.com/fictions/new-releases',
			'https://www.royalroad.com/fictions/weekly-views-top-50',
		])
		url = url.lower()
		if any([url.startswith(tmp) for tmp in want]):

			print("RRLSeriesUpdateFilter Wants url: '%s'" % url)
			return True
		# print("RRLSeriesUpdateFilter doesn't want url: '%s'" % url)
		return False

	def __init__(self, **kwargs):

		self.kwargs     = kwargs


		self.pageUrl    = kwargs['pageUrl']

		self.content    = kwargs['pgContent']
		self.type       = kwargs['type']
		self.db_sess    = kwargs['db_sess']

		self.log.info("Processing RoyalRoadL Item")
		super().__init__(**kwargs)


##################################################################################################################################
##################################################################################################################################
##################################################################################################################################


	def extractSeriesReleases(self, seriesPageUrl, soup):

		containers = soup.find_all('div', class_='fiction-list-item')
		# print(soup)
		# print("container: ", containers)
		if not containers:
			return []
		urls = []
		for item in containers:
			div = item.find('h2', class_='fiction-title')
			a = div.find("a")
			if a:
				url = common.util.urlFuncs.rebaseUrl(a['href'], seriesPageUrl)
				urls.append(url)
			else:
				self.log.error("No series in container: %s", item)

		return set(urls)


	def retrigger_pages(self, releases):
		self.log.info("Total releases found on page: %s. Forcing retrigger of item pages.", len(releases))

		for release_url in releases:
			self.retrigger_page(release_url)





	def processPage(self, url, content):
		print("processPage() call")
		soup = WebRequest.as_soup(self.content)
		releases = self.extractSeriesReleases(self.pageUrl, soup)
		if releases:
			self.retrigger_pages(releases)




##################################################################################################################################
##################################################################################################################################
##################################################################################################################################



	def extractContent(self):
		# print("Call to extract!")
		# print(self.amqpint)

		self.processPage(self.pageUrl, self.content)



def test():
	print("Test mode!")
	import logSetup
	import WebMirror.rules
	import WebMirror.Engine
	import multiprocessing
	logSetup.initLogging()

	c_lok = cookie_lock = multiprocessing.Lock()
	engine = WebMirror.Engine.SiteArchiver(cookie_lock=c_lok)





	# engine.dispatchRequest(testJobFromUrl('http://www.royalroadl.com/fiction/3021'))
	# engine.dispatchRequest(testJobFromUrl('http://www.royalroadl.com/fictions/latest-updates/'))

	# engine.dispatchRequest(testJobFromUrl('http://www.royalroadl.com/fictions/best-rated/'))
	engine.dispatchRequest(testJobFromUrl('http://www.royalroadl.com/fictions/latest-updates/'))
	engine.dispatchRequest(testJobFromUrl('http://www.royalroadl.com/fictions/active-top-50/'))
	engine.dispatchRequest(testJobFromUrl('http://www.royalroadl.com/fictions/weekly-views-top-50/'))
	engine.dispatchRequest(testJobFromUrl('http://www.royalroadl.com/fictions/newest/'))



if __name__ == "__main__":
	test()

