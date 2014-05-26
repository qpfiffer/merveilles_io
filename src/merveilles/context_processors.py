from kyotocabinet import DB
from flask import current_app, Blueprint, g, session

app = Blueprint("wut", __name__, template_folder='templates')

@app.app_context_processor
def site_settings():
    return {"live_site": current_app.config['LIVE_SITE'],
            "channel": current_app.config['CHANNEL']
            }

@app.app_context_processor
def get_user():
    from merveilles.database import _get_user_str
    user = None
    username = session.get("username")
    if username:
        oleg = g.oleg
        user_str = _get_user_str(username)
        user = oleg.get(user_str)

    return {"user": user}

@app.app_context_processor
def db_meta_info():
    meta = {}
    db = DB()
    db_file = current_app.config['DB_FILE']
    if not db.open("{0}".format(db_file), DB.OREADER):
        print "Could not open database (meta info)."
    meta["size"] = db.size()
    meta["count"] = db.count()
    db.close()

    return meta
