def extractPotatoesHaveEyesButCannotSeeMtTai(item):
	'''
	Parser for 'Potatoes Have Eyes But Cannot See Mt. Tai'
	'''

	vol, chp, frag, postfix = extractVolChapterFragmentPostfix(item['title'])
	if not (chp or vol) or "preview" in item['title'].lower():
		return False


	tagmap = [
		('fhmhyfql',       "Father, Mother Escaped Again!",                      'translated'),
		('wall flip',       "Father, Mother Escaped Again!",                      'translated'),
		('ddsnysh',       "An Oddette’s Otherworld Odyssey",                      'translated'),
	]

	for tagname, name, tl_type in tagmap:
		if tagname in item['tags']:
			return buildReleaseMessageWithType(item, name, vol, chp, frag=frag, postfix=postfix, tl_type=tl_type)

	return False