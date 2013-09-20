from flask import Flask
from merveilles.routes import app as routes
from merveilles.filters import get_domain_filter, file_size, unix_to_human
from merveilles.context_processors import db_meta_info
import sys, os, getopt

app = Flask(__name__)
app.register_blueprint(routes)
app.config['DB_FILE'] = os.environ.get("DB_FILE") or "/tmp/links.kct"
app.config['CHANNEL'] = os.environ.get("CHANNEL") or "#merveilles"
app.jinja_env.globals.update(db_meta_info=db_meta_info)
app.jinja_env.filters['get_domain'] = get_domain_filter
app.jinja_env.filters['file_size'] = file_size
app.jinja_env.filters['unix_to_human'] = unix_to_human


def main(argv):
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
            app.config['DB_FILE'] = arg
        elif opt in ("--debug"):
            debug = True
        elif opt in ("--port"):
            port = int(arg)

    app.run(debug=debug, port=port)

if __name__ == "__main__":
    main(sys.argv[1:])
