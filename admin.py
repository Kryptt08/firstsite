from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime, timezone
import hashlib
import secrets

from database import get_conn
from schemas import PetCreate, PetUpdate

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ── Simple session store (use Redis in production) ────────────────────────────
_sessions: dict[str, str] = {}

ADMIN_USERNAME = "admin"
# Default password: "bgsgg_admin" — CHANGE THIS before deploying!
ADMIN_PASSWORD_HASH = hashlib.sha256(b"bgsgg_admin").hexdigest()


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def get_session_user(request: Request) -> str | None:
    token = request.cookies.get("session")
    return _sessions.get(token)


def require_admin(request: Request):
    user = get_session_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


# ── Auth ──────────────────────────────────────────────────────────────────────

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
async def do_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    if username == ADMIN_USERNAME and hash_password(password) == ADMIN_PASSWORD_HASH:
        token = secrets.token_hex(32)
        _sessions[token] = username
        resp = RedirectResponse("/admin/", status_code=302)
        resp.set_cookie("session", token, httponly=True, samesite="lax")
        return resp
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid username or password"}
    )


@router.get("/logout")
async def logout(request: Request):
    token = request.cookies.get("session")
    _sessions.pop(token, None)
    resp = RedirectResponse("/admin/login", status_code=302)
    resp.delete_cookie("session")
    return resp


# ── Admin Dashboard ───────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, user: str = Depends(require_admin)):
    conn = get_conn()
    pets = conn.execute("SELECT * FROM pets ORDER BY value DESC").fetchall()
    recent = conn.execute(
        "SELECT * FROM value_history ORDER BY changed_at DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "pets": pets, "recent": recent, "user": user},
    )


# ── Pet Management (API endpoints used by admin panel JS) ────────────────────

@router.post("/pets/add")
async def add_pet(pet: PetCreate, user: str = Depends(require_admin)):
    conn = get_conn()
    try:
        conn.execute(
            """
            INSERT INTO pets (name, rarity, value, shiny_value, note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (pet.name, pet.rarity, pet.value, pet.shiny_value, pet.note),
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Could not add pet: {e}")
    conn.close()
    return {"success": True, "message": f"{pet.name} added"}


@router.patch("/pets/{pet_id}")
async def update_pet_value(
    pet_id: int,
    update: PetUpdate,
    user: str = Depends(require_admin),
):
    conn = get_conn()

    row = conn.execute("SELECT * FROM pets WHERE id = ?", (pet_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pet not found")

    old_value = row["value"]
    old_shiny = row["shiny_value"]

    # Write history entry
    conn.execute(
        """
        INSERT INTO value_history
            (pet_id, pet_name, old_value, new_value, old_shiny, new_shiny, changed_by, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            pet_id,
            row["name"],
            old_value,
            update.value,
            old_shiny,
            update.shiny_value,
            user,
            update.reason,
        ),
    )

    # Update pet
    conn.execute(
        """
        UPDATE pets
        SET value = ?, shiny_value = ?, note = ?, updated_at = datetime('now')
        WHERE id = ?
        """,
        (update.value, update.shiny_value, update.note, pet_id),
    )
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Value updated for {row['name']}"}


@router.delete("/pets/{pet_id}")
async def delete_pet(pet_id: int, user: str = Depends(require_admin)):
    conn = get_conn()
    row = conn.execute("SELECT name FROM pets WHERE id = ?", (pet_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Pet not found")
    conn.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"{row['name']} deleted"}
