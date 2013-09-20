from kyotocabinet import DB
from flask import Blueprint

def db_meta_info():
    meta = {}
    db = DB()
    db_file = app.config['DB_FILE']
    if not db.open("{0}".format(db_file), DB.OREADER):
        print "Could not open database."
    meta["size"] = db.size()
    meta["count"] = db.count()
    db.close()

    return meta
