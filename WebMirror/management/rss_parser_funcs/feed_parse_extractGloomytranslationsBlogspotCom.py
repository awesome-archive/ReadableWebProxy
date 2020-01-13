def extractGloomytranslationsBlogspotCom(item):
	'''
	Parser for 'gloomytranslations.blogspot.com'
	'''

	vol, chp, frag, postfix = extractVolChapterFragmentPostfix(item['title'])
	if not (chp or vol) or "preview" in item['title'].lower():
		return None

	tagmap = [
		('Hey Don\'t Act Unruly!',       'Hey Don\'t Act Unruly!',                      'translated'),
		('Master Summoner Online',       'Master Summoner Online',                      'translated'),
	]

	for tagname, name, tl_type in tagmap:
		if tagname in item['tags']:
			return buildReleaseMessageWithType(item, name, vol, chp, frag=frag, postfix=postfix, tl_type=tl_type)

	return False