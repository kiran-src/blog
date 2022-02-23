from flask import Flask, render_template
import requests
from datetime import datetime

app = Flask(__name__)

api = requests.get(url="https://api.npoint.io/6c3754b7be2b015f9e72")
api.raise_for_status()
posts = api.json()


@app.route('/')
def home():
    return render_template("index.html", posts=posts)

@app.route('/contact')
def contact():
    return render_template("contact.html", posts=posts)

@app.route('/about')
def about():
    return render_template("about.html", posts=posts)


@app.route('/posts/<page>')
def post_page(page):
    post = {}
    print(page)
    for i in posts:
        if i['id'] == int(page):
            post = i
            break
    print(post)
    dt = datetime.now()
    date = f"{dt.day} {dt.strftime('%B')} {dt.year}"
    return render_template("post.html", post=post, date=date)


if __name__ == "__main__":
    app.run(debug=True)
