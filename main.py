from flask import Flask, render_template, request
import requests
import smtplib
import os
from datetime import datetime

app = Flask(__name__)

api = requests.get(url="https://api.npoint.io/ac95d15dc3289a5388fd")
api.raise_for_status()
posts = api.json()


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
    post = {}
    print(page)
    for i in posts:
        if i['id'] == int(page):
            post = i
            break
    print(post)
    return render_template("post.html", post=post)


if __name__ == "__main__":
    app.run(debug=True)
