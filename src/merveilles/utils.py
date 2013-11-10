import re, requests, json, os
from networkx import Graph, spring_layout
from markdown import markdown
from flask import Markup
#from forceatlas import forceatlas2_layout
#from numpy import asscalar

def build_posts(location):
    posts = []
    blog_posts = os.listdir(location)
    blog_posts = filter(lambda x: x.endswith(".markdown"), blog_posts)
    for post in blog_posts:
        post_file = open("{0}/{1}".format(location, post))
        post_content = Markup(markdown(post_file.read()))
        posts.append(post_content)
        post_file.close()

    return posts


def paradise_compare(data, x, y):
    # we want things with huge numbers to be first
    return cmp(data[x].get('children_count', 0), data[y].get('children_count', 0))

def get_children_of(parent_id, paradise_json):
    children = [] # Return a list of dictionaries
    new_dict = {}

    for item in paradise_json:
        if paradise_json[item]["parent"] == parent_id:
            # Found a child
            child = {}
            child["id"] = item
            child["name"] = paradise_json[item]["name"]
            #child["size"] = paradise_json[item]["security"]
            children.append(child)
        else:
            new_dict[item] = paradise_json[item]

    for child in children:
        my_children = get_children_of(child["id"], new_dict)
        if len(my_children) == 0:
            pass
            #child["size"] = paradise_json[item]["security"]
            #child["size"] = 1000
        else:
            child["children"] = my_children

    return children

def get_paradise_json_for_d3():
    paradise_api = "http://api.xxiivv.com/?key=paradise"
    r = requests.get(paradise_api)
    paradise_json = r.json()
    PARADISE_ID = "1"

    tree = {}
    tree["id"] = PARADISE_ID
    tree["name"] = paradise_json[PARADISE_ID]["name"]
    #tree["size"] = paradise_json[PARADISE_ID]["security"]
    tree["children"] = get_children_of(PARADISE_ID, paradise_json)

    return tree

def get_paradise_items():
    paradise_api = "http://api.xxiivv.com/?key=paradise"
    r = requests.get(paradise_api)
    paradise_json = r.json()

    for item in paradise_json:
        parent_key = paradise_json[item]["parent"]
        parent = paradise_json.get(parent_key)

        if not parent:
            continue;

        if paradise_json[parent_key].get("children_count", False):
            paradise_json[parent_key]["children_count"] = paradise_json[parent_key]["children_count"] + 1
        else:
            paradise_json[parent_key]["children_count"] = 1

    def cmp_func(x,y):
        return paradise_compare(paradise_json, x, y)

    sorted_keys = sorted(paradise_json, cmp=cmp_func, reverse=True)
    sorted_json = {}
    for key in sorted_keys:
        item = paradise_json[key]
        item["id"] = key
        sorted_json[key] = item

    return sorted_json

def gen_paradise_graph(items):
    g = Graph()
    for item in items:
        g.add_node(item, **items[item])

    for item in items:
        g.add_edge(item, items[item]["parent"])

    print "Starting spring layout generation..."
    the_graph = forceatlas2_layout(g, iterations=1)
    print "Finished spring layout."

    for item in the_graph:
        try:
            items[item]["x"] = asscalar(the_graph[item][0])
            items[item]["y"] = asscalar(the_graph[item][1])
        except KeyError as e:
            print "{} not found.".format(e)
            continue

    return items

def get_domain(raw_url):
    return raw_url['url'].split("://")[1].split("/")[0]

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'link']:
        return False
    elif re.match('<!--.*-->', unicode(element)):
        return False

    return True
