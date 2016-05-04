#!/usr/bin/env python2
from json import loads
from kyotocabinet import DB
from sys import argv

def main():
    db_file = argv[1]
    username = argv[2]

    if not db_file and not username:
        print "Need db_file and username."
        return -1

    db = DB()
    if not db.open("{0}".format(db_file), DB.OWRITER):
        print "Could not open database."
        return -1

    all_keys = []
    cur = db.cursor()
    cur.jump()
    while True:
        rec = cur.get(False)
        if not rec:
            break

        loaded = loads(rec[1])
        if loaded["person"] == username:
            all_keys.append(cur.get_key())

        cur.step()
    cur.disable()

    print "Found {} records.".format(len(all_keys))
    for key in all_keys:
        print "Pending {}...".format(key)
        if len(argv) > 3 and argv[3] == '--delete':
            print "Removing {}...".format(key)
            if not db.remove(key):
                print "Could not remove key: {}".format(db.error())

    db.close()

if __name__ == '__main__':
    main()
