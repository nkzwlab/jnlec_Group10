from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite3'
app.config['SQLALCHEMY_NATIVE_UNICODE'] = 'utf-8'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # disable warnings
app.permanent_session_lifetime = timedelta(minutes=15)

db = SQLAlchemy(app)

"""
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    books = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False,
                            default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.id'), nullable=False)  # lower case for table name

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"
"""


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    book_author = db.Column(db.String(100), nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # lower case for table name

    def __repr__(self):
        return f"Book('{self.title}','{self.book_author}')"


@ app.route("/")
def home():  # ホームページ
    return render_template("index.html")

# -------------------------------------------posts-------------------------------------------


"""
@ app.route("/post")
def post():
    # DBに投稿追加
    return render_template("post.html")


@ app.route("/create_post")
def create_post():
    # DBに投稿追加
    return render_template("create_post.html")


@ app.route("/delete_post", methods=["POST", "GET"])
def delete_post():
    # ここでDBから投稿削除。削除し終わったらリダイレクト
    flash(f"投稿を削除しました", "info")
    return redirect(url_for("bookshelf"))
"""
# -------------------------------------------book shelf-------------------------------------------


@ app.route("/bookshelf/")
def bookshelf():  # 本棚(本一覧)を表示
    Books = Book.query.all()
    return render_template("bookshelf.html", Books=Books)


@ app.route("/add_book/", methods=["POST", "GET"])
def add_book():
    # DBに本追加
    if request.method == "POST":
        title = request.form["title"]
        book_author = request.form["book_author"]
        book = Book(title=title, book_author=book_author)
        db.session.add(book)
        db.session.commit()
        flash(f"本を追加しました", "info")
        return redirect(url_for("bookshelf"))
    else:
        return render_template("add_book.html")


@ app.route("/update_book/<int:book_id>/", methods=["POST", "GET"])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    # if post.author != current_user:
    #   abort(403)
    if request.method == "POST":
        title = request.form["title"]
        book_author = request.form["book_author"]
        book.title = title
        book.book_author = book_author
        db.session.commit()
        flash(f"変更を保存しました", "info")
    else:
        title = book.title
        book_author = book.book_author

    return render_template("update_book.html", title=title, book_author=book_author)


@ app.route("/delete_book/<int:book_id>/", methods=["POST", "GET"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash(f"本を削除しました", "info")
    # ここでDBから本を削除。削除し終わったらリダイレクト
    return redirect(url_for("bookshelf"))


if __name__ == "__main__":
    db.create_all()  # create db
    app.run(debug=True)  # debug = True is for debugging.
