from flask import Flask
from json import loads, dumps
from merveilles.routes import app as routes
from merveilles.context_processors import app as context_processors
from merveilles.filters import get_domain_filter, file_size, unix_to_human
from merveilles.context_processors import db_meta_info
from merveilles.utils import gen_thumbnail_for_url
import sys, os, getopt

app = Flask(__name__)
app.register_blueprint(routes)
app.register_blueprint(context_processors)
app.config['DB_FILE'] = os.environ.get("DB_FILE") or "/tmp/links.kct"
app.config['CHANNEL'] = os.environ.get("CHANNEL") or "#merveilles"
app.config['LIVE_SITE'] = os.environ.get("LIVE_SITE") or False
app.config['BLOG_DIR'] = os.environ.get("BLOG_DIR") or "src/static/blog_posts/"
app.config['PARADISE_JSON'] = os.environ.get("PARADISE_JSON") or "src/static/paradise.json"
app.config['THUMBNAIL_DIR'] = os.environ.get("PARADISE_JSON") or "src/static/thumbnails/"
#app.jinja_env.globals.update(size=db_meta_info)
app.jinja_env.filters['get_domain'] = get_domain_filter
app.jinja_env.filters['file_size'] = file_size
app.jinja_env.filters['unix_to_human'] = unix_to_human


def gen_thumbnails(db_file):
    db = DB()
    if not db.open("{0}".format(db_file), DB.OREADER | DB.OCREATE):
        print "Could not open database."

    cur = db.cursor()
    cur.jump_back()
    while True:
        rec = cur.get(False)
        if not rec:
            break

        loaded = loads(item[1])

        if item["url"].lower().endswith(("jpg", "jpeg", "gif", "png")):
            thumbnail = gen_thumbnail_for_url(loads(item[1]))
            loaded["thumbnail"] = thumbnail
            cur.set(dumps(loaded))

        cur.step_back()

    cur.disable()
    db.close()

    sorted_items = sorted(items, key=get_key, reverse=True)
    sorted_items_for_viewing = [loads(item[1]) for item in sorted_items]
    return sorted_items_for_viewing

def main(argv):
    debug = False
    gen_thumbnails = False
    port = 5000

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["db=", "debug", "port="])
    except getopt.GetoptError:
        print "merveilles_io --db=<db_dir>"
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'NO HELP FOR THE WICKED'
            sys.exit()
        elif opt in ("-d", "--db"):
            app.config['DB_FILE'] = arg
        elif opt in ("--debug"):
            debug = True
        elif opt in ("--port"):
            port = int(arg)
        elif opt in ("--gen-thumbnails"):
            gen_thumbnails = True

    if gen_thumbnails and app.config['DB_FILE']:
        gen_thumbnails(app.config['DB_FILE'])
        sys.exit(0)

    app.run(debug=debug, port=port)

if __name__ == "__main__":
    main(sys.argv[1:])
