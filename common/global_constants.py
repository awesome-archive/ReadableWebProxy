
GLOBAL_BAD_URLS = [
			'//mail.google.com',
			'/comments/feed/',
			'/embed?',
			'/osd.xml',
			'/page/page/',
			'/wp-json/',
			'/wp-login.php',
			'/xmlrpc.php',
			'?openidserver=1',
			'a.wikia-beacon.com',
			'accounts.google.com',
			'add.my.yahoo.com',
			'addtoany.com',
			'b.scorecardresearch.com',
			'delicious.com',
			'digg.com',
			'edit.yahoo.com',
			'facebook.com',
			'fw.adsafeprotected.com',
			'getnewsoft.pleaseupdatesafesystems4younow.online',
			'pleaseupdatesafesystems4younow.online',
			'tpc.googlesyndication.com',
			'jp-g2.gumgum.com',
			'fbcdn-',
			'bnc.lt',
			'www.atspace.com',
			'feeds.wordpress.com',
			'www.cpm20.com',
			'gprofiles.js',
			'javascript:void',
			'wordfence_syncAttackData',
			'netvibes.com',
			'newsgator.com',
			'paypal.com',
			'pixel.wp.com',
			'public-api.wordpress.com',
			'r-login.wordpress.com',
			'maintenance.volarenovels.com',
			'stumbleupon.com',
			'technorati.com',
			'topwebfiction.com',
			'twitter.com',
			'twitter.com/intent/',
			'wretch.cc',
			'ws-na.amazon-adsystem.com',
			'www.addtoany.com'
			'www.pinterest.com/pin/',
			'www.wattpad.com/login?',
			'www.tumblr.com/reblog/',
			'#comment-form',
			'www.paypalobjects.com',
			'attorneyking.pro',    # Wat
			'.temp.domains',
			'box5113.temp.domains',
			'attorneykings.gdn',
			's2ba7sw2d.us-02.live-paas.net',

			# Tumblr can seriously go fuck itself with a rusty stake
			'tumblr.com/widgets/',
			'www.tumblr.com/login',
			'://tumblr.com',
			'&share=tumblr',
			'/wp-content/plugins/',
			'/wp-content/themes/',
			'/wp-json/oembed/',
			'tracking.feedpress.it',
			# At least one site (booksie) is serving the favicon with a mime-type
			# of "text/plain", which then confuses the absolute crap out of the
			# mime-type dispatcher.
			# Since I'm not re-serving favicons anyways, just do not fetch them ever.
			'favicon.ico',
			# Try to not scrape inline images
			';base64,',
			"www.fashionmodeldirectory.com",
			"www.watchingprivatepractice.com",
			"Ebonyimages.jupiterimages.com",
			# More garbage issues.
			'"https',
			'#comment-',
			'/oembed/1.0/',
			'&share=',
			'replytocom=',
			'?feed=rss2&page_id',
			'?share=tumblr',
			'?share=facebook',
			'chasingadreamtranslations.com/?fp=',
			# NFI where /this/ came from
			'www.miforcampuspolice.com',
			'attorneyking.pro',
			'webkingsga.us',
			'www.quantcast.com',
			'mailto:',
			'javascript:popupWindow(',
			'en.blog.wordpress.com',
			'counter.yadro.ru',
			'box5315.temp.domains',
			'thewhizmarketing.com',
			'/js/js/',
			'/css/css/',
			'/images/images/',
			'ref=dp_brlad_entry',
			'https:/www.',
			'tumblr.com/oembed/1.0?',
			'/wp-includes/js/',
			# Oh god fuck discord so much.
			'discord1-1494780898_lrg.png',
			'discord_partner_badge_black.png',
			'discord.png',
			# Bought by asshole squatters
			'app3.letitbefaster.world',
			'app4.letitbefaster.world',
			'install.shopping-day.com',
			'pastebin.com',
			'ww1.absurdtl.com',
			'ww1.avertranslation.org',
			'ww1.catingham-palace.com',
			'ww1.chiakunloong.com',
			'ww1.circustranslations.com',
			'ww1.grimdarkztranslations.com',
			'ww1.helidwarf.com',
			'ww1.kudalakorn.com',
			'ww12.circustranslations.com',
			'ww12.nepustation.com',
			'ww12.pegasusfarts.com',
			'ww12.shomotsu.com',
			'ww12.steadytranslation.com',
			'ww3.grimdarkztranslations.com',
			'ww38.asuratales.com',
			'ww4.grimdarkztranslations.com',
			'www.dropcatch.com',
			'www.fictionpress.com',
			'www.google.com',
			'www.hugedomains.com',
			'www.wattpad.com',
			'www1.trungtnguyen123.org',
			'ww2.steadytranslation.com',
			'ww1.pegasusfarts.com',
			'ww1.myotterspace.com',
			'ww12.kudalakorn.com',
			'ww12.myotterspace.com',
			'ww1.pegasusfarts.com',
			'ww12.kudalakorn.com',
			'ww12.nepustation.com',
			'ww12.pegasusfarts.com',
			'ww1.fictiongrill.com',
			'ww12.fictiongrill.com',

			'www.swoopdeal.com',
			'www.hyfind.de'
			'https:/68.media.tumblr.com',
			'https%3A/68.media.tumblr.com',
			'/68.media.tumblr.com',
			# Wat
			'fierydragonbreath.tumblr.com',
			# Spanish. I don't want to waste disk space on this.
			'novelasymangasjpo.blogspot.com',
			# Seems to be just anime images.
			'trashbunny.tumblr.com',
			'turtleme.me/feed/includes/',
			'turtleme.me/feed/images/',
			'turtleme.me/includes/',
			'turtleme.me/images/products/includes/',
			'pathoftranslation.com/?ga=',
			'//en.wordpress.com/'
			# Lawl
			'/<?php',
			# Fuck that one domain squatter in particular.
			'.com/?fp=',
			'www.facebook.com',
			'www.pinterest.com',  # fucking hell, really?
			'www.linkedin.com',

			'www.nifty.com',
			'tag:blogger.com',
			'http:/s',
			'/comments/default',
			'#comment-',
			'/comment-',
			'/data/atom/?itemid=',
			'Special:UserLogin',
			'&returnto=',
			'Special:WhatLinksHere',
			'/User:',
			'.cfm?fp=',
	]


GLOBAL_DECOMPOSE_BEFORE = [
			{'name'     : 'likes-master'},  # Bullshit sharing widgets
			{'id'       : 'jp-post-flair'},
			{'class'    : 'post-share-buttons'},
			#{'class'    : 'commentlist'},  # Scrub out the comments so we don't try to fetch links from them
			#{'class'    : 'comments'},
			#{'id'       : 'comments'},
		]

GLOBAL_DECOMPOSE_AFTER = []


RSS_SKIP_FILTER = [
	"www.baka-tsuki.org",
	"re-monster.wikia.com",
	'inmydaydreams.com',
	'www.fanfiction.net',
	'www.booksie.com',
	'www.booksiesilk.com',
	'www.fictionpress.com',
	'storiesonline.net',
	'www.fictionmania.tv',
	'www.bestories.net',
	'www.tgstorytime.com',
	'www.nifty.org',
	'www.literotica.com',
	'pokegirls.org',
	'www.asstr.org',
	'www.mcstories.com',
	'www.novelupdates.com',
	'40pics.com',
	'#comment-',
	'?showComment=',

	# Spanish retranslators.
	'inmortallegends.blogspot.com.es',
	'dollstranslations.blogspot.com.es',
	'slaverod.com'
	'spanishtraslation.wordpress.com',
	'noveligeras.wordpress.com',
	'odiseafinal.blogspot.com',

	# WTF is this even from?
	'www.miforcampuspolice.com',

	'tracking.feedpress.it',
	'en.blog.wordpress.com',

	'youkojitsu.wordpress.com',  # Gone

	# The irony of a writing fiction about the bible is apparently
	# lost on this guy.
	'whathasjesusdone.wordpress.com',

]


# Some sites have gone down or are now squatters. Mask them off.
NU_NEW_MASK_NETLOCS = [
			'en.wordpress.com',
			'endofdays42.ph.tn',
			'endofdays42.000webhostapp.com',
			'host307.hostmonster.com',
			'plus.google.com',

			'thundertranslations.com',
			'ww1.thundertranslations.com',
			'ww12.thundertranslations.com',
			'ww2.thundertranslations.com',

			'hugginglovetranslations.heliohost.org',
			'suspendeddomain.org',
			'www.facebook.com',
			'www.testing.wuxiaworld.com',

			'www.patreon.com',
			'wordpress.com',
			'forum.gravitytales.com',
			'www.wangkaiinternational.com',    # Some garbage korean soap opera actor's website?

			'drive.google.com',
			'gakno.com.mx',          # Mexican food manufacturer?

			'kitakamiooi.com',   # Redirects to www.kitakamiooi.com
			'kanojo.eu',

			'www.tumblr.com',

			# Fucking mobile shit.
			'm.wuxiaworld.com',
			'm.xianxiaworld.net',
			'm.webnovel.com',

			# In the LUT already
			'catatopatch.wixsite.com',
			'kitsune.club',   # Also failing DNS resolution
			'uncommittedtranslations.bravesites.com',

			'www.optranslations.net',  # Ded
			'steadytranslation.com',
			'translatinotaku.ml',
			'www.worldofwatermelons.com',
			'ww5.worldofwatermelons.com',

			# Manga site?
			'ckmscans.halofight.com',

			"www1.faktranslations.com",  # Bought by a domain squatter
			"ww1.steadytranslation.com", # ditto
			'box479.bluehost.com',       # Site error thing.

			'jianghuwanderer.com',
			'www.failtranslations.xyz',
			'jpierce.peopleshostvps.com',
			'localhost',
			'mygirlfriendisazombiechapter169',
			'3619.furust.com',
			'449.furust.com',

			'forums.lolscans.com',
			'arestiny.com',
			'kousato106.wix.com',

			'medium.com',
			'ttps',
			'wp.me',
			'www.blogger.com',
			'webnovel.com',
			'www.hostinger.co.uk',

			'rtranslation.home.blog',
			'retranslationsx.home.blog',

			# Some extnu leaked through.
			'www.novelupdates.com',

			# now 404
			'bluedreams99.wixsite.com',
			'bumtranslations.weebly.com',
			'elyssiamc.com',
			'forum.babelchain.org',
			'ilovecandies123.simplesite.com',
			'ilover18novel.com',
			'lp.supergaminator.com',
			'myemtranslations.blogspot.com',
			'www.alphapolis.co',
			'www.muabeyond.com',
			'www.weebly.com',


		]



RSS_TITLE_FILTER = [
	"by: ",
	"comments on: ",
	"comment on: ",
	"comment on ",
]


# Goooooo FUCK YOURSELF
GLOBAL_INLINE_BULLSHIT = [
			"Read the original on https://dao.ist",
			"Property of Fantasy-Books.live | outside of it, it is stolen.",
			"This translation is property of Infinite Novel Translations.",
			"This translation is property of Infinite NovelTranslations.",
			"If you read this anywhere but at Infinite Novel Translations, you are reading a stolen translation.",
			"&lt;Blank&gt;",
			"&lt;space&gt;",
			"<Blank>",
			"<Blank>",
			"please read only translator’s websitewww.novitranslation.com",
			"please read only translator’s website www.novitranslation.com",
			"Please do not host elsewhere but MBC and Yumeabyss",
			'Original and most updated translations are from volaretranslations.',
			'Please support the translator for Wild Consort by reading on volarenovels!',
			'Original and most updated translations are from volaretranslations.',
			'Original and most updated translations are from volaretranslations.',
			"&lt;StarveCleric&gt;",
			'(trytranslations.com at your service!)',
			'Please do not host elsewhere but volare and Yumeabyss',
			'[Follow the latest chapter at wuxiadream.com]',

			'I slid my penis inside her. She squirmed a bit but YOU SICK FUCK STOP STEALING MY TRANSLATIONS',   # siiiiigh
			'I kissed her sweet anus once more before leaving',   # siiiiiiiiiiiiigh

			'(Watermark: read this translation only at shinku. xiaoxiaonovels.com)',
			"<TLN: If you're reading this novel at any other site than Sousetsuka.com you might be reading an unedited, uncorrected version of the novel.>",

			'Original and most updated translations are from volare. If read elsewhere, this chapter has been stolen. Please stop supporting theft.',
			'*******If you are reading this on a place other than rinkagetranslation.com, this chapter has been stolen and is neither the most recent or complete chapter.*******',
			'*******Read the chapters at rinkagetranslation.com. The chapters for this series will NOT be posted anywhere else other than on that site itself. If you are reading this from somewhere else then this is chapter has been stolen.*******',
			'If you are reading this on a place other than rinkagetranslation.com, this chapter has been stolen and is neither the most recent or complete chapter.',

			"Read The Lazy Swordmaster first on Lightnovelbastion.com (If you're reading this elsewhere, it has been stolen)",
			"Read The Lazy Swordmaster on Lightnovelbastion.com",

			"Property of © Fantasy-Books.live; outside of it, it is stolen.",
			'This is translated at nakimushitl.wordpress.com, please don’t post elsewhere.',
			'Please don’t post elsewhere.',
			'translated at nakimushitl.wordpress.com',
			'This translation is only hosted on bcatranslation',
			'Come Read it at DarkCirclesTranslations.com instead',
			'Read-only at SHMTranslations.com',
			'Read at SHMTranslations.com',
			'SHMTranslations.com',
			'Please support the translator by reading at shmtranslations.com',
			'Read at SHMTranslations dot com',
			'This chapter is translated by Convallaria’s Library (www.convallariaslibrary.com), so please continue to read there. Drop some comments to show your support over there. If you are seeing this, then that means you’re reading from another site that simply stole our translation, and you will keep seeing this message a few times.',

			'(Thank you for reading at bayabuscotranslation.com)',
			'(Ele note: Follow Supreme Tentacle’s site at Cardboard Translations. Top tier stuff.)',
			'HELP! This aggregator site is making me manually copy and paste chapters! this is slavery! call the police!',
			'Read the original translation in Wang Mama Read.',
]
