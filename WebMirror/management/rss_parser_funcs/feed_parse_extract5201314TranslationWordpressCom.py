def extract5201314TranslationWordpressCom(item):
	'''
	Parser for '5201314translation.wordpress.com'
	'''

	vol, chp, frag, postfix = extractVolChapterFragmentPostfix(item['title'])
	if not (chp or vol) or "preview" in item['title'].lower():
		return None

	tagmap = [
		('guardian (bu hui xia qi)',       'guardian (bu hui xia qi)',                      'translated'),
		('peeping woman',                  'peeping woman',                      'translated'),
		('the zoo in my eyes',             'The Zoo In My Eyes',                      'translated'),
		('PRC',       'PRC',                      'translated'),
		('Loiterous', 'Loiterous',                'oel'),
	]

	for tagname, name, tl_type in tagmap:
		if tagname in item['tags']:
			return buildReleaseMessageWithType(item, name, vol, chp, frag=frag, postfix=postfix, tl_type=tl_type)


	return False