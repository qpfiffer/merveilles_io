import re

def get_domain(raw_url):
    return raw_url['url'].split("://")[1].split("/")[0]

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'link']:
        return False
    elif re.match('<!--.*-->', unicode(element)):
        return False

    return True
