# Bevásárlólista – FastAPI, MariaDB, Home Assistant

Magyar nyelvű bevásárlólista saját MariaDB adatbázissal, FastAPI REST-felülettel, böngészős kezelőfelülettel és Home Assistant Assist hangvezérléssel.

## Felépítés

- **MariaDB** – tételek, mennyiségek, mértékegységek, beszerzési helyek és teljesítési állapot tárolása.
- **FastAPI** (`app.py`) – REST API, Swagger dokumentáció, weboldalak kiszolgálása.
- **Web** (`templates/`, `static/`) – admin felület és mobilbarát bevásárlólista.
- **Home Assistant** (`HA REST/`, `HA autamations/`) – REST hívások és magyar nyelvű ADD / DELETE / LIST automatizációk.
- **Google AI Conversation** – a beszédfelismerésből kapott szöveg és a boltnevek értelmezése. Az Assist saját TTS-e vagy külön TTS-szolgáltatás mondja vissza az eredményt.
- **SQL init/** – az adatbázis létrehozásához szükséges SQL definíció.

## Telepítés

Python 3 környezetben telepítsd a szükséges csomagokat:

```bash
python -m pip install fastapi "uvicorn[standard]" mariadb python-dotenv jinja2
```

Hozd létre a MariaDB adatbázist a `SQL init/` mappában található SQL-definíció alapján, és adj megfelelő jogosultságokat az alkalmazás adatbázis-felhasználójának.

Másold a `.env.example` fájlt `.env` néven a projekt gyökerébe, majd töltsd ki a saját adataiddal:

```dotenv
DB_HOST=
DB_PORT=3306
DB_USER=
DB_PASSWORD=
DB_NAME=
```

Az `app.py` a `python-dotenv` segítségével olvassa be ezeket a változókat. A `.env` fájl **nem kerülhet GitHubra** (a `.gitignore` kizárja), és nem szabad benne valódi értékeket commitolni.

Indítás a projekt gyökérkönyvtárából:

```bash
uvicorn app:app --host 0.0.0.0 --port 8123
```

A port példa, a saját környezetben módosítható. Az API dokumentációja: `http://<szerver-ip>:8123/docs`; a webes felületek: `/admin` és `/lista`.

## API – fő műveletek

| Metódus | Útvonal | Funkció |
| --- | --- | --- |
| GET | `/api/list` | Teljes lista |
| GET | `/api/list/{honnan}` | Egy bolt listája |
| POST | `/api/list` | Aktív tételek lekérdezése boltnév alapján, hangos válaszhoz |
| POST | `/api/add` | Tétel hozzáadása |
| POST | `/api/delete` | Tétel(ek) törlése név, opcionálisan bolt alapján |
| POST | `/api/done/{mit}` | Tétel készre jelölése |
| POST | `/api/undone/{mit}` | Teljesítés visszavonása |
| GET | `/api/db-test` | Adatbázis-kapcsolat ellenőrzése |

További, ID-alapú és törlési műveletek a Swagger felületen találhatók.

## Home Assistant hangvezérlés

Az automatizációk a `HA autamations/` mappában találhatók. A rendszer magyar beszéd alapján hozzáad (**ADD**), töröl (**DELETE**) és felolvas (**LIST**) tételeket. A Google AI Conversation segít a termék- és boltnév-normalizálásban, például a beszédfelismerés által `OSAN`-nak írt `Auchan` esetén.

A HA-konfigurációhoz a FastAPI szerver címét, a `rest_command` hívásokat és a Google AI Conversation agent azonosítóját a saját rendszeredhez kell igazítani.

conversation parancsok:
ADD:
      - írd fel {valami}
      - add hozzá {valami}
      - tedd fel {valami}
      - vegyünk {valami}
DELETE:
      - Töröld [(a|az)]  {valami} [a] [listáról]
      - Vedd le [(a|az)] {valami} [a] [listáról] 
      - Töröld [(a|az)] {valami}
      - Vedd le [(a|az)] {valami}
LIST
      - Mi van [(a|az)] {lista} listán
      - Kérem [(a|az)] {lista} [bevásárló]listáját
## Biztonság

A repó nyilvános. Soha ne commitolj jelszavakat, API-kulcsokat, hozzáférési tokeneket, kitöltött `.env` fájlt vagy adatbázis-mentést. A `SQL init/` mappában kizárólag séma/definíció szerepeljen, éles adatok nélkül.
