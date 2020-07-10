def extractJinzeffectWordpressCom(item):
	'''
	Parser for 'jinzeffect.wordpress.com'
	'''

	vol, chp, frag, postfix = extractVolChapterFragmentPostfix(item['title'])
	if not (chp or vol) or "preview" in item['title'].lower():
		return None

	tagmap = [
		('Eternal Reverence',                             'Eternal Reverence',                                            'translated'),
		('i\'m an olympic superstar',                     'i\'m an olympic superstar',                                    'translated'),
		('tpe',                                           'The Paranoid Emperor’s Black Moonlight Shizun',                'translated'),
		('PRC',                     'PRC',                                    'translated'),
		('Loiterous',               'Loiterous',                              'oel'),
	]

	for tagname, name, tl_type in tagmap:
		if tagname in item['tags']:
			return buildReleaseMessageWithType(item, name, vol, chp, frag=frag, postfix=postfix, tl_type=tl_type)

	if item['tags'] == ['translation']:
		titlemap = [
			('TPE – ',                            'The Paranoid Emperor’s Black Moonlight Shizun',                'translated'),
			('Tensei Shoujo no Rirekisho',        'Tensei Shoujo no Rirekisho',                                   'translated'),
			('Master of Dungeon',                 'Master of Dungeon',                                            'oel'),
		]

		for titlecomponent, name, tl_type in titlemap:
			if titlecomponent.lower() in item['title'].lower():
				return buildReleaseMessageWithType(item, name, vol, chp, frag=frag, postfix=postfix, tl_type=tl_type)


	return False