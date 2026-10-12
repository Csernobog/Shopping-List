from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import mariadb
import os

class DeleteItem(BaseModel):
    mit: str
    honnan: Optional[str] = None

load_dotenv()

app = FastAPI(
    title="Bevásárlólista API",
    version="0.2"
)

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

# ------------------------------------------------------------
# ADATBÁZIS
# ------------------------------------------------------------

def get_db():
    try:
        return mariadb.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

    except mariadb.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Adatbázis kapcsolat hiba: {e}"
        )


# ------------------------------------------------------------
# MODELLEK
# ------------------------------------------------------------

class UjTetel(BaseModel):
    mit: str
    mennyit: Optional[float] = None
    me: Optional[str] = None
    honnan: Optional[str] = None


# ------------------------------------------------------------
# ALAP TESZT
# ------------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "bevlist",
        "status": "ok",
        "version": "0.2"
    }


@app.get("/api/db-test")
def db_test():

    db = get_db()

    try:
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        return {
            "database": "ok",
            "result": result[0]
        }

    finally:
        db.close()


# ------------------------------------------------------------
# HOZZÁADÁS
# ------------------------------------------------------------

@app.post("/api/add")
def add_item(item: UjTetel):

    mit = item.mit.strip()

    if not mit:
        raise HTTPException(
            status_code=400,
            detail="'mit' mező kötelező"
        )

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute(
            """
            INSERT INTO bevasarlas
                (
                    mit,
                    mennyit,
                    mertekegyseg,
                    honnan,
                    teljesult
                )
            VALUES
                (?, ?, ?, ?, 0)
            """,
            (
                mit,
                item.mennyit,
                item.me,
                item.honnan
            )
        )

        db.commit()

        return {
            "status": "ok",
            "id": cursor.lastrowid,
            "mit": mit,
            "mennyit": item.mennyit,
            "me": item.me,
            "honnan": item.honnan,
            "teljesult": False
        }

    except mariadb.Error as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"SQL hiba: {e}"
        )

    finally:
        db.close()


# ------------------------------------------------------------
# TELJES LISTA
# ------------------------------------------------------------

@app.get("/api/list")
def list_all():

    db = get_db()

    try:
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                mit,
                mennyit,
                mertekegyseg,
                honnan,
                teljesult
            FROM bevasarlas
            ORDER BY
                teljesult ASC,
                honnan ASC,
                id ASC
            """
        )

        return cursor.fetchall()

    finally:
        db.close()


# ------------------------------------------------------------
# LISTA BOLT SZERINT
# ------------------------------------------------------------

@app.get("/api/list/{honnan}")
def list_store(honnan: str):

    db = get_db()

    try:
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                mit,
                mennyit,
                mertekegyseg,
                honnan,
                teljesult
            FROM bevasarlas
            WHERE honnan = ?
            ORDER BY
                teljesult ASC,
                id ASC
            """,
            (honnan,)
        )

        return cursor.fetchall()

    finally:
        db.close()


# ------------------------------------------------------------
# TELJESÜLT
# ------------------------------------------------------------

@app.post("/api/done/{mit}")
def done_item(mit: str):

    db = get_db()

    try:
        cursor = db.cursor()

        # Először megnézzük, létezik-e
        cursor.execute(
            """
            SELECT id, teljesult
            FROM bevasarlas
            WHERE mit = ?
            LIMIT 1
            """,
            (mit,)
        )

        item = cursor.fetchone()

        if item is None:
            raise HTTPException(
                status_code=404,
                detail=f"Nincs ilyen tétel: {mit}"
            )

        # Utána állítjuk teljesültre
        cursor.execute(
            """
            UPDATE bevasarlas
            SET teljesult = 1
            WHERE id = ?
            """,
            (item[0],)
        )

        db.commit()

        return {
            "status": "ok",
            "id": item[0],
            "mit": mit,
            "teljesult": True
        }

    finally:
        db.close()

# ------------------------------------------------------------
# VISSZAÁLLÍTÁS NEM TELJESÜLTRE
# később a weboldali kipipálásnál jól fog jönni
# ------------------------------------------------------------
@app.post("/api/undone/{mit}")
def undone_item(mit: str):

    db = get_db()

    try:
        cursor = db.cursor()

        # Először megnézzük, létezik-e
        cursor.execute(
            """
            SELECT id, teljesult
            FROM bevasarlas
            WHERE mit = ?
            LIMIT 1
            """,
            (mit,)
        )

        item = cursor.fetchone()

        if item is None:
            raise HTTPException(
                status_code=404,
                detail=f"Nincs ilyen tétel: {mit}"
            )

        # Visszaállítjuk nem teljesültre
        cursor.execute(
            """
            UPDATE bevasarlas
            SET teljesult = 0
            WHERE id = ?
            """,
            (item[0],)
        )

        db.commit()

        return {
            "status": "ok",
            "id": item[0],
            "mit": mit,
            "teljesult": False
        }

    finally:
        db.close()
# ------------------------------------------------------------
# TÖRLÉS NÉV ALAPJÁN
# ------------------------------------------------------------

@app.delete("/api/delete/{mit}")
def delete_item(mit: str):

    db = get_db()

    try:
        cursor = db.cursor()

        # Előbb ellenőrizzük, hogy létezik-e ilyen tétel
        cursor.execute(
            """
            SELECT id, mit
            FROM bevasarlas
            WHERE mit = ?
            LIMIT 1
            """,
            (mit,)
        )

        item = cursor.fetchone()

        if item is None:
            raise HTTPException(
                status_code=404,
                detail=f"Nincs ilyen tétel: {mit}"
            )

        # Ha létezik, töröljük
        cursor.execute(
            """
            DELETE FROM bevasarlas
            WHERE id = ?
            """,
            (item[0],)
        )

        db.commit()

        return {
            "status": "ok",
            "id": item[0],
            "mit": item[1],
            "deleted": True
        }

    finally:
        db.close()

# ------------------------------------------------------------
# MINDEN TÖRLÉSE
# ------------------------------------------------------------

@app.delete("/api/delete-all")
def delete_all():

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute(
            """
            DELETE FROM bevasarlas
            """
        )

        db.commit()

        return {
            "status": "ok",
            "deleted": cursor.rowcount
        }

    finally:
        db.close()
        
@app.post("/api/delete")
def delete_item(item: DeleteItem):
    mit = item.mit.strip()
    honnan = (item.honnan or "").strip() or None

    if not mit:
        raise HTTPException(
            status_code=400,
            detail="Hiányzik a termék neve."
        )

    conn = get_db()

    try:
        cur = conn.cursor()

        if honnan is None:
            # Minden boltból, minden előfordulás
            cur.execute(
                "DELETE FROM bevasarlas WHERE mit = ?",
                (mit,)
            )
        else:
            # Csak a megadott boltból,
            # minden előfordulás
            cur.execute(
                """
                DELETE FROM bevasarlas
                WHERE mit = ? AND honnan = ?
                """,
                (mit, honnan)
            )

        deleted = cur.rowcount
        conn.commit()

    finally:
        conn.close()
# Ragozás:)
    first_mit = mit[0].lower()   
    first_honnan = honnan[0].lower() if honnan else None
    if first_mit in "aeiouáéíóöőúüű":
        article = "az"
    else:
        article = "a"
    if first_honnan and first_honnan in "aeiouáéíóöőúüű":
        honnan_article = "az"
    else:
        honnan_article = "a"
    if deleted == 0:
        if honnan:
            response = (
                f"{article} {mit} nem szerepel "
                f"{honnan_article} {honnan} listáján."
            )
        else:
            response = (
                f"{article} {mit} nem szerepel "
                "a bevásárlólistán."
            )

    elif honnan:
        response = (
            f"Töröltem {article} {mit} terméket "
            f"{honnan_article} {honnan} listájáról."
        )

    else:
        response = (
            f"Töröltem {article} {mit} terméket "
            "az összes bevásárlólistáról."
        )

    return {
        "status": "ok",
        "mit": mit,
        "honnan": honnan,
        "deleted": deleted,
        "response": response
    }

        
@app.post("/api/done-id/{item_id}")
def done_item_id(item_id: int):

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT id
            FROM bevasarlas
            WHERE id = ?
            """,
            (item_id,)
        )

        item = cursor.fetchone()

        if item is None:
            raise HTTPException(
                status_code=404,
                detail=f"Nincs ilyen ID: {item_id}"
            )

        cursor.execute(
            """
            UPDATE bevasarlas
            SET teljesult = 1
            WHERE id = ?
            """,
            (item_id,)
        )

        db.commit()

        return {
            "status": "ok",
            "id": item_id,
            "teljesult": True
        }

    finally:
        db.close()


@app.post("/api/undone-id/{item_id}")
def undone_item_id(item_id: int):

    db = get_db()

    try:
        cursor = db.cursor()

        cursor.execute(
            """
            SELECT id
            FROM bevasarlas
            WHERE id = ?
            """,
            (item_id,)
        )

        item = cursor.fetchone()

        if item is None:
            raise HTTPException(
                status_code=404,
                detail=f"Nincs ilyen ID: {item_id}"
            )

        cursor.execute(
            """
            UPDATE bevasarlas
            SET teljesult = 0
            WHERE id = ?
            """,
            (item_id,)
        )

        db.commit()

        return {
            "status": "ok",
            "id": item_id,
            "teljesult": False
        }

    finally:
        db.close()


@app.delete("/api/delete-id/{item_id}")
def delete_item_id(item_id: int):

    db = get_db()

    try:
        cursor = db.cursor()

        # Előbb ellenőrizzük, hogy létezik-e
        cursor.execute(
            """
            SELECT id, mit
            FROM bevasarlas
            WHERE id = ?
            """,
            (item_id,)
        )

        item = cursor.fetchone()

        if item is None:
            raise HTTPException(
                status_code=404,
                detail=f"Nincs ilyen ID: {item_id}"
            )

        # Ha létezik, töröljük
        cursor.execute(
            """
            DELETE FROM bevasarlas
            WHERE id = ?
            """,
            (item_id,)
        )

        db.commit()

        return {
            "status": "ok",
            "id": item_id,
            "mit": item[1],
            "deleted": True
        }

    finally:
        db.close()

# ==========================================
# API - Bevásárlólista lekérdezése
# ==========================================

class ListRequest(BaseModel):
    lista: str


@app.post("/api/list")
def api_list(data: ListRequest):

    lista = data.lista.strip()

    if not lista:
        raise HTTPException(
            status_code=400,
            detail="Hiányzó lista neve."
        )

    conn = get_db()

    try:
        cur = conn.cursor(dictionary=True)

        cur.execute(
            """
            SELECT mit, mennyit, mertekegyseg
            FROM bevasarlas
            WHERE honnan = ?
              AND teljesult = 0
            ORDER BY id
            """,
            (lista,)
        )

        rows = cur.fetchall()

        items = [
            {
                "mit": row["mit"],
                "mennyiseg": row["mennyit"],
                "egyseg": row["mertekegyseg"]
            }
            for row in rows
        ]

        return {
            "status": "ok",
            "lista": lista,
            "count": len(items),
            "items": items
        }

    finally:
        conn.close()
        
@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={}
    )

@app.get("/lista", response_class=HTMLResponse)
def lista_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="lista.html",
        context={}
    )