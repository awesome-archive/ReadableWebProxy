def extractAutomaticmanualWordpressCom(item):
	'''
	Parser for 'automaticmanual.wordpress.com'
	'''

	vol, chp, frag, postfix = extractVolChapterFragmentPostfix(item['title'])
	if not (chp or vol) or "preview" in item['title'].lower():
		return None

	tagmap = [
		('The Bastard Called Brave And The Former Fiance',       'The Bastard Called Brave And The Former Fiance',                                               'translated'),
		('The man whose fiancées were stolen',                   'The man whose fiancées were stolen from him by the hero, is picked up by the goddess',         'translated'),
		('PRC',       'PRC',                      'translated'),
		('Loiterous', 'Loiterous',                'oel'),
	]

	for tagname, name, tl_type in tagmap:
		if tagname in item['tags']:
			return buildReleaseMessageWithType(item, name, vol, chp, frag=frag, postfix=postfix, tl_type=tl_type)


	return False