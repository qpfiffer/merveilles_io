from context_processors import db_meta_info
from flask import request, current_app
from functools import wraps
from kyotocabinet import DB
import requests

def ol_view_cache(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Debug
        if not current_app.config['CACHE']:
            return f(*args, **kwargs)

        res = None
        fancy = hash("{}{}{}".format(db_meta_info()['count'], request.url, f.func_name))

        resp = requests.get("http://localhost:8080/{}".format(fancy))
        if resp.status_code == 404:
            res = f(*args, **kwargs)
            requests.post("http://localhost:8080/{}".format(fancy),
                data=res.encode('utf-8'), headers={"Content-Type": "text/html"})
        else:
            res = resp.text

        return res
    return decorated_function

def kc_view_cache(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Debug
        if not current_app.config['CACHE']:
            return f(*args, **kwargs)

        db = DB()
        db.open("/tmp/page_cache.kch")
        res = None
        fancy = hash("{}{}{}".format(db_meta_info()['count'], request.url, f.func_name))

        res = db.get(fancy)
        if not res:
            res = f(*args, **kwargs)
            db.set(fancy, res)

        db.close()
        return res
    return decorated_function
