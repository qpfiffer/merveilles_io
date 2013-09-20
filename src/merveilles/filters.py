from datetime import datetime

def get_domain_filter(raw_url):
    return raw_url.split("://")[1].split("/")[0]

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
