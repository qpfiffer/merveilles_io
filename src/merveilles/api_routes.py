from flask import Blueprint, render_template, Response, \
    abort, g
from json import dumps

from cache import view_cache
from database import get_all_items, get_post_num, \
        get_post_by_date, get_user_stats

app = Blueprint('merveilles_api', __name__, template_folder='templates')

@app.route("/data/all")
@view_cache
def all_posts():
    items = get_all_items(g.db_file)
    return Response(dumps(items), mimetype="application/json")

@app.route("/data/<int:post_num>")
@view_cache
def post_num(post_num):
    item = get_post_num(post_num, g.db_file)
    if item == {}:
        abort(404)
    return Response(dumps(item), mimetype="application/json")

@app.route("/data/date/<int:key>")
@view_cache
def post_date(key):
    item = get_post_by_date(key, g.db_file)
    if item == {}:
        abort(404)
    return Response(dumps(item), mimetype="application/json")

@app.route("/data/<username>")
@view_cache
def user_stats(username):
    item = get_user_stats(username, g.db_file)
    if item == {}:
        abort(404)
    return Response(dumps(item), mimetype="application/json")

@app.route("/data/<int:post_num>/pretty")
def post_num_pretty(post_num):
    item = get_post_num(post_num, g.db_file)
    if item == {}:
        abort(404)
    return render_template("index.html", items=[item])

@app.route("/data/date/<int:key>/pretty")
def post_date_pretty(key):
    item = get_post_by_date(key, g.db_file)
    if item == {}:
        abort(404)
    return render_template("index.html", items=[item])

@app.route("/data/date/single/<int:key>")
def post_date_single(key):
    item = get_post_by_date(key, g.db_file)
    if item == {}:
        abort(404)
    return render_template("single_item.html", item=item)

