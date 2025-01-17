
import code
import ast
import re
import json
import datetime

from sqlalchemy import Table

from sqlalchemy import Column
from sqlalchemy import BigInteger
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import JSONB

# from  sqlalchemy.sql.expression import func
# from citext import CIText

from sqlalchemy.ext.associationproxy import association_proxy


import common.db_base
import common.db_types

import cachetools
import citext

from common.db_engine import get_db_session

from WebMirror.OutputFilters.util.MessageConstructors import buildReleaseDeleteMessageWithType
from WebMirror.OutputFilters.util.MessageConstructors import buildReleaseMessageWithType
from WebMirror.OutputFilters.util.TitleParsers import extractChapterVol
from WebMirror.OutputFilters.util.TitleParsers import extractChapterVolFragment
from WebMirror.OutputFilters.util.TitleParsers import extractVolChapterFragmentPostfix


feed_tags_link = Table(
		'feed_tags_link', common.db_base.Base.metadata,
		Column('releases_id', BigInteger, ForeignKey('feed_pages.id'), nullable=False),
		Column('tags_id',     BigInteger, ForeignKey('feed_tags.id'),     nullable=False),
		PrimaryKeyConstraint('releases_id', 'tags_id')
	)

feed_author_link = Table(
		'feed_authors_link', common.db_base.Base.metadata,
		Column('releases_id', BigInteger, ForeignKey('feed_pages.id'), nullable=False),
		Column('author_id',   BigInteger, ForeignKey('feed_author.id'),     nullable=False),
		PrimaryKeyConstraint('releases_id', 'author_id')
	)


class Tags(common.db_base.Base):
	__tablename__ = 'feed_tags'
	id          = Column(BigInteger, primary_key=True)
	tag         = Column(citext.CIText(), nullable=False, index=True)

	__table_args__ = (
		UniqueConstraint('tag'),
		)


class Author(common.db_base.Base):
	__tablename__ = 'feed_author'
	id          = Column(BigInteger, primary_key=True)
	author      = Column(citext.CIText(), nullable=False, index=True)

	__table_args__ = (
		UniqueConstraint('author'),
		)


def tag_creator(tag):
	tmp = get_db_session().query(Tags) \
		.filter(Tags.tag == tag)    \
		.scalar()
	if tmp:
		return tmp

	return Tags(tag=tag)

def author_creator(author):
	tmp = get_db_session().query(Author)    \
		.filter(Author.author == author) \
		.scalar()
	if tmp:
		return tmp
	return Author(author=author)


class RssFeedPost(common.db_base.Base):
	__tablename__ = 'feed_pages'

	id          = Column(BigInteger, primary_key=True)

	type        = Column(common.db_types.itemtype_enum, default='unknown', index=True)

	feed_id     = Column(BigInteger, ForeignKey('rss_parser_funcs.id'), index = True, nullable=False)


	contenturl   = Column(Text, nullable=False, index=True)
	contentid    = Column(Text, nullable=False, index=True, unique=True)

	title        = Column(Text)
	contents     = Column(Text)

	updated      = Column(DateTime, default=datetime.datetime.min)
	published    = Column(DateTime, nullable=False)

	tag_rel       = relationship('Tags',       secondary=feed_tags_link,   backref='feed_pages')
	author_rel    = relationship('Author',     secondary=feed_author_link, backref='feed_pages')

	tags          = association_proxy('tag_rel',      'tag',       creator=tag_creator)
	author        = association_proxy('author_rel',   'author',    creator=author_creator)


##########################################################################################
##########################################################################################
##########################################################################################
##########################################################################################

QIDIAN_META_CACHE = cachetools.TTLCache(maxsize=5000, ttl=60 * 5)

class QidianFeedPostMeta(common.db_base.Base):
	__tablename__ = 'feed_post_meta'

	id          = Column(BigInteger, primary_key=True)

	contentid    = Column(Text, nullable=False, index=True, unique=True)
	meta         = Column(JSONB)


def get_feed_article_meta(feedid):
	global QIDIAN_META_CACHE
	if feedid in QIDIAN_META_CACHE:
		return QIDIAN_META_CACHE[feedid]

	sess = get_db_session(flask_sess_if_possible=False)
	have = sess.query(QidianFeedPostMeta).filter(QidianFeedPostMeta.contentid == feedid).scalar()
	if have:
		ret = have.meta
	else:
		ret = {}

	sess.commit()

	try:
		QIDIAN_META_CACHE[feedid] = ret
	except KeyError:
		QIDIAN_META_CACHE = cachetools.TTLCache(maxsize=5000, ttl=60 * 5)
		QIDIAN_META_CACHE[feedid] = ret


	return ret

def set_feed_article_meta(feedid, new_data):
	global QIDIAN_META_CACHE
	# if feedid in QIDIAN_META_CACHE:
	# 	if QIDIAN_META_CACHE[feedid] == new_data:
	# 		return

	sess = get_db_session(flask_sess_if_possible=False)
	have = sess.query(QidianFeedPostMeta).filter(QidianFeedPostMeta.contentid == feedid).scalar()
	if have:
		if have.meta != new_data:
			print("Updating item: ", have, have.contentid)
			print("	old -> ", have.meta)
			print("	new -> ", new_data)
			have.meta = new_data
		else:
			print("Item has not changed. Nothing to do!")
	else:
		print("New item: ", feedid, new_data)
		new = QidianFeedPostMeta(
			contentid = feedid,
			meta      = new_data,
			)
		sess.add(new)

	sess.commit()

	try:
		QIDIAN_META_CACHE[feedid] = new_data
	except KeyError:
		QIDIAN_META_CACHE = cachetools.TTLCache(maxsize=5000, ttl=60 * 5)
		QIDIAN_META_CACHE[feedid] = new_data

	return


##########################################################################################
##########################################################################################
##########################################################################################
##########################################################################################


# LRU Cache of function text -> function objects.
PARSED_FUNCTION_CACHE = cachetools.LRUCache(maxsize=5000)

class RssFeedUrlMapper(common.db_base.Base):
	__versioned__ = {}

	__tablename__     = 'rss_parser_feed_name_lut'
	name              = 'rss_parser_feed_name_lut'

	id                = Column(BigInteger, primary_key = True, index = True)
	feed_netloc       = Column(Text, nullable = False, index = True)

	# Most feeds are defined by netloc, so we have to allow that, at least untill the first feed scrape.
	feed_url          = Column(Text, nullable = True, index = True)
	feed_id           = Column(BigInteger, ForeignKey('rss_parser_funcs.id'), nullable = False, index = True)



	__table_args__ = (
		UniqueConstraint('feed_netloc', 'feed_id'),
		)


def str_to_ast(instr, name):
	print("Compiling function from DB (str_to_ast) for '%s'" % name)

	# So compile needs a trailing newline to properly terminate (or something?)
	# anyways, stick some extra on to be safe.
	func_str = instr+"\n\n"

	func_container = ast.parse(func_str, "<db_for_<{}>>".format(name), "exec")
	return func_container

def str_to_function(instr, name):
	instr = instr.strip()

	# Use the loaded function when possible.
	if instr in PARSED_FUNCTION_CACHE:
		print("Using LRU cached function (%s items)" % len(PARSED_FUNCTION_CACHE))
		return PARSED_FUNCTION_CACHE[instr]

	print("Compiling function from DB (str_to_function) for '%s'" % name)

	# So compile needs a trailing newline to properly terminate (or something?)
	# anyways, stick some extra on to be safe.
	func_str = instr+"\n\n"

	func_container = compile(func_str, "<db_for_<{}>>".format(name), "exec")

	# These keys determine what modules are available to the database functions.
	# If a database function needs a library, it has to be imported here!
	scope = {
		"get_feed_article_meta"             : get_feed_article_meta,
		"set_feed_article_meta"             : set_feed_article_meta,
		"buildReleaseMessageWithType"       : buildReleaseMessageWithType,
		"buildReleaseDeleteMessageWithType" : buildReleaseDeleteMessageWithType,
		"extractChapterVol"                 : extractChapterVol,
		"extractChapterVolFragment"         : extractChapterVolFragment,
		"extractVolChapterFragmentPostfix"  : extractVolChapterFragmentPostfix,
		"re"                                : re,
		"json"                              : json,
	}
	popkeys = set(scope.keys())
	popkeys.add("__builtins__")

	exec(func_container, scope)

	func = [val for key, val in scope.items() if not key in popkeys]

	# Check we have just one object in the return, and that it's callable
	assert len(func) == 1
	assert callable(func[0])

	# Push processed function into the cache
	PARSED_FUNCTION_CACHE[instr] = func[0]

	return func[0]

class RssFeedEntry(common.db_base.Base):
	__versioned__ = {}

	__tablename__     = 'rss_parser_funcs'
	name              = 'rss_parser_funcs'

	id                = Column(BigInteger, primary_key = True, index = True)
	version           = Column(Integer, default='0')

	feed_name         = Column(Text, nullable = False, index = True, unique = True)

	enabled           = Column(Boolean, default=True)

	func              = Column(Text)

	urls              = relationship('RssFeedUrlMapper', backref='feed_entry')
	releases          = relationship('RssFeedPost',      backref='feed_entry')


	last_changed      = Column(DateTime, nullable=False)

	__loaded_func       = None

	def _get_ast(self):
		return str_to_ast(self.func, self.feed_name)

	def get_func(self):
		self.__loaded_func = str_to_function(self.func, self.feed_name)
		return self.__loaded_func

