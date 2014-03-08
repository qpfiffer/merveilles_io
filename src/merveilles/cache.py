from context_processors import db_meta_info
from flask import request, current_app
from functools import wraps
from kyotocabinet import DB
import requests, time, zlib, urllib

def ol_view_cache(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Debug
        if not current_app.config['CACHE']:
            return f(*args, **kwargs)

        res = None
        fancy = "{}{}{}{}".format(db_meta_info()['count'],
                request.host,
                request.query_string,
                f.func_name)
        quoted = urllib.quote(fancy.encode('ascii', 'replace'))

        resp = requests.get("http://localhost:8080/{}".format(quoted), stream=True)
        if resp.status_code == 404:
            res = f(*args, **kwargs)
            # 24 hours
            expiration = int(time.mktime(time.gmtime())) + (60 * 60 * 24)
            utf_data = res.encode('utf-8')
            compressed = zlib.compress(utf_data)
            requests.post("http://localhost:8080/{}".format(quoted),
                data=compressed,
                headers={
                    "Content-Type": "text/html",
                    "X-OlegDB-use-by": expiration})
        else:
            compressed = resp.raw.read()
            res = zlib.decompress(compressed)

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
