from constants import PERSON_COLORS, THUMBNAIL_SIZE, THUMBNAIL_DIR
from flask import Markup
from networkx import Graph, spring_layout
from PIL import Image
import re, requests, json, os, markdown

def gen_thumbnail_for_url(url, filename):
    is_image = url.lower().endswith(("jpg", "jpeg", "gif", "png"))

    if not is_image:
        return None

    r = requests.get(url)

    if r.status_code == 200:
        with open("/tmp/tmp_img", 'wb') as f:
            for chunk in r.iter_content():
                f.write(chunk)

        ext = url.split(".")[-1]
        im = Image.open("/tmp/tmp_img")
        im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        full_filepath = "{0}{1}.{2}".format(THUMBNAIL_DIR, filename, ext.lower())
        if ext.lower() == 'jpg':
            im.save(full_filepath, 'JPEG')
        else:
            im.save(full_filepath, ext)

        return full_filepath
    return None

def slugify_post(post):
    cleaned = post.split('.')[0] # Remove file extension
    cleaned = cleaned.replace('_', '-')
    return cleaned

def build_posts(location):
    posts = []
    blog_posts = os.listdir(location)
    blog_posts = filter(lambda x: x.endswith(".markdown"), blog_posts)
    for post in blog_posts:
        post_file = open("{0}/{1}".format(location, post))
        md = markdown.Markdown(extensions = ['meta'])

        post_html = md.convert(post_file.read())
        post_content = Markup(post_html)

        author = md.Meta['author'][0]
        author_color = [ord(x) for x in author]
        author_color = PERSON_COLORS[len(PERSON_COLORS) - 1 % sum(author_color)]

        post_cleaned = {
            'author': author,
            'author_color': author_color,
            'title': md.Meta['title'][0],
            'date': md.Meta['date'][0],
            'preview': md.Meta['preview'][0],
            'content': post_content,
            'slug': slugify_post(post)
        }

        posts.append(post_cleaned)
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
