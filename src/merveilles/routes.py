from json import loads
from datetime import datetime, timedelta, date
from flask import current_app, Blueprint, render_template, request, \
    abort, redirect, url_for, g, session, Response
from time import mktime
from werkzeug.exceptions import BadRequestKeyError

from context_processors import get_user
from database import insert_item, get_items, top_things, search_func, \
    get_items_last_X_days, aggregate_by_hour, auth_user, sign_up
from utils import get_domain, build_posts, get_effective_page

app = Blueprint('merveilles', __name__, template_folder='templates')

@app.route("/viz", methods=['GET'])
def viz():
    return render_template("viz.html")

@app.route("/blog", methods=['GET'])
def blog():
    try:
        posts = build_posts(current_app.config["BLOG_DIR"])
    except OSError:
        return redirect(url_for('merveilles.root'))
    return render_template("blog.html", posts=posts)

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if auth_user(g.oleg, username, password):
            session.permanent = True
            session['username'] = username
            return redirect(url_for('merveilles.root'))
        error = "Could not log in for some reason."
    return render_template("login.html", error=error)

@app.route("/register", methods=['GET', 'POST'])
def register():
    error = ""
    if request.method == 'POST':
        try:
            username = request.form['username']
            password1 = request.form['password1']
            password2 = request.form['password2']
        except BadRequestKeyError:
            error = "Some data didn't make it to the front."
            return render_template("register.html", error=error)

        if len(username) == 0:
            error = "Must input username."
            return render_template("register.html", error=error)

        if password1 != password2:
            error = "Passwords do not match."
            return render_template("register.html", error=error)

        created, user_obj = sign_up(g.oleg, username, password1)
        if created:
            session.permanent = True
            session['username'] = user_obj['username']
            return redirect(url_for('merveilles.root'))
        # Well something didn't work right.
        error = user_obj

    return render_template("register.html", error=error)

@app.route("/blog/<slug>", methods=['GET'])
def blog_post(slug):
    # Whole-ass getting the post:
    try:
        def s(x):
            return x["slug"] == slug
        post = filter(s, build_posts(current_app.config["BLOG_DIR"]))
    except OSError:
        abort(404)

    if len(post) != 1:
        abort(404)

    return render_template("blog_post.html", post=post[0])

@app.route("/submit", methods=['POST'])
def submit():
    failure_response = (Response('{"Fucking Burn": True}', mimetype="application/json"), 666)

    try:
        if request.json['submission_salt'] != current_app.config['SUBMISSION_SALT']:
            return failure_response
    except KeyError:
            return failure_response

    url = request.json["url"]
    person = request.json["person"]
    title = request.json.get("title", "")
    return insert_item(url, person, g.db_file, title)

@app.route("/intrigue/<user>", methods=['GET'])
def intrigue(user):
    def filter_func(x):
        return loads(x[1])["person"].lower() == user.lower()
    pages, requested_page = get_effective_page(request.args.get("page", 0),
            filter_func)
    items = get_items(filter_func, g.db_file, requested_page)

    return render_template("index.html", items=items, pages=pages,
            requested_page=requested_page, current_page=request.args.get('page', 0))

@app.route("/introspect/<domain>", methods=['GET'])
def introspect(domain):
    def filter_func(x):
        return get_domain(loads(x[1])).lower() in domain.lower()
    pages, requested_page = get_effective_page(request.args.get("page", 0),
            filter_func)
    items = get_items(filter_func, g.db_file, requested_page)

    return render_template("index.html", items=items, pages=pages,
            requested_page=requested_page, current_page=request.args.get('page', 0))

@app.route("/user/starred", methods=['GET'])
def starred():
    user = get_user()["user"]
    if not user:
        return redirect(url_for('merveilles.login'))

    def filter_func(x)
        return int(loads(x[1])["created_at"]) in user["starred"]
    pages, requested_page = get_effective_page(request.args.get("page", 0),
            filter_func)
    items = get_items(filter_func, g.db_file, requested_page)

    return render_template("index.html", items=items, pages=pages,
            requested_page=requested_page, current_page=request.args.get('page', 0))


@app.route("/introspect", methods=['GET'])
def introspect_old():
    if not request.args.get('domain', False):
        return redirect(url_for('merveilles.root'))

    return redirect(url_for('merveilles.introspect', domain=request.args['domain']))

@app.route("/interrogate/<qstring>", methods=['GET'])
def interrogate(qstring):
    def filter_func(x):
        return search_func(loads(x[1]), qstring)
    pages, requested_page = get_effective_page(request.args.get("page", 0),
            filter_func)
    items = get_items(filter_func, g.db_file, requested_page)

    return render_template("index.html", items=items, pages=pages,
            requested_page=requested_page, current_page=request.args.get('page', 0))

@app.route("/", methods=['GET'])
def root():
    pages, requested_page = get_effective_page(request.args.get("page", 0))
    def s(x):
        return True
    items = get_items(, g.db_file, requested_page)

    return render_template("index.html", items=items, pages=pages,
        current_page=request.args.get('page', 0))

@app.route("/sigma")
def sigma():
    items = top_things(g.db_file)
    graph_data = items[2]
    return render_template("sigma.html", items=items, graph_data=graph_data)

@app.route("/top")
def top():
    return redirect(url_for('merveilles.stats'))

@app.route("/logout", methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('merveilles.root'))

@app.route("/stats")
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
        def muh_lambda(x):
            return (x[0], people[item])
        stats.append({"name": item, "data": map(muh_lambda, sorted(p_to_dp[item]))})

    return render_template("stats.html",
        items=top_items,
        hourly_activity=hourly_activity,
        start_date=day_unix,
        stats=stats,
        stats_ten=stats_ten,
        graph_data=graph_data)
