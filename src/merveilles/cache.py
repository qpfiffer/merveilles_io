from context_processors import db_meta_info
from flask import request
from functools import wraps
from kyotocabinet import DB

def view_cache(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
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
