
import traceback
import os
import os.path
import sys
import re
import time
import urllib.parse
import yaml
import flags

class ValidationError(Exception):
	pass

def getStartURLs(ruleset):
	if not 'baseUrl' in ruleset:
		raise ValidationError("No 'baseUrl' values in ruleset!")
	ret = []

	# Allow the special-case "Generic" ruleset, which matches all
	# sites not matched by a more specific case.
	if ruleset['baseUrl'] == 'None':
		return None

	if not isinstance(ruleset['baseUrl'], list):
		print("BaseUrl type:", type(ruleset['baseUrl']))
		raise ValidationError("'baseUrl' is not a list!")
	ret += ruleset['baseUrl']

	if 'extraStartUrls' in ruleset:
		if not isinstance(ruleset['extraStartUrls'], list):
			raise ValidationError("'extraStartUrls' is not a list!")
		ret += ruleset['extraStartUrls']
	ret.sort()
	return ret

def getFeedUrls(ruleset):
	feeds = []
	if 'feedPostfix' in ruleset:
		assert isinstance(ruleset['feedPostfix'], str)
		feeds.extend([url+ruleset['feedPostfix'] for url in ruleset['baseUrl']])

	if 'feeds' in ruleset:
		assert isinstance(ruleset['feeds'], list)
		feeds.extend(ruleset['feeds'])

	return feeds

def getUrlBadWords(ruleset):
	assert 'badwords' in ruleset
	assert isinstance(ruleset['badwords'], list)
	return ruleset['badwords']


def getCompoundUrlBadWords(ruleset):
	if 'compound_badwords' in ruleset:
		assert isinstance(ruleset['compound_badwords'], list)
		return ruleset['compound_badwords']
	return []

def getStripTitle(ruleset):
	if not 'stripTitle' in ruleset:
		return []
	assert isinstance(ruleset['stripTitle'], list)
	return ruleset['stripTitle']

def getDecomposeBefore(ruleset):
	if not 'decomposeBefore' in ruleset:
		return []
	assert isinstance(ruleset['decomposeBefore'], list)
	for item in ruleset['decomposeBefore']:
		assert isinstance(item, dict)
	return ruleset['decomposeBefore']

def getDecomposeAfter(ruleset):
	assert 'decompose' in ruleset
	assert isinstance(ruleset['decompose'], list)
	for item in ruleset['decompose']:
		assert isinstance(item, dict)
	return ruleset['decompose']

def getFileDomains(ruleset, extant):
	if not 'fileDomains' in ruleset and not extant:
		return []
	if not 'fileDomains' in ruleset:
		return extant
	assert isinstance(ruleset['fileDomains'], list)
	for item in ruleset['fileDomains']:
		assert isinstance(item, str)

	return ruleset['fileDomains']+extant

def getDestyles(ruleset):
	if not 'destyle' in ruleset:
		return []
	assert isinstance(ruleset['destyle'], list)
	for item in ruleset['destyle']:
		assert isinstance(item, list)
		assert len(item) == 2
		assert isinstance(item[0], str)
		assert isinstance(item[1], dict)
	return ruleset['destyle']

def getPreserveAttrs(ruleset):
	if not 'preserveAttrs' in ruleset:
		return []
	assert isinstance(ruleset['preserveAttrs'], list)
	for item in ruleset['preserveAttrs']:
		assert isinstance(item, list)
		assert len(item) == 2
		assert isinstance(item[0], str)
		assert isinstance(item[1], str)
	return ruleset['preserveAttrs']


def getPossibleNetLocs(ruleset):
	'''
	Given the set of start URLs, and (if present) a set of
	allowed TLDs, generate a comprehensive set of possible allowable
	TLDs that the scrape can walk to.
	'''

	if ruleset['baseUrl'] == 'None':
		return None

	inTlds = set()
	if 'tld' in ruleset and ruleset['tld']:
		assert isinstance(ruleset['tld'], list)
		inTlds = set(ruleset['tld'])


	inList = set()
	for url in ruleset['baseUrl']:
		inList.add(url)

	TLDs = set([urllib.parse.urlsplit(url.lower()).netloc.rsplit(".")[-1] for url in inList])
	TLDs = TLDs | inTlds


	def genBaseUrlPermutations(url):


		netloc = urllib.parse.urlsplit(url.lower()).netloc
		if not netloc:
			raise ValueError("One of the scanned domains collapsed down to an empty string: '%s'!" % url)
		ret = set()
		# Generate the possible wordpress netloc values.
		if 'wordpress.com' in netloc:
			subdomain, mainDomain, tld = netloc.rsplit(".")[-3:]

			ret.add("www.{sub}.{main}.{tld}".format(sub=subdomain, main=mainDomain, tld=tld))
			ret.add("{sub}.{main}.{tld}".format(sub=subdomain, main=mainDomain, tld=tld))
			ret.add("www.{sub}.files.{main}.{tld}".format(sub=subdomain, main=mainDomain, tld=tld))
			ret.add("{sub}.files.{main}.{tld}".format(sub=subdomain, main=mainDomain, tld=tld))

		# Blogspot is annoying and sometimes a single site is spread over several tlds. *.com, *.sg, etc...
		if 'blogspot.' in netloc:
			subdomain, mainDomain, dummy_tld = netloc.rsplit(".")[-3:]
			for tld in TLDs:
				ret.add("www.{sub}.{main}.{tld}".format(sub=subdomain, main=mainDomain, tld=tld))
				ret.add("{sub}.{main}.{tld}".format(sub=subdomain, main=mainDomain, tld=tld))


		elif 'google.' in netloc:
			pass

		else:
			assert "." in netloc, "No period in netloc: '%s'" % netloc
			base, dummy_tld = netloc.rsplit(".", 1)
			for tld in TLDs:
				ret.add("{main}.{tld}".format(main=base, tld=tld))
				# print(ret)
		return ret

	retSet = set()
	for url in inList:
		items = genBaseUrlPermutations(url)
		retSet.update(items)

	if 'FOLLOW_GOOGLE_LINKS' in ruleset and ruleset['FOLLOW_GOOGLE_LINKS']:
		retSet.add('https://docs.google.com/document/')
		retSet.add('https://docs.google.com/spreadsheets/')
		retSet.add('https://drive.google.com/folderview')
		retSet.add('https://drive.google.com/open')

	# Filter out spurious 'blogspot.com.{TLD}' entries that are getting in somehow
	ret = [item for item in retSet if not item.startswith('blogspot.com')]

	return ret

def getAllImages(ruleset):
	if not 'allImages' in ruleset:
		return False
	return ruleset['allImages']

def getTrigger(ruleset):
	if not 'trigger' in ruleset:
		return True
	return ruleset['trigger']

def getRefetch(ruleset):
	if not 'normal_fetch_mode' in ruleset:
		return True
	return ruleset['normal_fetch_mode']

def getDisableRewalk(ruleset):
	if not 'rewalk_disabled' in ruleset:
		return False
	return ruleset['rewalk_disabled']

def getDisallowDuplicatePathComponents(ruleset):
	if not 'disallow_duplicate_path_segments' in ruleset:
		return True
	return ruleset['disallow_duplicate_path_segments']

def getIgnoreMalformed(ruleset):
	if not 'IGNORE_MALFORMED_URLS' in ruleset:
		return False
	return ruleset['IGNORE_MALFORMED_URLS']

def getMaximumFetchPriority(ruleset):
	# Highest priority is 0, lowest is 1000000
	if not 'get_maximum_fetch_priority' in ruleset:
		return 0
	# Clamp the max to 999999
	return min(ruleset['get_maximum_fetch_priority'], 999999)

def getGenreType(ruleset):
	assert 'type' in ruleset, "Type missing from ruleset!"
	assert ruleset['type'] in ['western', 'eastern', 'unknown']
	return ruleset['type']

def getSpecialFilters(ruleset):
	ret = {}
	if "special_case_filters" in ruleset:
		for netloc, params in ruleset['special_case_filters'].items():
			ret[netloc] = params
	return ret

def getSkipFilters(ruleset):
	ret = []
	if "skip_filters" in ruleset:
		for netloc, regex, ignorecase in ruleset['skip_filters']:
			comp = re.compile(regex, re.I if ignorecase else None)
			ret.append((netloc, comp))
	return ret

def get_www_remap_lut(ruleset):
	ret = {}

	if "www_no_www_same" in ruleset:
		if isinstance(ruleset['www_no_www_same'], bool) and ruleset['www_no_www_same']:
			pass
		elif isinstance(ruleset['www_no_www_same'], list):
			for netloc in ruleset['www_no_www_same']:
				pass
		else:
			raise RuntimeError("'www_no_www_same' must be a list. Passed %s (%s)" % (type(ruleset['www_no_www_same']), ruleset['www_no_www_same']))

	# 	for netloc, regex, ignorecase in ruleset['skip_filters']:
	# 		comp = re.compile(regex, re.I if ignorecase else None)
	# 		ret.append((netloc, comp))
	return ret

def get_http_s_remap_lut(ruleset):
	ret = {}
	if "http_https_same" in ruleset:
		if isinstance(ruleset['http_https_same'], bool) and ruleset['http_https_same']:
			pass
		elif isinstance(ruleset['http_https_same'], list):
			for netloc in ruleset['http_https_same']:
				pass
		else:
			raise RuntimeError("'http_https_same' must be a list. Passed %s (%s)" % (type(ruleset['http_https_same']), ruleset['http_https_same']))

	# if "http_https_same" in ruleset:
	# 	for netloc, regex, ignorecase in ruleset['skip_filters']:
	# 		comp = re.compile(regex, re.I if ignorecase else None)
	# 		ret.append((netloc, comp))
	return ret

def getAttributeRewriteRules(ruleset):
	if not 'rewriteAttrs' in ruleset:
		return False
	return ruleset['rewriteAttrs']

def getDecomposeSvg(ruleset):
	if not 'decompose_svg' in ruleset:
		return False
	return ruleset['decompose_svg']

def getRewalkIntervalDays(ruleset):
	if not 'rewalk_interval_days' in ruleset:
		return 90
	ret = ruleset['rewalk_interval_days']
	assert ret > 3
	return ret

def getMaxActiveJobs(ruleset):
	if not 'max_active_jobs' in ruleset:
		return 100
	ret = ruleset['max_active_jobs']
	assert ret > 0
	return ret


def transmitFeeds(ruleset):
	assert 'send_raw_feed' in ruleset, "'send_raw_feed' flag missing from ruleset!"

	return bool(ruleset['send_raw_feed'])


def checkBadValues(ruleset):
	assert 'wg' not in ruleset
	assert 'threads' not in ruleset
	assert 'startUrl' not in ruleset
	assert 'tableKey' not in ruleset
	assert 'pluginName' not in ruleset
	assert 'loggerPath' not in ruleset


def validateRuleKeys(dat, fname):
	checkBadValues(dat)
	keys = list(dat.keys())
	# print(keys)
	valid = [
		'badwords',
		'compound_badwords',

		'decompose',
		'decomposeBefore',

		'baseUrl',
		'feeds',
		'feedPostfix',
		'stripTitle',
		'tld',
		'FOLLOW_GOOGLE_LINKS',
		'allImages',
		'fileDomains',
		'destyle',
		'preserveAttrs',
		'type',
		'extraStartUrls',
		'trigger',
		'decompose_svg',

		'normal_fetch_mode',
		'rewalk_disabled',
		'send_raw_feed',
		'special_case_filters',

		'rewriteAttrs',
		'rewalk_interval_days',
		'disallow_duplicate_path_segments',
		'skip_filters',

		'www_no_www_same',
		'http_https_same',
		'max_active_jobs',

		# Not currently implemented, but useful
		'titleTweakLut',
		]
	for key in keys:
		assert key in valid, "Key '%s' from ruleset '%s' is not valid!" % (key, fname)


def load_validate_rules(fname, dat):

	validateRuleKeys(dat, fname)


	rules = {}
	rules['starturls']                         = getStartURLs(dat)
	rules['attrRewriteRules']                  = getAttributeRewriteRules(dat)
	rules['feedurls']                          = getFeedUrls(dat)

	rules['badwords']                          = getUrlBadWords(dat)
	rules['compound_badwords']                 = getCompoundUrlBadWords(dat)
	rules['stripTitle']                        = getStripTitle(dat)
	rules['decomposeBefore']                   = getDecomposeBefore(dat)
	rules['decompose']                         = getDecomposeAfter(dat)
	rules['netlocs']                           = getPossibleNetLocs(dat)

	rules['allImages']                         = getAllImages(dat)
	rules['fileDomains']                       = getFileDomains(dat, rules['netlocs'])
	rules['IGNORE_MALFORMED_URLS']             = getIgnoreMalformed(dat)
	rules['type']                              = getGenreType(dat)

	rules['send_raw_feed']                     = transmitFeeds(dat)
	rules['destyle']                           = getDestyles(dat)
	rules['preserveAttrs']                     = getPreserveAttrs(dat)
	rules['decompose_svg']                     = getDecomposeSvg(dat)

	rules['rewalk_interval_days']              = getRewalkIntervalDays(dat)
	rules['max_active_jobs']                   = getMaxActiveJobs(dat)
	rules['disallow_duplicate_path_segments']  = getDisallowDuplicatePathComponents(dat)
	rules['maximum_priority']                  = getMaximumFetchPriority(dat)
	rules['skip_filters']                      = getSkipFilters(dat)

	rules['www_no_www_same']                   = get_www_remap_lut(dat)
	rules['http_https_same']                   = get_http_s_remap_lut(dat)

	rules['trigger']                           = getTrigger(dat)
	if not rules['trigger']:
		rules['starturls']                     = []

	rules['normal_fetch_mode']                 = getRefetch(dat)
	rules['rewalk_disabled']                   = getDisableRewalk(dat)

	rules['filename']                          = fname
	special = getSpecialFilters(dat)

	return rules, special

def get_rules():
	cwd = os.path.split(__file__)[0]
	rulepath = os.path.join(cwd, "rules")

	items = os.listdir(rulepath)
	items.sort()
	ret = []
	specials = {}
	for item in [os.path.join(rulepath, item) for item in items if item.endswith('.yaml')]:

		with open(item, "r", encoding='utf-8') as fp:
			try:
				text = fp.read()
				# Fuck you YAML, tabs are better then spaces.
				# Also, single-space indentation discontinuity in
				# YAML causes the whole file to load wrong.
				text = text.replace("	", "    ")
				dat = yaml.load(text, Loader=yaml.SafeLoader)
				rules, special = load_validate_rules(item, dat)
				if rules:
					ret.append(rules)

				if special:
					for key, val in special.items():
						specials[key] = val

				# print(item)
				assert 'starturls' in rules
				# print(rules['starturls'])

			except (yaml.scanner.ScannerError, yaml.parser.ParserError):
				print("ERROR!")
				print("Attempting to load file: '{}'".format(item))
				traceback.print_exc()
			except ValidationError:
				print("ERROR!")
				print("Validation error when trying to load file: '{}'".format(item))
				traceback.print_exc()
				print(dat)
			except AssertionError:
				print("ERROR!")
				print("Validation error when trying to load file: '{}'".format(item))
				traceback.print_exc()
				# print(dat)

	# for ruleset in ret:
	# 	print(type(ruleset['starturls']))

	assert [True for ruleset in ret if 'starturls' in ruleset and ruleset['starturls'] == None], "You must have a base ruleset for matching generic sites (with a baseurl value of `None`)"

	print("Loaded rulesets ({}):".format(len(ret)))

	# traceback.print_exc()
	# for ruleset in ret:
	# 	print(ruleset)
	# 	print()
	return ret, specials

# Reload the rules every 8 hours
reload_interval = 60 * 60 * 8

last_rule_load = 0
last_triggered_load = 0
last_special_load = 0
last_raw_load = 0


def load_rules(override=False):
	global last_rule_load

	now = time.time()
	if flags.RULE_CACHE == None or "debug" in sys.argv or override or (last_rule_load + reload_interval) < now:
		last_rule_load = now
		print("Need to load rules (%s, %s, %s)" % (flags.RULE_CACHE == None, "debug" in sys.argv, (last_rule_load + reload_interval) < now))
		rules, specials = get_rules()

		# Might as well update both while we're here.
		flags.RULE_CACHE = rules
		flags.SPECIAL_CASE_CACHE = specials

	return flags.RULE_CACHE



def load_special_case_sites(override=False):
	global last_special_load

	now = time.time()
	if flags.SPECIAL_CASE_CACHE == None or "debug" in sys.argv or override or (last_special_load + reload_interval) < now:
		last_special_load = now
		print("Need to load special-url handling ruleset (%s, %s, %s)" % (flags.SPECIAL_CASE_CACHE == None, "debug" in sys.argv, (last_special_load + reload_interval) < now))
		rules, specials = get_rules()

		# Might as well update both while we're here.
		flags.RULE_CACHE = rules
		flags.SPECIAL_CASE_CACHE = specials

	return flags.SPECIAL_CASE_CACHE



def get_raw_mirror_confs():

	cwd = os.path.split(__file__)[0]
	rulepath = os.path.join(cwd, "raw_mirror_rules")

	items = os.listdir(rulepath)
	items.sort()
	ret = []
	specials = {}
	for item in [os.path.join(rulepath, item) for item in items if item.endswith('.yaml')]:
		print("Irem: ", item)


	return ret


def load_raw_mirror_sites():
	global last_raw_load


	now = time.time()
	if flags.RAW_MIRROR_CACHE == None or "debug" in sys.argv or (last_raw_load + reload_interval) < now:
		last_raw_load = now
		print("Need to load special-url handling ruleset (%s, %s, %s)" % (flags.RAW_MIRROR_CACHE == None, "debug" in sys.argv, (last_raw_load + reload_interval) < now))
		flags.RAW_MIRROR_CACHE = get_raw_mirror_confs()


	return flags.RAW_MIRROR_CACHE




def netloc_send_feed(netloc):
	for ruleset in load_rules():
		if ruleset['send_raw_feed']:
			if netloc in ruleset['netlocs']:
				return True
	return False




##############################################################################################################
##############################################################################################################
##############################################################################################################


def import_from_path(path):
	"""Import a module / class from a path string.

	:param str path: class path, e.g., ndscheduler.core.job
	:return: class object
	:rtype: class
	"""

	components = path.split('.')
	module = __import__('.'.join(components[:-1]))
	for comp in components[1:-1]:
		module = getattr(module, comp)
	return getattr(module, components[-1])


def get_triggered_urls():
	'''
	Iterate over all the active jobs, and
	extract the triggered URLs from those jobs to
	pass on to the triggering system.


	'''
	import WebMirror.TimedTriggers.UrlTriggers
	import activeScheduledTasks
	ret = []
	for job in activeScheduledTasks.target_jobs:
		print("Job:", (type(job), job, ))
		plugin = import_from_path(job).invokable
		if issubclass(plugin, WebMirror.TimedTriggers.UrlTriggers.UrlTrigger):
			instance = plugin()
			urls = instance.get_urls()
			ret += urls
	return ret

def load_triggered_url_list():
	global last_triggered_load
	now = time.time()


	if flags.TRIGGERED_URLS_CACHE == None or "debug" in sys.argv or (last_triggered_load + reload_interval) < now:
		print("Need to load special-url handling ruleset (%s, %s, %s)" % (flags.TRIGGERED_URLS_CACHE == None, "debug" in sys.argv, (last_triggered_load + reload_interval) < now))
		flags.TRIGGERED_URLS_CACHE = get_triggered_urls()

		print("Triggered URLs:")
		print(flags.TRIGGERED_URLS_CACHE)

	return flags.TRIGGERED_URLS_CACHE

##############################################################################################################
##############################################################################################################
##############################################################################################################



# Trigger cache-loading of the ruleset.

def startup():
	load_rules()
	load_special_case_sites()
	load_raw_mirror_sites()

	# # Don't load the triggered URLs list, as it requires loading a bunch of database dependencies
	# # that can break things due to fiddly import ordering issues.
	# load_triggered_url_list()

startup()


def test():
	# print(load_raw_mirror_sites())
	# print(load_special_case_sites())

	ruleset = load_rules()

	specialty_handlers = load_special_case_sites()

	# print("SiteArchiver rules loaded")
	relinkable = set()
	for item in ruleset:
		[relinkable.add(url) for url in item['fileDomains']]         #pylint: disable=W0106
		if item['netlocs'] != None:
			[relinkable.add(url) for url in item['netlocs']]             #pylint: disable=W0106


	ctnt_filters = {}
	rsc_filters  = {}


	for item in ruleset:
		if not item['netlocs']:
			continue
		for netloc in item['netlocs']:
			ctnt_filters[netloc] = item['netlocs']
		for netloc in item['fileDomains']:
			rsc_filters[netloc]  = item['fileDomains']

	# for key, value in ctnt_filters.items():
	# 	print(key, value)

	load_triggered_url_list()


	# import pdb
	# pdb.set_trace()

def test_multuple_load():
	for x in range(100):
		startup()
		print("Loop ", x)


def time_it():
	import timeit
	t = timeit.Timer("time.time()", setup="import time")
	print("Repeating")
	print(t.repeat())


if __name__ == "__main__":
	test_multuple_load()
	# time_it()
	# test()
	# for ruleset in load_rules():
	# 	if ruleset['send_raw_feed'] == False:
	# 		print(ruleset['netlocs'])
