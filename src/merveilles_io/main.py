from flask import Flask, render_template
import kyotocabinet

app = Flask(__name__)

@app.route("/")
def root():
    items = [{"person": "person{0}".format(i),
              "link":"http://link{0}.com".format(i)} for i in range(0,25)]
    return render_template("index.html", items=items)

def main_production():
    app.run(host="0.0.0.0")

def main_debug():
    app.run(debug=True)

if __name__ == "__main__":
    main_debug()
