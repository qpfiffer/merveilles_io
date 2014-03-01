from json import loads
from datetime import datetime, timedelta, date
from flask import current_app, Blueprint, render_template, request, \
    abort, redirect, url_for, g
from time import mktime

from cache import ol_view_cache
from database import insert_item, get_items, top_things, search_func, \
    get_items_last_X_days, aggregate_by_hour
from utils import get_domain, build_posts, get_effective_page, auth_user
import requests, urllib

app = Blueprint('merveilles', __name__, template_folder='templates')

@app.route("/viz", methods=['GET'])
@ol_view_cache
def viz():
    return render_template("viz.html")

@app.route("/blog", methods=['GET'])
@ol_view_cache
def blog():
    try:
        posts = build_posts(current_app.config["BLOG_DIR"])
    except OSError:
        return redirect(url_for('merveilles.root'))
    return render_template("blog.html", posts=posts)

@app.route("/login", methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        email_address = request.form['email_address']
        password = request.form['password']
        if auth_user(email_address, password):
            session.permanent = True
            session['email_address'] = request.form['email_address']
            return redirect(url_for('kyoto.manage'))
        else:
            message = 'Login incorrect.'

    return render_template("login.html", message=message)
    return render_template("login.html")

@app.route("/blog/<slug>", methods=['GET'])
@ol_view_cache
def blog_post(slug):
    # Whole-ass getting the post:
    try:
        post = filter(lambda x: x["slug"] == slug, build_posts(current_app.config["BLOG_DIR"]))
    except OSError:
        abort(404)

    if len(post) != 1:
        abort(404)

    return render_template("blog_post.html", post=post[0])

@app.route("/submit", methods=['POST'])
def submit():
    url = request.json['url']
    person = request.json["person"]
    return insert_item(url, person, g.db_file)

@app.route("/intrigue/<user>", methods=['GET'])
@ol_view_cache
def intrigue(user):
    filter_func = lambda x: loads(x[1])["person"].lower() == user.lower()
    pages, requested_page = get_effective_page(request.args.get("page", 0),
            filter_func)
    items = get_items(filter_func, g.db_file, requested_page)

    return render_template("index.html", items=items, pages=pages,
            requested_page=requested_page, current_page=request.args.get('page', 0))

@app.route("/introspect/<domain>", methods=['GET'])
@ol_view_cache
def introspect(domain):
    filter_func = lambda x: get_domain(loads(x[1])).lower() in domain.lower()
    pages, requested_page = get_effective_page(request.args.get("page", 0),
            filter_func)
    items = get_items(filter_func, g.db_file)

    return render_template("index.html", items=items, pages=pages,
            requested_page=requested_page, current_page=request.args.get('page', 0))

@app.route("/introspect", methods=['GET'])
def introspect_old():
    if not request.args.get('domain', False):
        return redirect(url_for('merveilles.root'))

    return redirect(url_for('merveilles.introspect', domain=request.args['domain']))

@app.route("/interrogate/<qstring>", methods=['GET'])
@ol_view_cache
def interrogate(qstring):
    filter_func = lambda x: search_func(loads(x[1]), qstring)
    pages, requested_page = get_effective_page(request.args.get("page", 0),
            filter_func)
    items = get_items(filter_func, g.db_file)

    return render_template("index.html", items=items, pages=pages,
            requested_page=requested_page, current_page=request.args.get('page', 0))

@app.route("/", methods=['GET'])
@ol_view_cache
def root():
    pages, requested_page = get_effective_page(request.args.get("page", 0))
    items = get_items(lambda x: True, g.db_file, requested_page)

    return render_template("index.html", items=items, pages=pages,
        current_page=request.args.get('page', 0))

@app.route("/sigma")
@ol_view_cache
def sigma():
    items = top_things(g.db_file)
    graph_data = items[2]
    return render_template("sigma.html", items=items, graph_data=graph_data)

@app.route("/top")
@ol_view_cache
def top():
    return redirect(url_for('merveilles.stats'))

@app.route("/stats")
@ol_view_cache
def stats():
    db_file = g.db_file
    top_items = top_things(db_file)
    graph_data = top_items[2]

    last_day = get_items_last_X_days(db_file, 1, munge=False)
    ten_days = get_items_last_X_days(g.db_file, 10)
    hourly_activity = aggregate_by_hour(db_file)

    time = datetime.now() - timedelta(days=10)
    date_obj = date(year=time.year, month=time.month, day=time.day)
    day_unix = int(mktime(date_obj.timetuple()))

    p_to_dp_ten = {}
    stats_ten = []

    for item in ten_days:
        for person in ten_days[item]:
            if p_to_dp_ten.get(person, False) == False:
                p_to_dp_ten[person] = [[item, ten_days[item][person]]]
            else:
                p_to_dp_ten[person].append([item, ten_days[item][person]])

    for item in p_to_dp_ten:
        stats_ten.append({"name": item, "data": sorted(p_to_dp_ten[item])})

    p_to_dp = {}
    stats = []
    people = {}
    i = 0

    for item in last_day:
        for person in last_day[item]:
            if people.get(person, False) == False:
                people[person] = i
                i = i+1
            if p_to_dp.get(person, False) == False:
                p_to_dp[person] = [[item, last_day[item][person]]]
            else:
                p_to_dp[person].append([item, last_day[item][person]])

    for item in p_to_dp:
        muh_lambda = lambda x: (x[0], people[item])
        stats.append({"name": item, "data": map(muh_lambda, sorted(p_to_dp[item]))})

    return render_template("stats.html",
        items=top_items,
        hourly_activity=hourly_activity,
        start_date=day_unix,
        stats=stats,
        stats_ten=stats_ten,
        graph_data=graph_data)
