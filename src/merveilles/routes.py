from database import insert_item, get_items, top_things, search_func, \
    get_all_items, get_post_num, get_items_last_X_days, get_page_count, \
    aggregate_by_hour, get_user_stats
from json import loads, dumps
from datetime import datetime, timedelta, date
from utils import get_domain, get_paradise_items, gen_paradise_graph, \
    get_paradise_json_for_d3, build_posts
from flask import current_app, Blueprint, render_template, request, Response, \
    make_response, abort, redirect, url_for
from time import mktime
import requests

app = Blueprint('merveilles', __name__, template_folder='templates')

@app.route("/paradise", methods=['GET'])
def paradise():
    return render_template("paradise.html")

@app.route("/viz", methods=['GET'])
def viz():
    return render_template("viz.html")

@app.route("/blog", methods=['GET'])
def blog():
    try:
        posts = build_posts(current_app.config["BLOG_DIR"])
    except OSError as e:
        return redirect(url_for('merveilles.root'))
    return render_template("blog.html", posts=posts)

@app.route("/blog/<slug>", methods=['GET'])
def blog_post(slug):
    # Whole-ass getting the post:
    try:
        post = filter(lambda x: x["slug"] == slug, build_posts(current_app.config["BLOG_DIR"]))
    except OSError as e:
        abort(404)

    if len(post) != 1:
        abort(404)

    return render_template("blog_post.html", post=post[0])

@app.route("/paradise.json", methods=['GET'])
def paradise_json():
    response = make_response(open(current_app.config["PARADISE_JSON"]).read())
    response.headers["Content-type"] = "application/json"
    return response
    #items = get_paradise_json_for_d3()
    #return Response(dumps(items), mimetype="application/json")

@app.route("/submit", methods=['POST'])
def submit():
    url = request.json['url']
    person = request.json["person"]
    return insert_item(url, person, current_app.config["DB_FILE"])

@app.route("/intrigue/<user>", methods=['GET'])
def intrigue(user):
    items = get_items(
        lambda x: loads(x[1])["person"].lower() == user.lower(),
        current_app.config["DB_FILE"])

    return render_template("index.html", items=items)

@app.route("/introspect/<domain>", methods=['GET'])
def introspect(domain):
    items = get_items(
        lambda x: get_domain(loads(x[1])).lower() in domain.lower(),
        current_app.config["DB_FILE"])

    return render_template("index.html", items=items)

@app.route("/interrogate/<qstring>", methods=['GET'])
def interrogate(qstring):
    items = get_items(
        lambda x: search_func(loads(x[1]), qstring),
        current_app.config["DB_FILE"])

    return render_template("index.html", items=items)

@app.route("/", methods=['GET'])
def root():
    page_count = get_page_count()
    pages = range(0, page_count)
    requested_page = int(request.args.get("page", 0))
    if page_count > 0 and requested_page < 0:
        requested_page = 0
    elif page_count > 0 and requested_page > pages[-1]:
        requested_page = pages[-1]

    items = get_items(lambda x: True,
        current_app.config["DB_FILE"], requested_page)
    for item in items:
        if item['title'] is None or item['title'] == "":
            item['title'] = item['url']

    ten_days = get_items_last_X_days(current_app.config["DB_FILE"], 10)

    time = datetime.now() - timedelta(days=10)
    date_obj = date(year=time.year, month=time.month, day=time.day)
    day_unix = int(mktime(date_obj.timetuple()))

    p_to_dp = {}
    stats = []

    for item in ten_days:
        for person in ten_days[item]:
            if p_to_dp.get(person, False) == False:
                # {u'December': [[1384070400, 1
                p_to_dp[person] = [[item, ten_days[item][person]]]
            else:
                p_to_dp[person].append([item, ten_days[item][person]])

    for item in p_to_dp:
        stats.append({"name": item, "data": sorted(p_to_dp[item])})

    return render_template("index.html", items=items,
        stats=stats, start_date=day_unix, pages=pages,
        current_page=request.args.get('page', 0),
        next_page=requested_page+1, prev_page=requested_page-1)

@app.route("/sigma")
def sigma():
    items = top_things(current_app.config["DB_FILE"])
    graph_data = items[2]
    return render_template("sigma.html", items=items, graph_data=graph_data)

@app.route("/top")
def top():
    return redirect(url_for('merveilles.stats'))

@app.route("/stats")
def stats():
    db_file = current_app.config["DB_FILE"]
    top_items = top_things(db_file)
    graph_data = top_items[2]

    last_day = get_items_last_X_days(db_file, 1, munge=False)
    hourly_activity = aggregate_by_hour(db_file)


    time = datetime.now() - timedelta(days=10)
    date_obj = date(year=time.year, month=time.month, day=time.day)
    day_unix = int(mktime(date_obj.timetuple()))

    p_to_dp = {}
    stats = []

    for item in last_day:
        for person in last_day[item]:
            if p_to_dp.get(person, False) == False:
                p_to_dp[person] = [[item, last_day[item][person]]]
            else:
                p_to_dp[person].append([item, last_day[item][person]])

    for item in p_to_dp:
        stats.append({"name": item, "data": sorted(p_to_dp[item])})

    return render_template("stats.html", items=top_items, hourly_activity=hourly_activity,
        stats=stats, graph_data=graph_data)

@app.route("/data/all")
def all_posts():
    items = get_all_items(current_app.config["DB_FILE"])
    return Response(dumps(items), mimetype="application/json")

@app.route("/data/<int:post_num>")
def post_num(post_num):
    item = get_post_num(post_num, current_app.config["DB_FILE"])
    return Response(dumps(item), mimetype="application/json")

@app.route("/data/<username>")
def user_stats(username):
    item = get_user_stats(username, current_app.config["DB_FILE"])
    return Response(dumps(item), mimetype="application/json")

@app.route("/data/<int:post_num>/pretty")
def post_num_pretty(post_num):
    item = get_post_num(post_num, current_app.config["DB_FILE"])
    if item == {}:
        abort(404)
    return render_template("index.html", items=[item])

