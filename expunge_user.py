#!/usr/bin/env python2
from json import loads
from kyotocabinet import DB
from sys import argv

def main():
    db_file = argv[0]
    username = argv[1]

    db = DB()
    if not db.open("{0}".format(db_file), DB.OREADER | DB.OCREATE):
        print "Could not open database."

    all_keys = []
    cur = db.cursor()
    cur.jump_back()
    while True:
        rec = cur.get(False)
        if not rec:
            break

        loaded = loads(rec[1])
        if loaded["person"] == username:
            all_keys.append(cur.get_key())

    print "Found {} records.".format(len(all_keys))

if __name__ == '__main__':
    main()
