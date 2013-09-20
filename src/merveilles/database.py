from bs4 import BeautifulSoup
from datetime import datetime
from flask import Response
from kyotocabinet import DB
from json import dumps, loads
from time import mktime
from urllib2 import urlopen
import random

from constants import FILTER_MAX, PERSON_COLORS
from utils import get_domain, visible

def is_url_in_db(db, url):
    cur = db.cursor()
    cur.jump_back()

    for i in range(0,FILTER_MAX):
        rec = cur.get(False)
        if not rec:
            break
        if loads(rec[1])['url'] == url:
            return True

        cur.step_back()

    cur.disable()
    return False

def get_key(item):
    try:
        key = int(item[0])
    except:
        key = int(loads(item[1])["created_at"])
    return key

def top_things(db_file):
    urls = {}
    people = {}
    graph = {}

    db = DB()

    if not db.open("{0}".format(db_file), DB.OREADER | DB.OCREATE):
        print "Could not open database."

    cur = db.cursor()
    cur.jump_back()
    while True:
        rec = cur.get(False)
        if not rec:
            break

        loaded_rec = loads(rec[1])
        split = get_domain(loaded_rec)

        if urls.get(split, False) == False:
            urls[split] = 1
        else:
            urls[split] = urls[split] + 1

        person = loaded_rec['person']
        if people.get(person, False) == False:
            people[person] = 1
        else:
            people[person] = people[person] + 1

        if split is not None and split is not "" and \
            person is not None and person is not "":
            # Build a crazy relational graph out of my nosql data
            if graph.get(split, False) == False:
                graph[split] = {"is_person": False, "data": [person], "linked_to_count": 1}
            elif person not in graph[split]:
                graph[split]["data"].append(person)
                graph[split]["linked_to_count"] = graph[split]["linked_to_count"] + 1

            if graph.get(person, False) == False:
                graph[person] = {"is_person": True, "data": [split]}
            elif split not in graph[person]:
                graph[person]["data"].append(split)

        cur.step_back()
    cur.disable()
    db.close()

    return (sorted(urls.items(), key=lambda x: x[1], reverse=True),
            sorted(people.items(), key=lambda x: x[1], reverse=True),
            graph)

def insert_item(url, person, db_file):
    mimetype = "application/json"
    db = DB()

    if not db.open("{0}".format(db_file),
        DB.OWRITER | DB.OCREATE):
        print "Could not open database."
        return Response('{"What happened?": "Couldn\'t open the damn '\
            'database. Error: {0}"}'.format(unicode(db.error())),
            mimetype=mimetype)

    if is_url_in_db(db, url):
        return Response('{"What happened?": "Someone '\
            'tried to submit a duplicate URL."}',
            mimetype=mimetype)

    title = url
    summary = "~?~"
    try:
        thing = urlopen(url, timeout=10)
        soup = BeautifulSoup(thing)
        title = soup.title.string

        # Do some dumb summarizing if we can
        func = lambda a,v: a + " " + v
        visible_stuff = filter(visible, soup.findAll(text=True))
        summary = reduce(func, visible_stuff, "")[:300] + "..."
    except:
        pass
        #return Response('{"What happened?": '\
        #    'I dunno bs4 messed up somehow."}',
        #    mimetype=mimetype)

    created_at = int(mktime(datetime.now().utctimetuple()))

    record = {
        "created_at": created_at,
        "title": title,
        "url": url,
        "person": person,
        "summary": summary,
        "person_color": PERSON_COLORS[random.randint(0, len(PERSON_COLORS)-1)]
    }
    db.set(created_at, dumps(record))
    db.close()

    return Response('{"What happened?": "MUDADA"}',
        mimetype=mimetype)

def get_items(item_filter, db_file):
    items = []
    db = DB()
    if not db.open("{0}".format(db_file), DB.OREADER | DB.OCREATE):
        print "Could not open database."

    cur = db.cursor()
    cur.jump_back()
    while len(items) < FILTER_MAX:
        rec = cur.get(False)
        if not rec:
            break

        if item_filter(rec):
            items.append(rec)

        cur.step_back()
    cur.disable()
    db.close()

    sorted_items = sorted(items, key=get_key, reverse=True)
    sorted_items_for_viewing = [loads(item[1]) for item in sorted_items]
    return sorted_items_for_viewing
