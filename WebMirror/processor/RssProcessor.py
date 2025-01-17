



from . import ProcessorBase


import feedparser
import bs4
import json
import time
import calendar
import urllib.parse
import traceback
import WebRequest
import common.database
import common.util.urlFuncs as urlFuncs
import WebMirror.OutputFilters.rss.FeedDataParser

# import TextScrape.RelinkLookup
# import TextScrape.RELINKABLE as RELINKABLE


import WebMirror.processor.HtmlProcessor


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



class RssProcessor(WebMirror.OutputFilters.rss.FeedDataParser.DataParser):


	wanted_mimetypes = [
							'application/atom+xml',
							'application/rdf+xml',
							'application/rss+xml',
							'application/xml',
							'text/xml',
						]
	want_priority    = 50

	loggerPath = "Main.Text.RssProcessor"

	_no_ret = False

	@staticmethod
	def wantsFromContent(content):
		try:
			# Check if the feed has a version
			# print("Content: ", content)
			feed = feedparser.parse(content)
			# print("Parsed feed: ", feed)
			return bool(feed['version'])
		except Exception:
			# print("Feedparser failed on content!")
			# traceback.print_exc()
			# print(content)
			return False

	def __init__(self, **kwargs):

		super().__init__(**kwargs)

		# We're inheriting from a filter (which implicitly sets _no_ret),
		# but we /do/ return content (Rss is a oddball filter instance), so
		# therefore we reset _no_ret after calling the parent initializer
		self._no_ret = False

		self.kwargs     = kwargs

		self.loggerPath = kwargs['loggerPath']+".RssProcessor"
		self.pageUrl    = kwargs['pageUrl']

		self.content    = kwargs['pgContent']
		self.type       = kwargs['type']

		self.log.info("Processing RSS Item")


	# @profile
	def parseFeed(self, rawFeed):
		return feedparser.parse(rawFeed)




	def extractFeedContents(self, feedUrl, contentDat):
		# TODO: Add more content type parsing!

		# So the complete fruitcakes at http://gravitytales.com/feed/ are apparently
		# embedding their RSS entries in a CDATA field in their feed, somehow.
		# Anyways, I think they probably broke wordpress. However, they're then breaking
		# /my/ stuff, so work around their fucked up feed format.
		if isinstance(contentDat, str):
			contentDat = [{
				'value' : contentDat,
				'type'  : 'text/html'
			}]

		if len(contentDat) != 1:
			print(contentDat)
			raise ValueError("How can one post have multiple contents?")


		contentDat = contentDat[0]

		if not contentDat['value']:
			return "No content for post!"

		params = self.kwargs.copy()


		params['pgContent'] = contentDat['value']
		params['mimeType']  = contentDat['type']


		# baseUrls, pageUrl, pgContent, loggerPath, relinkable
		scraper = WebMirror.processor.HtmlProcessor.HtmlPageProcessor(extra_msg="for rss filter", extra_logger="-RSS", **params)

		extracted = scraper.extractContent()
		assert contentDat['type'] == 'text/html', "Content is not html? Type: %s" % contentDat['type']
		content = extracted['contents']

		# Use a parser that doesn't try to generate a well-formed output (and therefore doesn't insert
		# <html> or <body> into content that will be only a part of the rendered page)
		soup = bs4.BeautifulSoup(content, "html.parser")

		if soup.html:
			soup.html.unwrap()
		if soup.body:
			soup.body.unwrap()

		try:
			cont = soup.prettify()
		except RuntimeError:
			try:
				cont = str(soup)
			except RuntimeError:
				cont = '<H2>WARNING - Failure when cleaning and extracting content!</H2><br><br>'
				cont += content


		# content = "Disabled?"
		return content



	def processFeed(self, feed, feedUrl):

		if '://pumanovels.com/' in feedUrl:
			return []
		if '://comrademao.com/' in feedUrl:
			return []

		meta = feed['feed']
		entries = feed['entries']

		ret = []

		for entry in entries:
			if not 'title' in entry:
				# Broken RSS sources
				continue
			if entry['title'].startswith('User:'):
				# The tsuki feed includes changes to user pages. Fuck that noise. Ignore that shit.
				continue

			# Fake various components if the rss source is fucked up.
			if not 'guid' in entry:
				entry['guid'] = entry['link'] + entry['title']
			if not "authors" in entry:
				entry['authors'] = ""


			kv_id = feedUrl + " " + entry['guid']
			item = common.database.get_from_db_key_value_store(kv_id)

			# Don't reparse releases continuously.
			if item:
				self.log.info("Using cached parse output!")
			else:
				item['feedtype'] = self.type

				item['title']    = entry['title']
				item['guid']     = entry['guid']
				item['linkUrl']  = urlFuncs.cleanUrl(entry['link'])
				item['authors']  = entry['authors']

				item['feedUrl']  = feedUrl



				if 'updated_parsed' in entry and entry['updated_parsed']:
					item['updated']   = calendar.timegm(entry['updated_parsed'])

				if 'published_parsed' in entry and entry['published_parsed']:
					item['published'] = calendar.timegm(entry['published_parsed'])


				if 'updated' not in item:
					item['updated']   = time.time()

				if 'published' not in item or ('updated' in item and item['published'] > item['updated']):
					item['published'] = item['updated']

				item['tags']    = []
				if 'tags' in entry:
					for tag in entry['tags']:
						item['tags'].append(tag['term'])

				if 'content' in entry:
					item['content'] = entry['content']
					item['contents'] = self.extractFeedContents(feedUrl, entry['content'])
				elif 'summary' in entry:
					item['contents'] = self.extractFeedContents(feedUrl, entry['summary'])
				else:
					self.log.warning('Empty item in feed?')
					self.log.warning('Feed url: %s', feedUrl)
					item['contents'] = ""

			common.database.set_in_db_key_value_store(kv_id, item)

			# processFeedData() call has to be /before/ we convert the tags to a json object.
			self.processFeedData(self.db_sess, item)


			assert(isinstance(item['published'], (float, int))), "Wrong type for item['published']. Expected '%s', received '%s'" % ((float, int), type(item['published']))
			assert(isinstance(item['updated'], (float, int, type(None)))), "Wrong type for item['updated']. Expected '%s', received '%s'" % ((float, int, type(None)), type(item['updated']))

			# print("Keys: ", list(item.keys()))
			ret.append(item)
		return ret



	def extractContent(self):

		feed = self.parseFeed(self.content)



		try:
			data = self.processFeed(feed, self.pageUrl)
		except Exception as e:
			self.log.critical("Failure parsing RSS feed!")
			for line in traceback.format_exc().split("\n"):
				self.log.critical(line)
			raise e


		plainLinks = []
		rsrcLinks  = []

		if 'entries' in feed:
			for post in feed['entries']:

				if hasattr(post, 'contenturl') and post.contenturl.startswith("tag:blogger.com"):
					continue

				if hasattr(post, 'contenturl') and post.contenturl and not '#comment_' in post.contenturl:
					plainLinks.append(post.contenturl)

				if hasattr(post, 'contents') and post.contents and post.contents != 'Disabled?' and post.contents != 'wat':
					soup = WebRequest.as_soup(post.contents)
					# print(post.contents)
					# Make all the page URLs fully qualified, so they're unambiguous
					soup = urlFuncs.canonizeUrls(soup, post.contenturl)

					# pull out the page content and enqueue it. Filtering is
					# done in the parent.
					plainLinks.extend(self.extractLinks(soup, post.contenturl))
					rsrcLinks.extend(self.extractImages(soup, post.contenturl))
				if 'links' in post:
					for link in post['links']:
						if 'href' in link:
							plainLinks.append(link['href'])
				if 'link' in post:
					plainLinks.append(post['link'])


		# I can't for the life of me remember why I added this.
		# self.normal_priority_links_trigger(plainLinks + rsrcLinks)

		output = bs4.BeautifulSoup("<html><body></body></html>", "lxml")


		output.html.body.append(output.new_tag("h3", text="RSS Feed for url '%s'" % self.pageUrl))

		for feed_item in data:
			itemdiv = output.new_tag("div")
			temp = output.new_tag("h5", )
			temp.string = feed_item['title']
			itemdiv.append(temp)
			temp = output.new_tag("a", href=feed_item['linkUrl'], )
			temp.string = feed_item['linkUrl']
			itemdiv.append(temp)
			temp = output.new_tag("p", )
			temp.string = ", ".join([str(author) for author in feed_item['authors']])
			itemdiv.append(temp)
			temp = output.new_tag("p", )
			temp.string = feed_item['contents']
			itemdiv.append(temp)

			output.html.body.append(itemdiv)


		ret = {}

		ret['title']    = "RSS Feed for url '%s'" % self.pageUrl
		ret['contents'] = output.html.body.prettify()
		ret['mimeType'] = "text/html"

		ret['rss-content'] = (data)
		ret['plainLinks']  = plainLinks
		ret['rsrcLinks']   = rsrcLinks


		return ret


def test():
	print("Test mode!")
	import logSetup
	import WebMirror.rules
	import WebMirror.Engine
	import multiprocessing
	logSetup.initLogging()

	c_lok = cookie_lock = multiprocessing.Lock()
	engine = WebMirror.Engine.SiteArchiver(cookie_lock=c_lok)



	url = 'http://taulsn.wordpress.com/feed/'

	job = testJobFromUrl(url)
	engine.dispatchRequest(job)


	url = 'http://turb0translation.blogspot.com/feeds/posts/default'
	job = testJobFromUrl(url)
	engine.dispatchRequest(job)


	url = 'http://www.w3schools.com/xml/note.xml'
	job = testJobFromUrl(url)
	engine.dispatchRequest(job)


if __name__ == "__main__":
	test()

