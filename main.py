from flask import Flask, render_template, request, redirect, url_for
import smtplib
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

posts = []

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def to_dict(self):
        posts = {}
        for i in self.__table__.columns:
            posts[i.name] = getattr(self, i.name)
        return posts


def update_posts():
    global posts
    posts = []
    for i in db.session.query(BlogPost).all():
        posts.append(i.to_dict())
    return posts

@app.route('/')
def home():
    update_posts()
    return render_template("index.html", posts=posts)

@app.route('/about')
def about():
    return render_template("about.html")

@app.route("/contact", methods=["POST", "GET"])
def contact():
    if request.method == "POST":
        data = request.form
        with smtplib.SMTP("smtp.gmail.com") as email:
            my_email = "ksetty12@gmail.com"
            password = os.environ.get("EMAIL_PASS")
            to_email = "kiransettyks@gmail.com"
            email.starttls()
            email.login(user=my_email, password=password)
            email.sendmail(from_addr=my_email, to_addrs=to_email,
                           msg=f"Subject:New Entry\n\nName: {data['name']}\nEmail: {data['email']}\nNumber: {data['phone']}\nMessage: {data['message']}")

        return render_template("contact.html", heading="Successfully sent your message")

    else:
        return render_template("contact.html", heading="Contact Me")
    # return render_template("form_entry.html", entry=request.form)

@app.route('/posts/<page>')
def post_page(page):
    post = {}
    for i in posts:
        if i['id'] == int(page):
            post = i
            break
    return render_template("post.html", post=post)


if __name__ == "__main__":
    app.run(debug=True)
