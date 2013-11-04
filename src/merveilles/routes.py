from database import insert_item, get_items, top_things, search_func
from flask import current_app, Blueprint, render_template, request, Response, make_response
from json import loads, dumps
from utils import get_domain, get_paradise_items, gen_paradise_graph, get_paradise_json_for_d3
import requests

app = Blueprint('merveilles', __name__, template_folder='templates')

@app.route("/paradise", methods=['GET'])
def paradise():
    return render_template("paradise.html", channel=current_app.config["CHANNEL"])

@app.route("/paradise.json", methods=['GET'])
def paradise_json():
    response = make_response(open('src/static/paradise.json').read())
    response.headers["Content-type"] = "application/json"
    return response
    #items = get_paradise_json_for_d3()
    #return Response(dumps(items), mimetype="application/json")

@app.route("/submit", methods=['POST'])
def submit():
    url = request.json['url']
    person = request.json["person"]
    return insert_item(url, person, current_app.config["DB_FILE"])

@app.route("/intrigue", methods=['GET'])
def intrigue():
    user = request.args.get("user", "")
    items = get_items(
        lambda x: loads(x[1])["person"].lower() == user.lower(),
        current_app.config["DB_FILE"])

    return render_template("index.html", items=items, channel=current_app.config["CHANNEL"])

@app.route("/introspect", methods=['GET'])
def introspect():
    domain = request.args.get("domain", "")
    items = get_items(
        lambda x: get_domain(loads(x[1])).lower() in domain.lower(),
        current_app.config["DB_FILE"])

    return render_template("index.html", items=items, channel=current_app.config["CHANNEL"])

@app.route("/interrogate", methods=['GET'])
def interrogate():
    qstring = request.args.get("q", "")
    items = get_items(
        lambda x: search_func(loads(x[1]), qstring),
        current_app.config["DB_FILE"])

    return render_template("index.html", items=items, channel=current_app.config["CHANNEL"])

@app.route("/", methods=['GET'])
def root():
    items = get_items(lambda x: True, current_app.config["DB_FILE"])
    for item in items:
        if item['title'] is None or item['title'] == "":
            item['title'] = item['url']

    return render_template("index.html", items=items, channel=current_app.config["CHANNEL"])

@app.route("/top")
def top():
    items = top_things(current_app.config["DB_FILE"])
    graph_data = items[2]
    return render_template("top.html", items=items, graph_data=graph_data, channel=current_app.config["CHANNEL"])
