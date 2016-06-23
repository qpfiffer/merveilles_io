from flask import Blueprint, render_template, Response, \
    abort, g
from json import dumps

from database import get_all_items, get_post_num, \
        get_post_by_date, get_user_stats, set_user
from context_processors import get_user

app = Blueprint('merveilles_api', __name__, template_folder='templates')

@app.route("/data/all")
def all_posts():
    items = get_all_items(g.db_file)
    return Response(dumps(items), mimetype="application/json")

@app.route("/data/<int:post_num>")
def post_num(post_num):
    item = get_post_num(post_num, g.db_file)
    if item == {}:
        abort(404)
    return Response(dumps(item), mimetype="application/json")

@app.route("/star/<key>", methods=['GET', 'POST'])
def star_toggle(key):
    key = int(key)
    to_return = {"success": False, "error": None}
    user = get_user()["user"]

    if not user:
        to_return["error"] = "You are not logged in."
        return Response(dumps(to_return), mimetype="application/json"), 403

    if key in user["starred"]:
        user["starred"] = [x for x in user["starred"] if x != key]
        to_return["starred"] = False
    else:
        user["starred"].append(key)
        to_return["starred"] = True

    print "User stars: {}".format(user["starred"])
    if set_user(user):
        to_return["success"] = True
        return Response(dumps(to_return), mimetype="application/json")
    else:
        to_return["error"] = "Could not set user object."
        return Response(dumps(to_return), mimetype="application/json"), 500

    return Response(dumps(to_return), mimetype="application/json"), 403

@app.route("/data/date/<int:key>")
def post_date(key):
    item = get_post_by_date(key, g.db_file)
    if item == {}:
        abort(404)
    return Response(dumps(item), mimetype="application/json")

@app.route("/data/<username>")
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

