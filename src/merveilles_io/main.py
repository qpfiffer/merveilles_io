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

def get_key(item):
    try:
        key = int(item[0])
    except:
        key = int(loads(item[1])["created_at"])
    return key

def top_things():
    urls = {}
    people = {}
    graph = {}

    db = DB()
    db_prefix = app.config['DB_PREFIX']

    if not db.open("{0}links.kct".format(db_prefix), DB.OREADER | DB.OCREATE):
        print "Could not open database."

    cur = db.cursor()
    cur.jump_back()
    while True:
        rec = cur.get(False)
        if not rec:
            break

        loaded_rec = loads(rec[1])
        split = loaded_rec['url'].split("://")[1].split("/")[0]

        if urls.get(split, False) == False:
            urls[split] = 1
        else:
            urls[split] = urls[split] + 1

        person = loaded_rec['person']
        if people.get(person, False) == False:
            people[person] = 1
        else:
            people[person] = people[person] + 1

        # Build a crazy relational graph out of my nosql data
        if graph.get(split, False) == False:
            graph[split] = [person]
        elif person not in graph[split]:
            graph[split].append(person)

        if graph.get(person, False) == False:
            graph[person] = [split]
        elif split not in graph[person]:
            graph[person].append(split)

        cur.step_back()
    cur.disable()
    db.close()

    return (sorted(urls.items(), key=lambda x: x[1], reverse=True),
            sorted(people.items(), key=lambda x: x[1], reverse=True),
            graph)

def get_items(item_filter):
    items = []
    db = DB()
    db_prefix = app.config['DB_PREFIX']
    if not db.open("{0}links.kct".format(db_prefix), DB.OREADER | DB.OCREATE):
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
    db.close()

    sorted_items = sorted(items, key=get_key, reverse=True)
    sorted_items_for_viewing = [loads(item[1]) for item in sorted_items]
    return sorted_items_for_viewing

@app.context_processor
def db_meta_info():
    meta = {}
    db = DB()
    db_prefix = app.config['DB_PREFIX']
    if not db.open("{0}links.kct".format(db_prefix), DB.OREADER):
        print "Could not open database."
    meta["size"] = db.size()
    meta["count"] = db.count()
    db.close()

    return meta

@app.template_filter('file_size')
def file_size(size_str):
    # Found here: http://djangosnippets.org/snippets/1866/
    value = int(size_str)
    if value < 512000:
        value = value / 1024.0
        ext = 'kb'
    elif value < 4194304000:
        value = value / 1048576.0
        ext = 'mb'
    else:
        value = value / 1073741824.0
        ext = 'gb'
    return '%s %s' % (str(round(value, 2)), ext)

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
        thing = urlopen(url, timeout=10)
        soup = BeautifulSoup(thing)
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

@app.route("/intrigue", methods=['GET'])
def intrigue():
    user = request.args.get("user", "")
    items = get_items(lambda x: loads(x[1])["person"].lower() == user.lower())

    return render_template("index.html", items=items)

@app.route("/", methods=['GET'])
def root():
    items = get_items(lambda x: True)
    for item in items:
        if item['title'] is None or item['title'] == "":
            item['title'] = item['url']

    return render_template("index.html", items=items)

@app.route("/top")
def top():
    items = top_things()
    graph_data = items[2]
    return render_template("top.html", items=items, graph_data=graph_data)

def main(argv):
    app.config['DB_PREFIX'] = "/tmp/"
    debug = False
    port = 5000

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["db=", "debug", "port="])
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
        elif opt in ("--port"):
            port = int(arg)

    app.run(debug=debug, port=port)

if __name__ == "__main__":
    main(sys.argv[1:])
