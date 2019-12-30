def extractBlackmaskedphantomWordpressCom(item):
	'''
	Parser for 'blackmaskedphantom.wordpress.com'
	'''

	vol, chp, frag, postfix = extractVolChapterFragmentPostfix(item['title'])
	if not (chp or vol) or "preview" in item['title'].lower():
		return None

	tagmap = [
		('Aloof King',                                                                  'Aloof King and Cold (Acting) Queen',                                                         'translated'),
		('The Adventures of the Idiot Hero, the Logical Mage, and Their Friends',       'The Adventures of the Idiot Hero, the Logical Mage, and Their Friends',                      'oel'), 
	]

	for tagname, name, tl_type in tagmap:
		if tagname in item['tags']:
			return buildReleaseMessageWithType(item, name, vol, chp, frag=frag, postfix=postfix, tl_type=tl_type)


	return False