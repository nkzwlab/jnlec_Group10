from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt  # PWのハッシング用 6.30 hhiromasa
# ログイン管理用 6.30 hhiromasa
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = "123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite3'
app.config['SQLALCHEMY_NATIVE_UNICODE'] = 'utf-8'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # disable warnings
app.permanent_session_lifetime = timedelta(
    minutes=15)  # セッション時間。使わないかも  6.29 hhiromasa

bcrypt = Bcrypt(app)  # PWのハッシング用 6.30 hhiromasa
login_manager = LoginManager(app)  # ログイン管理用 6.30 hhiromasa
login_manager.login_view = 'login'  # ログイン管理用 6.30 hhiromasa
login_manager.login_message = 'そのページを閲覧するにはログインが必要です。'
login_manager.login_message_category = 'warning'

db = SQLAlchemy(app)

# -------------------------------------------models  6.29 hhiromasa-------------------------------------------


# ユーザ管理、本の感想文の投稿とかできたら面白そう。

# ユーザセッション管理用//////////////
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# ////////////////////////////


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    #email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    #posts = db.relationship('Post', backref='author', lazy=True)
    books = db.relationship('Book', backref='author', lazy=True)

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



class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    book_author = db.Column(db.String(100), nullable=False)
    # ユーザとの関連付け。ユーザ管理がまだ完成してないのでコメントアウト 6.29 hhiromasa
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Book('{self.title}','{self.book_author}')"


@ app.route("/")
def home():  # ホームページ
    return render_template("index.html")


# -------------------------------------------posts 6.30 hhiromasa-------------------------------------------


@ app.route("/register/", methods=["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('bookshelf'))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(
            password).decode('utf-8')
        user = User(username=username, password=hashed_password)
        if User.query.filter_by(username=username).first() == None:
            db.session.add(user)
            db.session.commit()
            flash(f"ようこそ{username}さん！", "info")
            return redirect(url_for("login"))
        else:
            flash(f"既に同じ名前のアカウントが存在します。", "warning")
            return render_template("register.html")

    else:
        return render_template("register.html")


@ app.route("/login/", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('bookshelf'))

    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and bcrypt.check_password_hash(user.password, request.form["password"]):
            login_user(user)
            flash(f"ログインできました。", "info")
            return redirect(url_for('bookshelf'))
        else:
            flash(f"ログインに失敗しました。", "info")
    return render_template("login.html")


@ app.route("/logout/")
def logout():
    logout_user()
    flash(f"ログアウトしました。", "info")
    return redirect(url_for('login'))

    # -------------------------------------------posts 6.29 hhiromasa-------------------------------------------



#本の感想文の投稿とかできたら面白そう
@ app.route("/post/")
def post():
    # DBに投稿追加
    return render_template("post.html")


@ app.route("/create_post/")
def create_post():
    # DBに投稿追加
    return render_template("create_post.html")


@ app.route("/delete_post/", methods=["POST", "GET"])
def delete_post():
    # ここでDBから投稿削除。削除し終わったらリダイレクト
    flash(f"投稿を削除しました", "info")
    return redirect(url_for("bookshelf"))

# -------------------------------------------book shelf 6.29 hhiromasa-------------------------------------------


@ app.route("/bookshelf/")
@login_required
def bookshelf():  # 本棚(本一覧)を表示
    Books = Book.query.filter_by(author=current_user).all()
    return render_template("bookshelf.html", Books=Books)


@ app.route("/add_book/", methods=["POST", "GET"])
@login_required
def add_book():
    # もしrequestがPOSTだったら(formが送信されたら)formの内容をDBに追加
    if request.method == "POST":
        title = request.form["title"]
        book_author = request.form["book_author"]
        book = Book(title=title, book_author=book_author,
                    author=current_user)
        db.session.add(book)
        db.session.commit()
        flash(f"本を追加しました", "info")
        return redirect(url_for("bookshelf"))
    else:  # もしrequestがGETだったら(formを開いただけなら)formを表示
        return render_template("add_book.html")


@ app.route("/update_book/<int:book_id>/", methods=["POST", "GET"])
@login_required
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    # if post.author != current_user: <-ユーザ管理だからあとで追加する
    #   abort(403)
    if request.method == "POST":  # もしrequestがPOSTだったら(formが送信されたら)DBの内容を更新
        title = request.form["title"]
        book_author = request.form["book_author"]
        book.title = title
        book.book_author = book_author
        db.session.commit()
        flash(f"変更を保存しました", "info")
    else:  # 　もしrequestがGETだったら(formを開いただけなら)既存情報をformのvalueに入れた状態で表示
        title = book.title
        book_author = book.book_author

    return render_template("update_book.html", title=title, book_author=book_author)


@ app.route("/delete_book/<int:book_id>/", methods=["POST", "GET"])
@login_required
def delete_book(book_id):
    # ここでDBから本を削除。削除し終わったらリダイレクト
    # 多分「本当に削除しますか」って確認した方が親切
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash(f"本を削除しました", "info")
    return redirect(url_for("bookshelf"))


# -------------------------------------------アプリをrun-------------------------------------------
if __name__ == "__main__":
    db.create_all()  # create db
    app.run(debug=True)  # debug = True はデバッグ用。実装する時は絶対にFalseにしないといけない
