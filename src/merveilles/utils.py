from constants import PERSON_COLORS, THUMBNAIL_SIZE, THUMBNAIL_DIR
from flask import Markup, current_app
from merveilles.filters import get_domain_filter
from PIL import Image
import re, requests, os, markdown, random, string

SCHEMA_VERSION = "0001"
USERS_PREFIX = "users"

def gen_thumbnail_for_url(url, filename):
    thumbnail_location = current_app.config['THUMBNAIL_DIR'] if current_app else THUMBNAIL_DIR
    is_image = url.lower().endswith(("jpg", "jpeg", "gif", "png"))
    if not is_image:
        return None

    ext = url.split(".")[-1]
    full_filepath = "{0}{1}.{2}".format(thumbnail_location,
        filename, ext.lower())

    if os.path.isfile(full_filepath):
        print "File exists: {}".format(full_filepath)
        return "thumbnails/{}.{}".format(filename, ext.lower())

    r = requests.get(url)

    if r.status_code == 200:
        with open("/tmp/tmp_img", 'wb') as f:
            for chunk in r.iter_content():
                f.write(chunk)

        im = Image.open("/tmp/tmp_img")
        im.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        print "Thumbnail writing to {}".format(full_filepath)
        if ext.lower() == 'jpg':
            im.save(full_filepath, 'JPEG')
        else:
            im.save(full_filepath, ext)

        return "thumbnails/{}.{}".format(filename, ext.lower())
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

def get_domain(raw_url):
    return get_domain_filter(raw_url['url'])

def visible(element):
    if element.parent.name in ['style', 'script', '[document]',
        'head', 'title', 'link', 'meta', 'h1', 'h2', 'h3', 'h4',
        'ul']:
        return False
    elif re.match('<!--.*-->', unicode(element)):
        return False

    return True

def get_effective_page(page, filter_func=lambda x: True):
    from merveilles.database import get_page_count
    page_count = get_page_count(filter_func)
    pages = range(0, page_count)
    requested_page = int(page)
    if page_count > 0 and requested_page < 0:
        requested_page = 0
    elif page_count > 0 and requested_page > pages[-1]:
        requested_page = pages[-1]

    return (pages, requested_page)

def random_password():
    myrg = random.SystemRandom()
    length = 32
    # If you want non-English characters, remove the [0:52]
    alphabet = string.letters[0:52] + string.digits
    pw = str().join(myrg.choice(alphabet) for _ in range(length))
    return pw

def sign_up(connection, username, password, admin=False):
    salt = gensalt()
    pwhash = _hash_pw(username, password, salt)
    user = connection.get(_get_user_str(username))

    if not user:
        new_user = {
            "api_version": SCHEMA_VERSION,
            "username": username,
            "password": pwhash,
            "salt": salt,
            "admin": admin
        }
        connection.set(_get_user_str(username), new_user)
        return (True, new_user)
    else:
        return (False, "Username already taken.")
    return (False, "Could not create user for some reason.")

def auth_user(email_address, password):
    connect_str = "http://localhost:8080/{}".format(email_address)
    response = requests.get(connect_str)

    if response.status_code == 200:
        user = response.json()
        hash = hashpw("{0}{1}".format(email_address, password), user.salt)

        if user.password == hash:
            return True

    return False
