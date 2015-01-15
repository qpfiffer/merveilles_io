from datetime import datetime

def get_domain_filter(raw_url):
    domain = ""
    try:
        domain = raw_url.split("://")[1].split("/")[0]
    except IndexError:
        pass
    return domain

def file_size(size_str):
    # Found here: http://djangosnippets.org/snippets/1866/
    value = int(size_str)
    if value < 512000:
        value = value / 1024.0
        ext = 'kb'
    elif value < 4194304000:
        value = value / 1048576.0
        ext = 'mb'
    else:
        value = value / 1073741824.0
        ext = 'gb'
    return '%s %s' % (str(round(value, 2)), ext)

def unix_to_human(timestamp_str):
    time = float(timestamp_str)
    return unicode(datetime.fromtimestamp(time))

def is_video(item):
    video_urls = ['youtube.com', 'vimeo.com']
    return reduce(lambda a, v: a or (v.lower() in get_domain_filter(item['url']).lower()), video_urls, False)

def is_youtube(item):
    x = 'youtube.com' in get_domain_filter(item['url']).lower()
    y = 'youtube.com/watch' in item['url'].lower()
    return x and y

def youtube_vid(item):
    query_str = item['url'].split('?')[1].split("&")
    ve_str = filter(lambda a: 'v=' in a, query_str)[0]
    return ve_str.split('v=')[1]

def is_sound(item):
    video_urls = ['bandcamp.com', 'soundcloud.com']
    return reduce(lambda a, v: a or (v.lower() in get_domain_filter(item['url']).lower()), video_urls, False)
