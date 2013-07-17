from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, render_template, request, Response
from kyotocabinet import DB
from json import loads, dumps
from time import mktime
from urllib2 import urlopen
import random
import re

app = Flask(__name__)
PERSON_COLORS = ["#FFD923", "#AA2BEF", "#366EEF", "#A68B0B"]

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'link']:
        return False
    elif re.match('<!--.*-->', unicode(element)):
        return False

    return True

@app.route("/submit", methods=['POST'])
def submit():
    mimetype = "application/json"
    url = request.json['url']
    db = DB()

    if not db.open("links.kct", DB.OWRITER | DB.OCREATE):
        print "Could not open database."
        return Response('{"What happened?": "Couldn\'t open the damn database."}',
            mimetype=mimetype)

    try:
        soup = BeautifulSoup(urlopen(url))
    except:
        return Response('{"What happened?": "I dunno bs4 messed up somehow."}',
            mimetype=mimetype)

    title = soup.title.string
    created_at = int(mktime(datetime.now().utctimetuple()))

    func = lambda a,v: a + " " + v
    visible_stuff = filter(visible, soup.findAll(text=True))
    summary = reduce(func, visible_stuff, "")[:300] + "..."

    record = {
        "created_at": created_at,
        "title": title,
        "url": url,
        "person": request.json["person"],
        "summary": summary,
        "person_color": PERSON_COLORS[random.randint(0, len(PERSON_COLORS)-1)]
    }
    db.set(created_at, dumps(record))
    db.close()
    return Response('{"What happened?": "MUDADA"}',
        mimetype=mimetype)

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

    sorted_items = sorted(items, key=lambda x: int(x[0]), reverse=True)
    sorted_items_for_viewing = [loads(item[1]) for item in sorted_items][:50]
    return render_template("index.html", items=sorted_items_for_viewing)

def main_production():
    app.run(host="0.0.0.0")

def main_debug():
    app.run(debug=True)

if __name__ == "__main__":
    main_debug()
