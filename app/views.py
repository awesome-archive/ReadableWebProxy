

# from guess_language import guess_language

import markdown
import os.path

from flask import render_template
from flask import send_file
from flask import request
from flask import g

import traceback

from app import app
from app import auth
from common import database


import WebMirror.API

import app.sub_views.content_views as content_views
import app.sub_views.rss_views     as rss_views
import app.sub_views.search_views  as search_views
import app.sub_views.status_view   as status_view
import app.sub_views.misc_views    as misc_views
import app.sub_views.nu_views      as nu_views
import app.sub_views.ebook_view    as ebook_view


@app.before_request
def before_request():
	g.locale = 'en'
	g.session = database.get_db_session(flask_sess_if_possible=False)
	print("Checked out session")


@app.teardown_request
def teardown_request(response):
	try:
		try:
			g.session.commit()
		except Exception:
			g.session.rollback()

		print("Returned session")

		database.delete_db_session(flask_sess_if_possible=False)
	except Exception:
		print("Failure in teardown_request()!")
		traceback.print_exc()


@app.errorhandler(404)
def not_found_error(dummy_error):
	print("404 for '{}'. Wat?".format(request.path))
	return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(dummy_error):
	print("Internal Error!")
	print(dummy_error)
	print(traceback.format_exc())
	# print("500 error!")
	return render_template('500.html'), 500




@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
@auth.login_required
def index():

	interesting = ""
	if os.path.exists("reading_list.txt"):
		with open("reading_list.txt", "r") as fp:
			raw_text = fp.read()
		interesting = markdown.markdown(raw_text, extensions=["mdx_linkify"])

		interesting = WebMirror.API.processRaw(interesting)

	return render_template('index.html',
						   title               = 'Home',
						   interesting_links   = interesting,
						   )

@app.route('/favicon.ico')
def sendFavIcon():
	return send_file(
		"./static/favicon.ico",
		conditional=True
		)



