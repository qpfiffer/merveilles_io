from flask import abort, Flask, g, request, session
from json import loads, dumps
from kyotocabinet import DB
from olegsessions import OlegDBSessionInterface
from olegdb import OlegDB

from merveilles.routes import app as routes
from merveilles.api_routes import app as api_routes
from merveilles.context_processors import app as context_processors
from merveilles.constants import THUMBNAIL_DIR, PARADISE_JSON, DB_FILE, \
    DEFAULT_CHANNEL, BLOG_DIR
from merveilles.filters import get_domain_filter, file_size, unix_to_human,\
    is_video, is_sound, youtube_vid, is_youtube
from merveilles.utils import gen_thumbnail_for_url, random_password

import sys, os, getopt, time

app = Flask(__name__)
app.register_blueprint(routes)
app.register_blueprint(api_routes)
app.register_blueprint(context_processors)
app.config['DB_FILE'] = os.environ.get("DB_FILE") or DB_FILE
app.config['CHANNEL'] = os.environ.get("CHANNEL") or DEFAULT_CHANNEL
app.config['LIVE_SITE'] = os.environ.get("LIVE_SITE") or False #Turns on or off google analytics
app.config['BLOG_DIR'] = os.environ.get("BLOG_DIR") or BLOG_DIR
app.config['PARADISE_JSON'] = os.environ.get("PARADISE_JSON") or PARADISE_JSON
app.config['THUMBNAIL_DIR'] = os.environ.get("THUMBNAIL_DIR") or THUMBNAIL_DIR
app.config['CACHE'] = True
app.session_interface = OlegDBSessionInterface()
app.jinja_env.globals.update(get_domain=get_domain_filter)

app.jinja_env.filters['get_domain'] = get_domain_filter
app.jinja_env.filters['file_size'] = file_size
app.jinja_env.filters['unix_to_human'] = unix_to_human
app.jinja_env.filters['is_video'] = is_video
app.jinja_env.filters['is_sound'] = is_sound
app.jinja_env.filters['is_youtube'] = is_youtube
app.jinja_env.filters['youtube_vid'] = youtube_vid


@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.2fms" % ((time.time() - g.request_start_time) * 1000)
    g.db_file = app.config['DB_FILE']
    g.oleg = OlegDB()

@app.before_request
def csrf_protect():
    if request.url_rule and request.url_rule.rule != '/submit' and request.method == "POST":
        token = session.get('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = random_password()
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

def gen_thumbnails(db_file):
    db = DB()
    if not db.open("{0}".format(db_file), DB.OREADER | DB.OWRITER):
        sys.exit(1)

    cur = db.cursor()
    cur.jump_back()
    while True:
        rec = cur.get(False)

        if not rec:
            break

        loaded = loads(rec[1])
        is_image = loaded["url"].lower().endswith(("jpg", "jpeg", "gif", "png"))

        if is_image:
            print "Thumbnailing {}".format(loaded["url"])
            loaded["is_image"] = True
            try:
                thumbnail = gen_thumbnail_for_url(loaded["url"], rec[0])
            except IOError as e:
                print "IOError: {}".format(e)
                print "Save result: {}".format(cur.set_value(dumps(loaded)))
                cur.step_back()
                continue


            if thumbnail:
                loaded["thumbnail"] = thumbnail
                print "Thumbnailed {}".format(loaded["url"])
                print "Save result: {}".format(cur.set_value(dumps(loaded)))

        cur.step_back()

    cur.disable()
    db.close()

    return True

def main(argv):
    debug = False
    should_gen_thumbnails = False
    port = 5000

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["db=", "debug", "port=", "gen-thumbnails"])
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
            should_gen_thumbnails = True

    if should_gen_thumbnails and app.config['DB_FILE']:
        gen_thumbnails(app.config['DB_FILE'])
        sys.exit(0)

    if debug:
        app.config['CACHE'] = False

    app.run(debug=debug, port=port)

if __name__ == "__main__":
    main(sys.argv[1:])
