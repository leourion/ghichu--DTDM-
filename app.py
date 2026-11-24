"""Ứng dụng ghi chú cá nhân: Flask, Jinja2 và PostgreSQL."""
import os
import secrets
from functools import wraps

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
DATABASE_URL = os.environ["DATABASE_URL"]


def db():
    # Mỗi lần truy vấn dùng một kết nối và tự đóng sau khi kết thúc.
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


@app.context_processor
def csrf_context():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return {"csrf_token": session["csrf_token"]}


@app.before_request
def protect_post():
    if request.method == "POST" and not secrets.compare_digest(
        session.get("csrf_token", ""), request.form.get("csrf_token", "")
    ):
        abort(400)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not (3 <= len(username) <= 50) or len(password) < 8:
            flash("Tên đăng nhập 3–50 ký tự, mật khẩu ít nhất 8 ký tự.")
        else:
            try:
                with db() as conn:
                    conn.execute(
                        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                        (username, generate_password_hash(password)),
                    )
                flash("Đăng ký thành công. Hãy đăng nhập.")
                return redirect(url_for("login"))
            except psycopg.errors.UniqueViolation:
                flash("Tên đăng nhập đã tồn tại.")
    return render_template("auth.html", title="Đăng ký", action="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        with db() as conn:
            user = conn.execute(
                "SELECT id, username, password_hash FROM users WHERE username = %s",
                (request.form.get("username", "").strip(),),
            ).fetchone()
        if user and check_password_hash(user["password_hash"], request.form.get("password", "")):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Đăng nhập thành công.")
            return redirect(url_for("index"))
        flash("Sai tên đăng nhập hoặc mật khẩu.")
    return render_template("auth.html", title="Đăng nhập", action="login")


@app.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/")
@login_required
def index():
    with db() as conn:
        notes = conn.execute(
            "SELECT id, title, content, updated_at FROM notes "
            "WHERE user_id = %s ORDER BY updated_at DESC, id DESC",
            (session["user_id"],),
        ).fetchall()
    return render_template("index.html", notes=notes)


def own_note(note_id):
    # Mọi thao tác đều giới hạn theo user_id, tránh xem/sửa ghi chú của người khác.
    with db() as conn:
        note = conn.execute(
            "SELECT id, title, content FROM notes WHERE id = %s AND user_id = %s",
            (note_id, session["user_id"]),
        ).fetchone()
    if note is None:
        abort(404)
    return note


@app.route("/notes/new", methods=["GET", "POST"])
@login_required
def create_note():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title or len(title) > 120:
            flash("Tiêu đề cần có 1–120 ký tự.")
        else:
            with db() as conn:
                conn.execute(
                    "INSERT INTO notes (user_id, title, content) VALUES (%s, %s, %s)",
                    (session["user_id"], title, content),
                )
            flash("Đã thêm ghi chú.")
            return redirect(url_for("index"))
        return render_template("form.html", title="Thêm ghi chú", note={"title": title, "content": content})
    return render_template("form.html", title="Thêm ghi chú", note=None)


@app.get("/notes/<int:note_id>")
@login_required
def view_note(note_id):
    return render_template("view.html", note=own_note(note_id))


@app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
@login_required
def edit_note(note_id):
    note = own_note(note_id)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        if not title or len(title) > 120:
            flash("Tiêu đề cần có 1–120 ký tự.")
            return render_template("form.html", title="Sửa ghi chú", note={"title": title, "content": content})
        with db() as conn:
            conn.execute(
                "UPDATE notes SET title = %s, content = %s, updated_at = NOW() "
                "WHERE id = %s AND user_id = %s",
                (title, content, note_id, session["user_id"]),
            )
        flash("Đã sửa ghi chú.")
        return redirect(url_for("view_note", note_id=note_id))
    return render_template("form.html", title="Sửa ghi chú", note=note)


@app.post("/notes/<int:note_id>/delete")
@login_required
def delete_note(note_id):
    own_note(note_id)
    with db() as conn:
        conn.execute(
            "DELETE FROM notes WHERE id = %s AND user_id = %s",
            (note_id, session["user_id"]),
        )
    flash("Đã xóa ghi chú.")
    return redirect(url_for("index"))
