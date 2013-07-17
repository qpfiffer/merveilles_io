from flask import Flask, render_template
from kyotocabinet import DB

app = Flask(__name__)

def get_links(num):
    db = DB()
    if not db.open("links.kct", DB.OREADER | DB.OCREATE):
        print "Could not open database."
    return db[:num]

@app.route("/")
def root():
    items = [{"person": "person{0}".format(i),
              "title": "Killing Ducks: A mortuary.",
              "link":"http://link{0}.com".format(i)} for i in range(0,25)]
    return render_template("index.html", items=items)

def main_production():
    app.run(host="0.0.0.0")

def main_debug():
    app.run(debug=True)

if __name__ == "__main__":
    main_debug()
