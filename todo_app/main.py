from __future__ import annotations

import hashlib
import html
import os
import secrets
import sqlite3
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fapi import Cookie, FastAPI, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "todo.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Bootstrap To-Do App", lifespan=lifespan)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                is_done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
            """
        )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, _ = stored_hash.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(hash_password(password, salt), stored_hash)


def get_current_user(session_token: str | None = Cookie(default=None)) -> sqlite3.Row | None:
    if not session_token:
        return None

    with get_db() as conn:
        return conn.execute(
            """
            SELECT users.id, users.username
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token = ?
            """,
            (session_token,),
        ).fetchone()


def page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">
  <style>
    :root {{
      color-scheme: light;
    }}

    body {{
      min-height: 100vh;
      background:
        radial-gradient(circle at top left, rgba(13, 110, 253, .18), transparent 32rem),
        linear-gradient(135deg, #f8fafc 0%, #eef2f7 46%, #f8fafc 100%);
    }}

    .app-shell {{
      max-width: 980px;
    }}

    .glass-panel {{
      background: rgba(255, 255, 255, .84);
      border: 1px solid rgba(148, 163, 184, .28);
      box-shadow: 0 24px 70px rgba(15, 23, 42, .12);
      backdrop-filter: blur(18px);
    }}

    .brand-mark {{
      width: 44px;
      height: 44px;
      display: inline-grid;
      place-items: center;
      color: #fff;
      background: linear-gradient(135deg, #0d6efd, #20c997);
      border-radius: 14px;
    }}

    .todo-row {{
      transition: transform .15s ease, box-shadow .15s ease;
    }}

    .todo-row:hover {{
      transform: translateY(-1px);
      box-shadow: 0 10px 30px rgba(15, 23, 42, .08);
    }}

    .todo-done {{
      color: #64748b;
      text-decoration: line-through;
    }}
  </style>
</head>
<body>
  <main class="container py-5">
    <div class="app-shell mx-auto">
      {body}
    </div>
  </main>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    )


def auth_page(message: str = "") -> HTMLResponse:
    alert = (
        f'<div class="alert alert-warning border-0 rounded-4 mb-4">{message}</div>'
        if message
        else ""
    )
    return page(
        "Login | To-Do",
        f"""
<div class="row align-items-center g-4">
  <div class="col-lg-6">
    <div class="d-inline-flex align-items-center gap-3 mb-4">
      <span class="brand-mark"><i class="bi bi-check2-square fs-4"></i></span>
      <span class="fw-semibold text-primary-emphasis">Modern To-Do</span>
    </div>
    <h1 class="display-5 fw-bold text-dark mb-3">Plan your day with a clean, private task list.</h1>
    <p class="lead text-secondary mb-4">Create an account, sign in, and keep your tasks stored in a local SQLite database.</p>
    <div class="d-flex gap-3 text-secondary small">
      <span><i class="bi bi-database-check me-1"></i>SQLite</span>
      <span><i class="bi bi-shield-lock me-1"></i>Hashed passwords</span>
      <span><i class="bi bi-bootstrap me-1"></i>Bootstrap 5</span>
    </div>
  </div>

  <div class="col-lg-6">
    <div class="glass-panel rounded-4 p-4 p-md-5">
      {alert}
      <ul class="nav nav-pills nav-fill bg-light rounded-4 p-1 mb-4" role="tablist">
        <li class="nav-item" role="presentation">
          <button class="nav-link active rounded-3" data-bs-toggle="pill" data-bs-target="#login" type="button">Login</button>
        </li>
        <li class="nav-item" role="presentation">
          <button class="nav-link rounded-3" data-bs-toggle="pill" data-bs-target="#register" type="button">Register</button>
        </li>
      </ul>

      <div class="tab-content">
        <form id="login" class="tab-pane fade show active" method="post" action="/login">
          <div class="mb-3">
            <label class="form-label fw-semibold">Username</label>
            <input class="form-control form-control-lg rounded-3" name="username" autocomplete="username" required>
          </div>
          <div class="mb-4">
            <label class="form-label fw-semibold">Password</label>
            <input class="form-control form-control-lg rounded-3" name="password" type="password" autocomplete="current-password" required>
          </div>
          <button class="btn btn-primary btn-lg w-100 rounded-3" type="submit">
            <i class="bi bi-box-arrow-in-right me-2"></i>Login
          </button>
        </form>

        <form id="register" class="tab-pane fade" method="post" action="/register">
          <div class="mb-3">
            <label class="form-label fw-semibold">Username</label>
            <input class="form-control form-control-lg rounded-3" name="username" autocomplete="username" minlength="3" required>
          </div>
          <div class="mb-4">
            <label class="form-label fw-semibold">Password</label>
            <input class="form-control form-control-lg rounded-3" name="password" type="password" autocomplete="new-password" minlength="6" required>
          </div>
          <button class="btn btn-success btn-lg w-100 rounded-3" type="submit">
            <i class="bi bi-person-plus me-2"></i>Create account
          </button>
        </form>
      </div>
    </div>
  </div>
</div>
""",
    )


@app.get("/", response_class=HTMLResponse)
def home(session_token: str | None = Cookie(default=None)):
    user = get_current_user(session_token)
    if not user:
        return auth_page()

    with get_db() as conn:
        todos = conn.execute(
            "SELECT id, title, is_done, created_at FROM todos WHERE user_id = ? ORDER BY is_done, id DESC",
            (user["id"],),
        ).fetchall()

    open_count = sum(1 for todo in todos if not todo["is_done"])
    completed_count = len(todos) - open_count
    items = "".join(todo_item(todo) for todo in todos) or empty_state()
    safe_username = html.escape(user["username"])

    return page(
        "My To-Do List",
        f"""
<div class="glass-panel rounded-4 p-4 p-md-5">
  <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-4">
    <div>
      <div class="d-inline-flex align-items-center gap-3 mb-3">
        <span class="brand-mark"><i class="bi bi-check2-square fs-4"></i></span>
        <span class="badge text-bg-primary-subtle text-primary-emphasis rounded-pill px-3 py-2">Welcome, {safe_username}</span>
      </div>
      <h1 class="h2 fw-bold mb-1">Today&apos;s tasks</h1>
      <p class="text-secondary mb-0">{open_count} open, {completed_count} completed</p>
    </div>
    <form method="post" action="/logout">
      <button class="btn btn-outline-secondary rounded-3" type="submit">
        <i class="bi bi-box-arrow-right me-2"></i>Logout
      </button>
    </form>
  </div>

  <form class="row g-2 mb-4" method="post" action="/todos">
    <div class="col">
      <input class="form-control form-control-lg rounded-3" name="title" placeholder="Add a new task..." maxlength="180" required autofocus>
    </div>
    <div class="col-auto">
      <button class="btn btn-primary btn-lg rounded-3 px-4" type="submit">
        <i class="bi bi-plus-lg"></i>
      </button>
    </div>
  </form>

  <div class="vstack gap-3">
    {items}
  </div>
</div>
""",
    )


def todo_item(todo: sqlite3.Row) -> str:
    safe_title = html.escape(todo["title"])
    title_class = "todo-done" if todo["is_done"] else "text-dark"
    done_label = "Mark open" if todo["is_done"] else "Mark done"
    return f"""
<div class="todo-row bg-white border rounded-4 p-3 d-flex align-items-center gap-3">
  <form method="post" action="/todos/{todo["id"]}/toggle">
    <button class="btn btn-light border rounded-circle" type="submit" title="{done_label}">
      <i class="bi {'bi-check2 text-success' if todo["is_done"] else 'bi-circle text-secondary'}"></i>
    </button>
  </form>
  <div class="flex-grow-1 overflow-hidden">
    <div class="fw-semibold text-break {title_class}">{safe_title}</div>
    <div class="small text-secondary">Saved in database</div>
  </div>
  <form method="post" action="/todos/{todo["id"]}/delete">
    <button class="btn btn-outline-danger rounded-3" type="submit" title="Delete task">
      <i class="bi bi-trash3"></i>
    </button>
  </form>
</div>
"""


def empty_state() -> str:
    return """
<div class="text-center bg-white border rounded-4 p-5">
  <i class="bi bi-stars display-5 text-primary"></i>
  <h2 class="h5 fw-bold mt-3">No tasks yet</h2>
  <p class="text-secondary mb-0">Add your first task above and it will be saved to SQLite.</p>
</div>
"""


@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    username = username.strip()
    if len(username) < 3 or len(password) < 6:
        return auth_page("Username must be 3+ characters and password must be 6+ characters.")

    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, hash_password(password), now_iso()),
            )
    except sqlite3.IntegrityError:
        return auth_page("That username is already registered. Try logging in.")

    return create_session_redirect(username)


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username.strip(),),
        ).fetchone()

    if not user or not verify_password(password, user["password_hash"]):
        return auth_page("Invalid username or password.")

    return create_session_redirect(user["username"])


def create_session_redirect(username: str) -> RedirectResponse:
    token = secrets.token_urlsafe(32)
    with get_db() as conn:
        user = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        conn.execute(
            "INSERT INTO sessions (token, user_id, created_at) VALUES (?, ?, ?)",
            (token, user["id"], now_iso()),
        )

    response = RedirectResponse("/", status_code=303)
    response.set_cookie("session_token", token, httponly=True, samesite="lax")
    return response


@app.post("/logout")
def logout(response: Response, session_token: str | None = Cookie(default=None)):
    if session_token:
        with get_db() as conn:
            conn.execute("DELETE FROM sessions WHERE token = ?", (session_token,))

    redirect = RedirectResponse("/", status_code=303)
    redirect.delete_cookie("session_token")
    return redirect


@app.post("/todos")
def add_todo(title: str = Form(...), session_token: str | None = Cookie(default=None)):
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse("/", status_code=303)

    clean_title = title.strip()
    if clean_title:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO todos (user_id, title, created_at) VALUES (?, ?, ?)",
                (user["id"], clean_title, now_iso()),
            )

    return RedirectResponse("/", status_code=303)


@app.post("/todos/{todo_id}/toggle")
def toggle_todo(todo_id: int, session_token: str | None = Cookie(default=None)):
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse("/", status_code=303)

    with get_db() as conn:
        conn.execute(
            "UPDATE todos SET is_done = CASE is_done WHEN 1 THEN 0 ELSE 1 END WHERE id = ? AND user_id = ?",
            (todo_id, user["id"]),
        )

    return RedirectResponse("/", status_code=303)


@app.post("/todos/{todo_id}/delete")
def delete_todo(todo_id: int, session_token: str | None = Cookie(default=None)):
    user = get_current_user(session_token)
    if not user:
        return RedirectResponse("/", status_code=303)

    with get_db() as conn:
        conn.execute("DELETE FROM todos WHERE id = ? AND user_id = ?", (todo_id, user["id"]))

    return RedirectResponse("/", status_code=303)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    app_path = "main:app" if Path.cwd() == BASE_DIR else "todo_app.main:app"
    reload_dirs = [str(BASE_DIR)]
    if str(BASE_DIR.parent) not in sys.path:
        sys.path.insert(0, str(BASE_DIR.parent))
    uvicorn.run(app_path, host="127.0.0.1", port=port, reload=True, reload_dirs=reload_dirs)
