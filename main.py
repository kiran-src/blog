from flask import Flask, render_template
import requests

app = Flask(__name__)

api = requests.get(url="https://api.npoint.io/c790b4d5cab58020d391")
api.raise_for_status()
posts = api.json()


@app.route('/')
def home():
    return render_template("index.html", posts=posts)


@app.route('/posts/<page>')
def post_page(page):
    post = {}
    for i in posts:
        if i['id'] == page:
            post = i
    return render_template("post.html", post=post)


if __name__ == "__main__":
    app.run(debug=True)
