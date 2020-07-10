def extractWwwAsianhobbyistCom(item):
	'''
	Parser for 'www.asianhobbyist.com'
	'''

	vol, chp, frag, postfix = extractVolChapterFragmentPostfix(item['title'])
	if not (chp or vol) or "preview" in item['title'].lower():
		return None
		
	if "Anime" in item['tags']:
		return None
	if "Articles" in item['tags']:
		return None
	if "L’Apprivoisement D’une Yandere" in item['tags']:
		return None

	tagmap = [
		('Boku wa Isekai',                                                                  'Boku wa Isekai de Fuyo Mahou to Shoukan Mahou wo Tenbin ni Kakeru',                           'translated'),
		('Traitor and Hero Party',                                                          'Traitor and Hero Party',                                                                      'translated'),
		('The God Slaying Hero and the Seven Covenants',                                    'The God Slaying Hero and the Seven Covenants',                                                'translated'),
		('First Hunter',                                                                    'The First Hunter',                                                                            'translated'),
		('Revolution of the 8th Class Mage',                                                'Revolution of the 8th Class Mage',                                                            'translated'),
		('The Villainess Is Being Doted on by the Crown Prince',                            'The Villainess Is Being Doted on by the Crown Prince',                                        'translated'),
		('The Lazy Swordmaster',                                                            'The Lazy Swordmaster',                                                                        'translated'),
		('My Pet Is a Holy Maiden',                                                         'My Pet Is a Holy Maiden',                                                                     'translated'),
		('I Will Quit the Entourage of the Villainess',                                     'I Will Quit the Entourage of the Villainess',                                                 'translated'),
		('The Archer of A Fictitious World',                                                'The Archer of A Fictitious World',                                                            'translated'),
		('The Spoilt Village Beauty',                                                       'The Spoilt Village Beauty',                                                                   'translated'),
		('Golden Word Master',                                                              'Golden Word Master',                                                                          'translated'),
		('Shadow Rogue',                                                                    'Shadow Rogue',                                                                                'translated'),
		('LV999 Villager',                                                                  'LV999 Villager',                                                                              'translated'),
		('Evil God Average',                                                                'Evil God Average',                                                                            'translated'),
		('Maou Ni',                                                                         'Maou ni Nattanode, Dungeon Tsukutte Jingai Musume to Honobono Suru',                          'translated'),
		('Uchi Musume',                                                                     'Uchi no Musume no Tame naraba, Ore wa Moshikashitara Maou mo Taoseru kamo Shirenai',          'translated'),
		('Botsuraku',                                                                       'Botsuraku Youtei Nanode, Kajishokunin wo Mezasu',                                             'translated'),
		('Akuya',                                                                           'Akuyaku Tensei Dakedo Doushite Kou Natta.',                                                   'translated'),
		('The Strong The Few Cultivators On Campus',                                        'The Strong The Few Cultivators On Campus',                                                    'translated'),
		('Magicraft Meister',                                                               'Magi Craft Meister',                                                                          'translated'),
		('A Tale of Two Phoenixes',                                                         'A Tale of Two Phoenixes',                                                                     'translated'),
		('The Taming of the Yandere',                                                       'The Taming of the Yandere',                                                                   'translated'),
		('Abyss Domination',                                                                'Abyss Domination',                                                                            'translated'),
		('Yuusha, Aruiwa Bakemono to Yobareta Shoujo',                                      'Yuusha, Aruiwa Bakemono to Yobareta Shoujo',                                                  'translated'),
		('The Manual of Duke\'s Daughter',                                                  'The Manual of Duke\'s Daughter',                                                              'translated'),
		('That Time I Got Reincarnated As A Slime',                                         'That Time I Got Reincarnated As A Slime',                                                     'translated'),
		('Every Day the Protagonist Wants to Capture Me',                                   'Every Day the Protagonist Wants to Capture Me',                                               'translated'),
		('kuro no maou',                                                                    'kuro no maou',                                                                                'translated'),
		('Me, Her, and the Ballistic Weaponry',                                             'Me, Her, and the Ballistic Weaponry',                                                         'translated'),
		('Hilarious pampered consort: Lord I will wait for your divorce',                   'Hilarious pampered consort: Lord I will wait for your divorce',                               'translated'),
		('Beastly Fēi that Go Against the Heaven: Coerced by the Huáng Shū',                'Beastly Fēi that Go Against the Heaven: Coerced by the Huáng Shū',                            'translated'),
		('One Man Army',                                                                    'One Man Army',                                                                                'translated'),
		('Rebirth Junior High School: The Exceling Top Student Goddess',                    'Rebirth Junior High School: The Exceling Top Student Goddess',                                'translated'),
		('Itai No Wa',                                                                      'Itai No Wa',                                                                                  'translated'),
		('Slime',                                                                           'Tensei Shitara Slime Datta Ken',                                                              'translated'),
		('Hero without Blood or Tear',                                                      'Hero without Blood or Tear',                                                                  'translated'),
		('The Magnificent Battle Records of a Former Noble Lady',                           'The Magnificent Battle Records of a Former Noble Lady',                                       'translated'),
		('Chiyu Mahou no Machigatta Tsukaikata ~Senjou wo Kakeru Kaifuku Youin~',           'Chiyu Mahou no Machigatta Tsukaikata ~Senjou wo Kakeru Kaifuku Youin~',                       'translated'),
		('The Daughter of the Albert House Wishes for Ruin',                                'The Daughter of the Albert House Wishes for Ruin',                                            'translated'),
		('The Black Demon King',                                                            'The Black Demon King',                                                                        'translated'),
		('Spice of Life',                                                                   'Spice of Life',                                                                               'translated'),
		('Unexpected Marriage',                                                             'Unexpected Marriage',                                                                         'translated'),
		('Heavenly Star',                                                                   'Heavenly Star',                                                                               'translated'),
		('Overlord of Blood and Iron',                                                      'Overlord of Blood and Iron',                                                                  'translated'),
		('Zhu Xian',                                                                        'Zhu Xian',                                                                                    'translated'),
		('Awakening',                                                                       'Awakening',                                                                                   'translated'),
		('I Somehow Got Strong By Raising Skills Related To Farming',                       'I Somehow Got Strong By Raising Skills Related To Farming',                                   'translated'),
		('I\'m a Villager So What?',                                                        'I\'m a Villager So What?',                                                                    'translated'),
		('Big Landlord',                                                                    'Big Landlord',                                                                                'translated'),
		('Common Sense of a Duke\'s Daughter',                                              'Common Sense of a Duke\'s Daughter',                                                          'translated'),
		('The Traitor of the Hero Party',                                                   'The Traitor of the Hero Party',                                                               'translated'),
		('Hiki Neet',                                                                       '10 nen goshi no HikiNiito o Yamete Gaishutsushitara Jitaku goto Isekai ni Ten\'ishiteta',     'translated'),
		('100 cheats',                                                                      'Because There Were 100 Goddesses in Charge of Reincarnation, I Received 100 Cheat Skills',    'translated'),
		('Even Posing as a Hero is Easy',                                                   'Yuusha no Furi mo Raku Janai–Riyuu? Ore ga Kami dakara–',                                     'translated'),
		('Large Tit Stepdaughter',                                                          'What’s Wrong With Liking My Busty Adopted Daughter',                                          'translated'),
		('Busty Adopted Daughter',                                                          'What’s Wrong With Liking My Busty Adopted Daughter',                                          'translated'),
		('Virgin Demon King',                                                               '400 Years Old Virgin Demon King',                                                             'translated'),
		('400 Year Old Virgin Demon King',                                                  '400 Years Old Virgin Demon King',                                                             'translated'),
		('Dancer In The Shadow',                                                            'Dancer In The Shadow',                                                                        'translated'),
		('Reformation of the Checkmated Reincarnated Feudal Lord',                          'Reformation of the Checkmated Reincarnated Feudal Lord',                                      'translated'),
		('History\'s Strongest Manager',                                                    'History\'s Strongest Manager',                                                                'translated'),
		('Black Belly Wife',                                                                'Black Belly Wife',                                                                            'translated'),
		('I Said Make My Abilities Average!',                                               'I Said Make My Abilities Average!',                                                           'translated'),
		('God of Cooking',                                                                  'God of Cooking',                                                                              'translated'),
		('The Reincarnated Vampire Wants an Afternoon Nap',                                 'The Reincarnated Vampire Wants an Afternoon Nap',                                             'translated'),
		('Possessing Nothing',                                                              'Possessing Nothing',                                                                          'translated'),
		('God-level Bodyguard in the City',                                                 'God-level Bodyguard in the City',                                                             'translated'),
		('I am an alchemist. I have discarded self-restraint in the trash',                 'I am an alchemist. I have discarded self-restraint in the trash',                             'translated'),
		('The Ability to Make Town!? ~Let’s Make a Japanese Town in Different World~',      'The Ability to Make Town!? ~Let’s Make a Japanese Town in Different World~',                  'translated'),
		('Lovable Package',                                                                 'Lovable Package',                                                                             'translated'),
		('God of Thunder',                                                                  'God of Thunder',                                                                              'translated'),
		('Max Level Newbie',                                                                'Max Level Newbie',                                                                            'translated'),
		('Because I’m a Weapon Shop Uncle',                                                 'Because I\'m a Weapon Shop Uncle',                                                            'translated'),
		('Game Market 1983',                                                                'Game Market 1983',                                                                            'translated'),
		('My Castle My Castellian',                                                         'My Castle My Castellian',                                                                     'translated'),
		('Oda',                                                                             'Mysterious Job Called Oda Nobunaga',                                                          'translated'),
		('Defense Build',                                                                   'I hate being in pain, so I think I’ll make a full defense build.',                            'translated'),
		('Return of the 8th Class Mage',                                                    'Return of the 8th Class Mage',                                                                'translated'),
		('di daughter’s rebirth: sheng shi wang fei',                                       'di daughter’s rebirth: sheng shi wang fei',                                                   'translated'),
		('rebirth: noble woman, poisonous concubine',                                       'rebirth: noble woman, poisonous concubine',                                                   'translated'),
		('Thousand Face Demonic Concubine',                                                 'Thousand Face Demonic Concubine',                                                             'translated'),
		('how do i fix it?',                                                                'i’ve led the villain astray',                                                                 'translated'),
		('i’ve led the villain astray',                                                     'i’ve led the villain astray',                                                                 'translated'),
		('the tale of the ghost eyes',                                                      'the tale of the ghost eyes',                                                                  'translated'),
		('rebirth of the national male god',                                                'rebirth of the national male god',                                                            'translated'),
		('pulling together a villain reformation strategy',                                 'pulling together a villain reformation strategy',                                             'translated'),
		('Assassin Landlord & Beauty Tenants',                                              'Assassin Landlord & Beauty Tenants',                                                          'translated'),
		('My Entire Class Was Summoned to Another World Except for Me',                     'My Entire Class Was Summoned to Another World Except for Me',                                 'translated'),
		('bringing along a ball and hiding from foreign devils',                            'bringing along a ball and hiding from foreign devils',                                        'translated'),
		('get lost! i don’t have a traitorous disciple like you',                           'get lost! i don’t have a traitorous disciple like you',                                       'translated'),
		('I Am An NPC',                                                                     'I Am An NPC',                                                                                 'translated'),
		('the wizard of the tower',                                                         'the wizard of the tower',                                                                     'translated'),
		('The Strange Adventure of a Broke Mercenary',                                      'The Strange Adventure of a Broke Mercenary',                                                  'translated'),
		('a mistaken marriage match: pursuit of murderer in liao yue',                      'a mistaken marriage match: pursuit of murderer in liao yue',                                  'translated'),
		('my c.e.o wife',                                                                   'my c.e.o wife',                                                                               'translated'),
		('Strongest Naruto System',                                                         'Strongest Naruto System',                                                                     'translated'),
		('Instant Death',                                                                   'Instant Death',                                                                               'translated'),
		('haunted duke’s daughter',                                                         'haunted duke’s daughter',                                                                     'translated'),
		('Arena',                                                                           'Arena',                                                                                       'translated'),
		('MEMORIZE',                                                                        'M E M O R I Z E',                                                                             'translated'),
		('fanning the flames of war!',                                                      'fanning the flames of war!',                                                                  'translated'),
		('I’ve Led the Villain Astray, How Do I Fix It?',                                   'I’ve Led the Villain Astray, How Do I Fix It?',                                               'translated'),
		('the lover’s prattle',                                                             'the lover’s prattle',                                                                         'translated'),
		('reborn only to love you again',                                                   'reborn only to love you again',                                                               'translated'),
		('Counterattack of a White Lotus that was Reborn into an Apocalypse',               'Counterattack of a White Lotus that was Reborn into an Apocalypse',                           'translated'),
		('More Than A Few Blessings',                                                       'More Than A Few Blessings',                                                                   'translated'),
		('Online Game: Evil Dragon Against The Heaven',                                     'Online Game: Evil Dragon Against The Heaven',                                                 'translated'),
		('The King of the Battlefield',                                                     'The King of the Battlefield',                                                                 'translated'),
		('Golden Assistant',                                                                'Golden Assistant',                                                                            'translated'),
		('Rebirth of the Rich and Wealthy',                                                 'Rebirth of the Rich and Wealthy',                                                             'translated'),
		('I Decided to Not Compete and Quietly Create Dolls Instead',                       'I Decided to Not Compete and Quietly Create Dolls Instead',                                   'translated'),
		('Otherworld Nation Founding Chronicles',                                           'Otherworld Nation Founding Chronicles',                                                       'translated'),
		('otoko nara ikkokuichijou no aruji o mezasa nakya',                                'otoko nara ikkokuichijou no aruji o mezasa nakya',                                            'translated'),
		('Being Able to Edit Skills in Another World, I Gained OP Waifus',                  'Being Able to Edit Skills in Another World, I Gained OP Waifus',                              'translated'),
		('Boku wa Isekai de Fuyo Mahou to Shoukan Mahou wo Tenbin ni Kakeru',               'Boku wa Isekai de Fuyo Mahou to Shoukan Mahou wo Tenbin ni Kakeru',                           'translated'),
		('Other World’s Monster Breeder',                                                   'Other World’s Monster Breeder',                                                               'translated'),
		('invincible saint ~salaryman',                                                     'Invincible Saint ~Salaryman, the Path I Walk to Survive in This Other World~',                'translated'),
		('qingge',                                                                          'qingge',                                                                                      'translated'),
		('Magi Craft Meister',                                                              'Magi Craft Meister',                                                                          'translated'),
		('albert ke no reijou wa botsuraku wo go shomou desu',                              'albert ke no reijou wa botsuraku wo go shomou desu',                                          'translated'),
		('sairin yuusha no fukushuu hanashi',                                               'sairin yuusha no fukushuu hanashi',                                                           'translated'),
		('kyuuketsu hime wa barairo no yume o miru',                                        'kyuuketsu hime wa barairo no yume o miru',                                                    'translated'),
		('Boundary Labyrinth and the Foreign Magician',                                     'Boundary Labyrinth and the Foreign Magician',                                                 'translated'),
		('let’s be an adventurer! ~defeating dungeons with a skill board~',                 'let’s be an adventurer! ~defeating dungeons with a skill board~',                             'translated'),
		('tilea’s worries',                                                                 'Tilea no Nayamigoto',                                                                         'translated'),
		('kaleidoscope of death',                                                           'kaleidoscope of death',                                                                       'translated'),
		('Magi’s Grandson',                                                                 'Magi’s Grandson',                                                                             'translated'),
		('the man standing on top of the food chain',                                       'the man standing on top of the food chain',                                                   'translated'),
		('Shinka no Mi',                                                                    'Shinka no Mi',                                                                                'translated'),
		('let’s be an adventurer! ~defeating dungeons with a skill board',                  'let’s be an adventurer! ~defeating dungeons with a skill board',                              'translated'),
		('chinese almanac master',                                                          'chinese almanac master',                                                                      'translated'),
		('Helping with Adventurer Party Management',                                        'Helping with Adventurer Party Management',                                                    'translated'),
		('i’m scattering iq to the protagonist',                                            'i’m scattering iq to the protagonist',                                                        'translated'),
		('Blade Online',                                                                    'Blade Online',                                                                                'translated'),
		('Real Cheat Online',                                                               'Real Cheat Online',                                                                           'translated'),
		('endo and kobayashi’s live commentary on the villainess',                          'endo and kobayashi’s live commentary on the villainess',                                      'translated'),
		('the s-classes that i raised',                                                     'the s-classes that i raised',                                                                 'translated'),
		('Green Skin',                                                                      'Green Skin',                                                                                  'translated'),
		('Chu Wang Fei',                                                                    'Chu Wang Fei',                                                                                'translated'),
		('my castle my castellan',                                                          'my castle my castellan',                                                                      'translated'),
		('Waiting For You Online',                                                          'Waiting For You Online',                                                                      'translated'),
		('Liu Yao: The Revitalization of Fuyao Sect',                                       'Liu Yao: The Revitalization of Fuyao Sect',                                                   'translated'),
		('The Simple Life of Killing Demons',                                               'The Simple Life of Killing Demons',                                                           'translated'),
		('frontiers ~chronicles of bucket-san’s detailed pioneering~',                      'frontiers ~chronicles of bucket-san’s detailed pioneering~',                                  'translated'),
	]

	for tagname, name, tl_type in tagmap:
		if tagname in item['tags']:
			return buildReleaseMessageWithType(item, name, vol, chp, frag=frag, postfix=postfix, tl_type=tl_type)


	titlemap = [
		('Because There Were 100 Goddesses ',                   'Because There Were 100 Goddesses in Charge of Reincarnation, I Received 100 Cheat Skills',    'translated'),
		('Botsuraku Youtei Volume',                             'Botsuraku Youtei Nanode, Kajishokunin wo Mezasu',                                             'translated'),
		('Reincarnated into a Werewolf',                        'Jinrou e no Tensei, Maou no Fukukan',                                                         'translated'),
		('Reincarnated Into Werewolf ',                         'Jinrou e no Tensei, Maou no Fukukan',                                                         'translated'),
		('Uchi no Musume no Tame naraba',                       'Uchi no Musume no Tame Naraba, Ore Moshikashitara Maou mo Taoserukamo Shirenai.',             'translated'),
		('Botsuraku Youtei Volume',                             'Botsuraku Youtei Nanode, Kajishokunin wo Mezasu',                                             'translated'),
		('Devouring The Heavens',                               'Devouring The Heavens',                                                                       'translated'),
		('The Taming of the Yandere',                           'The Taming of the Yandere',                                                                   'translated'),
		('Maou Ni',                                             'Maou ni Nattanode, Dungeon Tsukutte Jingai Musume to Honobono Suru',                          'translated'),
		('The Strong The Few Cultivators On Campus',            'The Strong The Few Cultivators On Campus',                                                    'translated'),
		('The Strong, The Few, True Cultivators on Campus',     'The Strong The Few Cultivators On Campus',                                                    'translated'),
		('Evolution Theory of the Hunter',                      'Evolution Theory of the Hunter',                                                              'translated'),
		('Beast Piercing The Heavens',                          'Beast Piercing The Heavens',                                                                  'translated'),
		('Tower of Karma',                                      'Tower of Karma',                                                                              'translated'),
		('400 Year Old Virgin Demon King',                      '400 Year Old Virgin Demon King',                                                              'translated'),
		('Expecting to Fall into Ruin Volume',                  'Botsuraku Youtei Nanode, Kajishokunin wo Mezasu',                                             'translated'),
		('Genius Sword Immortal',                               'Genius Sword Immortal',                                                                       'translated'),
		('Evil God Average',                                    'Evil God Average',                                                                            'translated'),
		('The God Slaying Hero',                                'The God Slaying Hero And The Seven Covenants',                                                'translated'),
		('First Hunter',                                        'The First Hunter',                                                                            'translated'),
		('Shadow Rogue',                                        'Shadow Rogue',                                                                                'translated'),
		('Black Haired Knight',                                 'Black Haired Knight',                                                                         'translated'),
		('The Lazy Swordmaster',                                'The Lazy Swordmaster',                                                                        'translated'),
		('Uchi Musume',                                         'Uchi Musume',                                                                                 'translated'),
		('Hero without Blood or Tear',                          'Hero without Blood or Tear',                                                                  'translated'),
		
	]

	for titlecomponent, name, tl_type in titlemap:
		if titlecomponent.lower() in item['title'].lower():
			return buildReleaseMessageWithType(item, name, vol, chp, frag=frag, postfix=postfix, tl_type=tl_type)

		
	return False