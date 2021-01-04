def extractMashintransWordpressCom(item):
	'''
	Parser for 'mashintrans.wordpress.com'
	'''

	vol, chp, frag, postfix = extractVolChapterFragmentPostfix(item['title'])
	if not (chp or vol) or "preview" in item['title'].lower():
		return None

	tagmap = [
		('Shinka no Mi',       'Shinka no Mi',                      'translated'),
		('about my login bonus after i was transferred to another world being obviously too strong',       'about my login bonus after i was transferred to another world being obviously too strong',                      'translated'),
		('PRC',       'PRC',                      'translated'),
		('Loiterous', 'Loiterous',                'oel'),
	]

	for tagname, name, tl_type in tagmap:
		if tagname in item['tags']:
			return buildReleaseMessageWithType(item, name, vol, chp, frag=frag, postfix=postfix, tl_type=tl_type)


	return False