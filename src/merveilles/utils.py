import re, requests, json

def paradise_compare(data, x, y):
    # we want things with huge numbers to be first
    return cmp(data[x].get('children_count', 0), data[y].get('children_count', 0))

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
    sorted_json = []
    for key in sorted_keys:
        sorted_json.append(paradise_json[key])


    return sorted_json

def get_domain(raw_url):
    return raw_url['url'].split("://")[1].split("/")[0]

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'link']:
        return False
    elif re.match('<!--.*-->', unicode(element)):
        return False

    return True
