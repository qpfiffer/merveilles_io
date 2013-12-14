from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date
from flask import Response, current_app
from kyotocabinet import DB
from json import dumps, loads
from time import mktime
from urllib2 import urlopen
from utils import gen_thumbnail_for_url
import random

from constants import FILTER_MAX, PERSON_COLORS
from utils import get_domain, visible

def search_func(record, search_string):
    for item in record:
        if search_string in unicode(record[item]):
            return True
    return False

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
        print "Could not open database. (Top things)"

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

        response = {}
        response['What happened?'] = "Couldn't open the damn database. Error: {0}".format(db.error())
        return Response(dumps(response), mimetype=mimetype)

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

    is_image = url.lower().endswith(("jpg", "jpeg", "gif", "png"))
    thumbnail = gen_thumbnail_for_url(url, str(created_at))

    record = {
        "created_at": created_at,
        "title": title,
        "url": url,
        "person": person,
        "summary": summary,
        "person_color": PERSON_COLORS[random.randint(0, len(PERSON_COLORS)-1)],
        "is_image": is_image,
        "thumbnail": thumbnail
    }
    db.set(created_at, dumps(record))
    db.close()

    return Response('{"What happened?": "MUDADA"}',
        mimetype=mimetype)

def get_items(item_filter, db_file, page=0):
    item_iter = 0
    items = []
    db = DB()
    if not db.open("{0}".format(db_file), DB.OREADER | DB.OCREATE):
        print "Could not open database."

    cur = db.cursor()
    cur.jump_back()
    while len(items) < FILTER_MAX:
        if item_iter != (FILTER_MAX * page):
            item_iter = item_iter + 1
            cur.step_back()
            continue

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

def get_all_items(db_file):
    items = []
    db = DB()
    if not db.open("{0}".format(db_file), DB.OREADER | DB.OCREATE):
        print "Could not open database."

    cur = db.cursor()
    cur.jump()
    while True:
        rec = cur.get(False)
        if not rec:
            break
        items.append(rec)
        cur.step()

    cur.disable()
    db.close()

    sorted_items_for_viewing = [loads(item[1]) for item in items]
    return sorted_items_for_viewing

def get_post_num(post_num, db_file):
    item = None
    db = DB()
    if not db.open("{0}".format(db_file), DB.OREADER | DB.OCREATE):
        print "Could not open database."

    cur = db.cursor()
    cur.jump()
    i = 0
    while True:
        rec = cur.get(False)
        if not rec:
            break

        if i == post_num:
            item = rec

        cur.step()
        i = i + 1

    cur.disable()
    db.close()

    if item is not None:
        return loads(item[1])
    return dict()

def get_items_last_X_days(db_file, X, munge=True):
    dates = {}
    db = DB()
    if not db.open("{0}".format(db_file), DB.OREADER | DB.OCREATE):
        print "Could not open database."

    X_days_ago = datetime.now() - timedelta(days=X)

    cur = db.cursor()
    cur.jump_back()
    while True:
        rec = cur.get(False)
        if not rec:
            break

        loaded = loads(rec[1])
        unix = float(loaded['created_at'])
        time = datetime.fromtimestamp(unix)

        if time > X_days_ago:
            if munge:
                date_obj = date(year=time.year, month=time.month, day=time.day)
            else:
                date_obj = time
            # Javascript expects Date.UTC to spit out dates of a certain
            # length.
            day_unix = int(mktime(date_obj.timetuple()))*1000
            if dates.get(day_unix, False) == False:
                dates[day_unix] = {loaded["person"]: 1}
            else:
                relevant_dict = dates[day_unix]

                if relevant_dict.get(loaded["person"], False) == False:
                    relevant_dict[loaded["person"]] = 1
                else:
                    relevant_dict[loaded["person"]] = relevant_dict[loaded["person"]] + 1
        else:
            break;

        cur.step_back()
    cur.disable()
    db.close()

    return dates

def aggregate_by_hour(db_file):
    # Initialize the dict with each hour
    hours = {key: 0 for key in range(0,24)}
    db = DB()

    if not db.open("{0}".format(db_file), DB.OREADER | DB.OCREATE):
        print "Could not open database."

    cur = db.cursor()
    cur.jump_back()

    while True:
        rec = cur.get(False)
        if not rec:
            break

        loaded = loads(rec[1])
        unix = float(loaded['created_at'])
        time = datetime.fromtimestamp(unix)

        hours[time.hour] = hours[time.hour] + 1

        cur.step_back()
    cur.disable()
    db.close()

    hours = [{'name': "{}:00".format(key), 'data': [hours[key]]} for key in hours]
    return hours

def get_page_count():
    count = 0
    db = DB()
    db_file = current_app.config['DB_FILE']
    if not db.open("{0}".format(db_file), DB.OREADER | DB.OCREATE):
        print "Could not open database (meta info)."
    count = db.count()
    db.close()
    return count / FILTER_MAX

