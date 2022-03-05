from flask import Flask, render_template, request, redirect, url_for
import smtplib
import os
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from flask_ckeditor import CKEditorField
from wtforms.validators import DataRequired, URL, length
from flask_ckeditor import CKEditor, CKEditorField
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CKEDITOR_PKG_TYPE'] = 'standard'
db = SQLAlchemy(app)
Bootstrap(app)
ck = CKEditor(app)


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), length(max=200)])
    subtitle = StringField('Subtitle', validators=[DataRequired(), length(max=300)])
    name = StringField('Author Name', validators=[DataRequired(), length(max=80)])
    image = StringField('Header Background Image URL', validators=[DataRequired(), URL()])
    content = CKEditorField('Body Content', validators=[DataRequired()])
    submit = SubmitField('Submit')


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


posts = []


def update_posts():
    global posts
    posts = []
    for i in db.session.query(BlogPost).all():
        posts.append(i.to_dict())


update_posts()
for i in posts:
    print(i)

def find_post(post_id):
    for i in posts:
        if i['id'] == int(post_id):
            return i
    return 0


@app.route('/')
def home():
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
    post = find_post(page)
    if post == 0:
        return "<h1>Error: Post not Found</h1>"
    return render_template("post.html", post=post)


@app.route('/new-post', methods=['POST', 'GET'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        now = datetime.now()
        print(f"{now.day} {now.strftime('%B')} {now.year}")
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            date=f"{now.day} {now.strftime('%B')} {now.year}",
            body=form.content.data,
            author=form.name.data,
            img_url=form.image.data
        )
        db.session.add(new_post)
        db.session.commit()
        update_posts()
        return redirect(url_for("home"))
    return render_template("make-post.html", form=form)


@app.route('/edit/<post_id>', methods=['POST', 'GET'])
def edit(post_id):
    post = find_post(post_id)
    if post == 0:
        return "<h1>Error: Post not Found</h1>"
    form = PostForm()
    if form.validate_on_submit():
        now = datetime.now()
        edit_post = BlogPost.query.filter_by(id=post_id).first()
        edit_post.title = form.title.data
        edit_post.subtitle = form.subtitle.data
        edit_post.author = form.name.data
        edit_post.img_url = form.image.data
        edit_post.body = form.content.data
        edit_post.date = f"{now.day} {now.strftime('%B')} {now.year}"
        db.session.commit()
        update_posts()
        return redirect(url_for("home"))
    form = PostForm(
        title=post['title'],
        subtitle=post['subtitle'],
        name=post['author'],
        image=post['img_url'],
        content=post['body']
    )
    return render_template("make-post.html", form=form)

@app.route('/delete/<post_id>')
def delete(post_id):
    post = find_post(post_id)
    if post == 0:
        return "<h1>Error: Post not Found</h1>"
    del_post = BlogPost.query.filter_by(id=post_id).first()
    db.session.delete(del_post)
    db.session.commit()
    update_posts()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
