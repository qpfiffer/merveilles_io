from BeautifulSoup import BeautifulSoup
from datetime import datetime
from flask import Flask, render_template, request, Response
from kyotocabinet import DB
from json import loads, dumps
from time import mktime
from urllib2 import urlopen

app = Flask(__name__)

def get_links(num):
    db = DB()
    if not db.open("links.kct", DB.OREADER | DB.OCREATE):
        print "Could not open database."
    return db[:num]

@app.route("/submit", methods=['POST'])
def submit():
    url = request.json['url']
    db = DB()

    if not db.open("links.kct", DB.OWRITER | DB.OCREATE):
        print "Could not open database."
        return Response('{"What happened?": "Something dumb."}', mimetype="text/json")

    try:
        title = BeautifulSoup(urlopen(url)).title.string
    except:
        return Response('{"What happened?": "Something dumb."}', mimetype="text/json")

    created_at = int(mktime(datetime.now().utctimetuple()))
    record = {
        "created_at": created_at,
        "title": title,
        "url": url,
        "person": request.json["person"]
    }
    db.set(created_at, dumps(record))
    db.close()
    return Response('{"What happened?": "MUDADA"}', mimetype="text/json")

@app.route("/", methods=['GET'])
def root():
    #items = [{"person": "person{0}".format(i),
    #          "title": "Killing Ducks: A mortuary.",
    #          "link":"http://link{0}.com".format(i)} for i in range(0,25)]
    items = []
    db = DB()

    if not db.open("links.kct", DB.OREADER):
        print "Could not open database."

    cur = db.cursor()
    cur.jump()
    while len(items) < 10:
        rec = cur.get(True)
        if not rec:
            break

        items.append(rec)
    cur.disable()
    sorted_items_for_viewing = [loads(item[1]) for item in sorted(items)]
    return render_template("index.html", items=sorted_items_for_viewing)

def main_production():
    app.run(host="0.0.0.0")

def main_debug():
    app.run(debug=True)

if __name__ == "__main__":
    main_debug()
