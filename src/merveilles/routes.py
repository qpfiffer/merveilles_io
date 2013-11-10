from database import insert_item, get_items, top_things, search_func, \
    get_all_items, get_post_num
from json import loads, dumps
from utils import get_domain, get_paradise_items, gen_paradise_graph, \
    get_paradise_json_for_d3, build_posts
from flask import current_app, Blueprint, render_template, request, Response, \
    make_response, abort
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
    posts = build_posts(current_app.config["BLOG_DIR"])
    return render_template("blog.html", posts=posts)

@app.route("/blog/<slug>", methods=['GET'])
def blog_post(slug):
    # Whole-ass getting the post:
    post = filter(lambda x: x["slug"] == slug, build_posts(current_app.config["BLOG_DIR"]))

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
    return insert_item(url, person)

@app.route("/intrigue", methods=['GET'])
def intrigue():
    user = request.args.get("user", "")
    items = get_items(
        lambda x: loads(x[1])["person"].lower() == user.lower(),
        current_app.config["DB_FILE"])

    return render_template("index.html", items=items)

@app.route("/introspect", methods=['GET'])
def introspect():
    domain = request.args.get("domain", "")
    items = get_items(
        lambda x: get_domain(loads(x[1])).lower() in domain.lower(),
        current_app.config["DB_FILE"])

    return render_template("index.html", items=items)

@app.route("/interrogate", methods=['GET'])
def interrogate():
    qstring = request.args.get("q", "")
    items = get_items(
        lambda x: search_func(loads(x[1]), qstring),
        current_app.config["DB_FILE"])

    return render_template("index.html", items=items)

@app.route("/", methods=['GET'])
def root():
    items = get_items(lambda x: True, current_app.config["DB_FILE"])
    for item in items:
        if item['title'] is None or item['title'] == "":
            item['title'] = item['url']

    return render_template("index.html", items=items)

@app.route("/sigma")
def sigma():
    items = top_things(current_app.config["DB_FILE"])
    graph_data = items[2]
    return render_template("sigma.html", items=items, graph_data=graph_data)

@app.route("/top")
def top():
    items = top_things(current_app.config["DB_FILE"])
    graph_data = items[2]
    return render_template("top.html", items=items, graph_data=graph_data)

@app.route("/stats")
def stats():
    return render_template("stats.html")

@app.route("/data/all")
def all_posts():
    items = get_all_items(current_app.config["DB_FILE"])
    return Response(dumps(items), mimetype="application/json")

@app.route("/data/<int:post_num>")
def post_num(post_num):
    item = get_post_num(post_num, current_app.config["DB_FILE"])
    return Response(dumps(item), mimetype="application/json")

@app.route("/data/<int:post_num>/pretty")
def post_num_pretty(post_num):
    item = get_post_num(post_num, current_app.config["DB_FILE"])
    if item == {}:
        abort(404)
    return render_template("index.html", items=[item])

