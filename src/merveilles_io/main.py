from bs4 import BeautifulSoup
from datetime import datetime
from flask import Flask, render_template, request, Response
from kyotocabinet import DB
from json import loads, dumps
from time import mktime
from urllib2 import urlopen
import sys, getopt, random, re

app = Flask(__name__)
PERSON_COLORS = ["#FFD923", "#AA2BEF", "#366EEF", "#A68B0B"]
FILTER_MAX = 50

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'link']:
        return False
    elif re.match('<!--.*-->', unicode(element)):
        return False

    return True

def is_url_in_db(db, url):
    cur = db.cursor()
    cur.jump_back()

    for i in range(0,FILTER_MAX):
        rec = cur.get(False)
        if not rec:
            break
        if loads(rec[1])['url'] == url:
            return True

        cur.step_back()

    cur.disable()
    return False

def get_items(item_filter):
    items = []
    db = DB()
    db_prefix = app.config['DB_PREFIX']
    if not db.open("{0}links.kct".format(db_prefix), DB.OREADER):
        print "Could not open database."

    cur = db.cursor()
    cur.jump_back()
    while len(items) < FILTER_MAX:
        rec = cur.get(False)
        if not rec:
            break

        if item_filter(rec):
            items.append(rec)

        cur.step_back()
    cur.disable()

    sorted_items = sorted(items, key=lambda x: int(x[0]), reverse=True)
    sorted_items_for_viewing = [loads(item[1]) for item in sorted_items]
    return sorted_items_for_viewing

@app.template_filter('unix_to_human')
def unix_to_human(timestamp_str):
    time = float(timestamp_str)
    return unicode(datetime.fromtimestamp(time))

@app.route("/submit", methods=['POST'])
def submit():
    mimetype = "application/json"
    url = request.json['url']
    db = DB()

    db_prefix = app.config['DB_PREFIX']
    if not db.open("{0}links.kct".format(db_prefix),
        DB.OWRITER | DB.OCREATE):
        print "Could not open database."
        return Response('{"What happened?": "Couldn\'t open the damn '\
            'database."}',
            mimetype=mimetype)

    if is_url_in_db(db, url):
        return Response('{"What happened?": "Someone '\
            'tried to submit a duplicate URL."}',
            mimetype=mimetype)

    try:
        request = urlopen(url, timeout=3)
        soup = BeautifulSoup(request)
    except:
        return Response('{"What happened?": '\
            'I dunno bs4 messed up somehow."}',
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

@app.route("/intrique", methods=['GET'])
def intrigue():
    user = request.args.get("user", "")
    items = get_items(lambda x: loads(x[1])["person"].lower() == user.lower())

    return render_template("index.html", items=items)

@app.route("/", methods=['GET'])
def root():
    items = get_items(lambda x: True)

    return render_template("index.html", items=items)

def main(argv):
    app.config['DB_PREFIX'] = "/tmp/"
    debug = False

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["db=", "debug"])
    except getopt.GetoptError:
        print 'merveilles_io --db=<db_dir>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'NO HELP FOR THE WICKED'
            sys.exit()
        elif opt in ("-d", "--db"):
            app.config['DB_PREFIX'] = arg
        elif opt in ("--debug"):
            debug = True

    app.run(debug=debug)

if __name__ == "__main__":
    main(sys.argv[1:])
