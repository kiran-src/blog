from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO Blog DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', "sqlite:///blog.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# LOGIN FUNCTIONALITY
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


# CONFIGURE TABLES


class Users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    posts = db.relationship('BlogPost', backref='users', lazy=True)
    user_comments = db.relationship('PostComments', backref='users', lazy=True)


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250), nullable=False)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    blog_comments = db.relationship('PostComments', backref='blog_posts', lazy=True)


class PostComments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


def admin_only(function):
    def wrapper():

        if int(current_user.id) == 1:
            function()
        else:
            abort(403)

    return wrapper


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    if current_user.is_authenticated:
        print(current_user.id)
    return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if current_user.is_authenticated:
            flash("You are already logged in. Log out to continue")
        elif Users.query.filter_by(email=form.email.data).first() is None:
            new_user = Users(
                email=form.email.data,
                password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8),
                name=form.name.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
        else:
            flash("That email has already has an account. Log in instead")
            return redirect(url_for('login'))
    return render_template("register.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print('A')
        user = Users.query.filter_by(email=form.email.data).first()
        print('B')
        if user is None:
            print('C')
            flash('That email is not registered. Register first to log in')
            # return redirect(url_for('login'))
        elif check_password_hash(user.password, form.password.data):
            print('D')
            flash('You were successfully logged in')
            login_user(user)
            return redirect(url_for('get_all_posts'))
        else:
            print('E')
            flash('That password is incorrect. Try again')
            # redirect(url_for('login'))
    return render_template("login.html", form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=['POST', 'GET'])
def show_post(post_id):
    comment = CommentForm()
    comment_history = PostComments.query.filter_by(blog_id=post_id)
    requested_post = BlogPost.query.get(post_id)
    if comment.validate_on_submit():
        if not current_user.is_authenticated:
            abort(404)
        new_comment = PostComments(
            author=current_user.name,
            body=comment.body.data,
            date=date.today().strftime("%B %d, %Y"),
            blog_id=post_id,
            person_id=current_user.id
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id))

    return render_template("post.html", comment=comment, post=requested_post, history=comment_history, logged_in=current_user.is_authenticated)


@app.route("/about")
def about():
    return render_template("about.html", logged_in=current_user.is_authenticated)


@app.route("/contact")
def contact():
    return render_template("contact.html", logged_in=current_user.is_authenticated)


@app.route("/new-post", methods=['POST', 'GET'])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user.name,
            date=date.today().strftime("%B %d, %Y"),
            person_id=current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/edit-post/<int:post_id>", methods=['POST', 'GET'])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=current_user.name,
        body=post.body,
        person_id=current_user.id
    )
    if post.person_id == current_user.id or current_user.id == 1:
        if edit_form.validate_on_submit():
            post.title = edit_form.title.data
            post.subtitle = edit_form.subtitle.data
            post.img_url = edit_form.img_url.data
            post.body = edit_form.body.data
            db.session.commit()
            return redirect(url_for("show_post", post_id=post.id))
    else:
        # return render_template("403.html"), 403
        abort(403)

    return render_template("make-post.html", form=edit_form, logged_in=current_user.is_authenticated)


@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    if BlogPost.query.get(post_id).person_id == current_user.id or current_user.id == 1:
        post_to_delete = BlogPost.query.get(post_id)
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    else:
        abort(403)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
