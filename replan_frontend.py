"""
replan_frontend.py
==================
RePlann – Streamlit Frontend (Implementierungsvorlage)

Passend zum Backend: https://github.com/TimBoj23/Fallstudie_Software_Engineering_G03

Starten:
    streamlit run replan_frontend.py

Voraussetzungen:
    pip3 install streamlit requests

Backend muss laufen auf: http://localhost:5000
"""

import streamlit as st
import requests
from datetime import datetime, timedelta

# ─── Konfiguration ─────────────────────────────────────────────────────────────
API_BASE = "http://localhost:5000/api"

# ─── Seiteneinstellungen ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="RePlann",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Session State initialisieren ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ─── Hilfsfunktionen ──────────────────────────────────────────────────────────

def get_headers():
    """Auth-Header für alle API-Requests."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def api_get(path, params=None):
    """GET-Request an die API."""
    try:
        r = requests.get(f"{API_BASE}{path}", headers=get_headers(), params=params, timeout=5)
        return r
    except requests.exceptions.ConnectionError:
        return None


def api_post(path, data):
    """POST-Request an die API."""
    try:
        r = requests.post(f"{API_BASE}{path}", json=data, headers=get_headers(), timeout=5)
        return r
    except requests.exceptions.ConnectionError:
        return None


def api_delete(path):
    """DELETE-Request an die API."""
    try:
        r = requests.delete(f"{API_BASE}{path}", headers=get_headers(), timeout=5)
        return r
    except requests.exceptions.ConnectionError:
        return None


def format_dt(iso_string):
    """ISO-8601 Datum → lesbares deutsches Format."""
    if not iso_string:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return iso_string


def status_badge(status):
    """Buchungsstatus als farbiges Emoji-Label."""
    mapping = {
        "confirmed": "✅ Bestätigt",
        "pending":   "⏳ Ausstehend",
        "cancelled": "❌ Storniert",
    }
    return mapping.get(status, f"❓ {status}")


def backend_online():
    """Prüft ob das Backend erreichbar ist."""
    r = api_get("/health")
    return r is not None and r.status_code == 200


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🗓️ RePlann")
    st.caption("Raum- & Ressourcenplanung")
    st.divider()

    # Login-Status anzeigen
    if st.session_state.logged_in:
        st.success(f"👤 Eingeloggt als **{st.session_state.username}**")
        if st.button("🚪 Ausloggen", use_container_width=True):
            api_post("/auth/logout", {})
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.page = "Dashboard"
            st.rerun()
    else:
        st.info("Nicht eingeloggt")

    st.divider()

    # Navigation
    pages_public = ["Dashboard", "Räume", "Sitzplätze", "Assets", "Verfügbarkeit prüfen"]
    pages_auth   = ["Meine Buchungen", "Buchung erstellen"]

    st.subheader("Navigation")
    for p in pages_public:
        if st.button(p, use_container_width=True):
            st.session_state.page = p

    if st.session_state.logged_in:
        st.divider()
        st.caption("Nur für eingeloggte Nutzer")
        for p in pages_auth:
            if st.button(p, use_container_width=True):
                st.session_state.page = p
    else:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True):
                st.session_state.page = "Login"
        with col2:
            if st.button("Registrieren", use_container_width=True):
                st.session_state.page = "Registrieren"


# ─── Seiten ────────────────────────────────────────────────────────────────────
page = st.session_state.page

# ══════════════════════════════════════════════════════════════════════════════
# SEITE: Dashboard
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.title("🏠 Dashboard")
    st.caption("Willkommen bei RePlann – Raum- und Ressourcenplanungssystem")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        if backend_online():
            st.metric("Backend-Status", "✅ Online", "API erreichbar")
        else:
            st.metric("Backend-Status", "❌ Offline", "http://localhost:5000 nicht erreichbar")

    with col2:
        r = api_get("/rooms")
        count = len(r.json()) if r and r.status_code == 200 else "—"
        st.metric("Verfügbare Räume", count)

    with col3:
        r = api_get("/assets")
        count = len(r.json()) if r and r.status_code == 200 else "—"
        st.metric("Verfügbare Assets", count)

    st.divider()
    st.subheader("📋 API-Übersicht")
    st.caption("Alle verfügbaren Endpunkte des Backends")

    r = api_get("")
    if r and r.status_code == 200:
        data = r.json()
        for category, endpoints in data.get("endpoints", {}).items():
            with st.expander(f"📁 {category.upper()}"):
                for endpoint, desc in endpoints.items():
                    st.code(endpoint, language=None)
                    st.caption(desc)
    else:
        st.warning("Backend nicht erreichbar. Starte zuerst das Backend mit `python3 app.py`.")
        st.code("cd Fallstudie_Software_Engineering_G03\npython3 app.py", language="bash")


# ══════════════════════════════════════════════════════════════════════════════
# SEITE: Login
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Login":
    st.title("🔐 Login")
    st.divider()

    with st.form("login_form"):
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        submitted = st.form_submit_button("Einloggen", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("Bitte Benutzernamen und Passwort eingeben.")
        else:
            r = api_post("/auth/login", {"username": username, "password": password})
            if r is None:
                st.error("❌ Backend nicht erreichbar. Starte zuerst `python3 app.py`.")
            elif r.status_code == 200:
                data = r.json()
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.token = data.get("token") or data.get("access_token")
                st.success(f"✅ Willkommen, {username}!")
                st.session_state.page = "Dashboard"
                st.rerun()
            elif r.status_code == 401:
                st.error("❌ Falscher Benutzername oder Passwort.")
            else:
                st.error(f"❌ Fehler {r.status_code}: {r.text}")

    st.divider()
    st.caption("Noch kein Konto?")
    if st.button("Jetzt registrieren →"):
        st.session_state.page = "Registrieren"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# SEITE: Registrieren
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Registrieren":
    st.title("📝 Registrieren")
    st.divider()

    with st.form("register_form"):
        username  = st.text_input("Benutzername")
        email     = st.text_input("E-Mail")
        password  = st.text_input("Passwort", type="password")
        password2 = st.text_input("Passwort wiederholen", type="password")
        submitted = st.form_submit_button("Registrieren", use_container_width=True)

    if submitted:
        if not username or not email or not password:
            st.error("Bitte alle Felder ausfüllen.")
        elif password != password2:
            st.error("Passwörter stimmen nicht überein.")
        else:
            r = api_post("/auth/register", {
                "username": username,
                "email": email,
                "password": password
            })
            if r is None:
                st.error("❌ Backend nicht erreichbar.")
            elif r.status_code in (200, 201):
                st.success("✅ Konto erfolgreich erstellt! Bitte einloggen.")
                st.session_state.page = "Login"
                st.rerun()
            elif r.status_code == 409:
                st.error("❌ Benutzername oder E-Mail bereits vergeben.")
            else:
                st.error(f"❌ Fehler {r.status_code}: {r.text}")


# ══════════════════════════════════════════════════════════════════════════════
# SEITE: Räume
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Räume":
    st.title("🏢 Räume")
    st.caption("GET /api/rooms – Alle Räume suchen und filtern")
    st.divider()

    with st.expander("🔍 Filter", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            q        = st.text_input("Suchbegriff (Name)")
            location = st.text_input("Standort")
        with col2:
            min_cap   = st.number_input("Mindestkapazität", min_value=0, value=0)
            equipment = st.text_input("Ausstattung (z.B. Beamer)")
        with col3:
            check_avail = st.checkbox("Verfügbarkeit prüfen")
            if check_avail:
                start_date = st.date_input("Von")
                start_time = st.time_input("Uhrzeit Von")
                end_date   = st.date_input("Bis")
                end_time   = st.time_input("Uhrzeit Bis")

    if st.button("🔍 Suchen", use_container_width=True):
        params = {}
        if q:         params["q"]            = q
        if location:  params["location"]     = location
        if min_cap:   params["min_capacity"] = min_cap
        if equipment: params["equipment"]    = equipment
        if check_avail:
            params["start"] = datetime.combine(start_date, start_time).isoformat()
            params["end"]   = datetime.combine(end_date, end_time).isoformat()

        with st.spinner("Räume werden geladen..."):
            r = api_get("/rooms", params=params)

        if r is None:
            st.error("❌ Backend nicht erreichbar.")
        elif r.status_code == 200:
            rooms = r.json()
            if not rooms:
                st.info("Keine Räume gefunden.")
            else:
                st.success(f"✅ {len(rooms)} Raum/Räume gefunden")
                for room in rooms:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.subheader(room.get("name", "—"))
                            st.caption(f"📍 {room.get('location', '—')} &nbsp;|&nbsp; 👥 {room.get('capacity', '—')} Personen")
                            if room.get("equipment"):
                                eq = room["equipment"]
                                st.write("🔧 " + (", ".join(eq) if isinstance(eq, list) else eq))
                            if room.get("description"):
                                st.write(room["description"])
                        with col2:
                            st.code(str(room.get("id", "")), language=None)
                            st.caption("Raum-ID (für Buchung)")
        else:
            st.error(f"❌ Fehler {r.status_code}: {r.text}")
    else:
        with st.spinner("Lade Räume..."):
            r = api_get("/rooms")
        if r and r.status_code == 200:
            st.write(f"**{len(r.json())} Räume** insgesamt – nutze die Filter oben zur Einschränkung.")
        elif r is None:
            st.warning("⚠️ Backend nicht erreichbar. Starte zuerst `python3 app.py`.")


# ══════════════════════════════════════════════════════════════════════════════
# SEITE: Sitzplätze
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Sitzplätze":
    st.title("🪑 Sitzplätze")
    st.caption("GET /api/seats – Alle Sitzplätze oder gezielt nach Raum filtern")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        room_id = st.text_input("Raum-ID (optional – leer lassen für alle)")
    with col2:
        q_seat = st.text_input("Suchbegriff")

    if st.button("🔍 Sitzplätze laden", use_container_width=True):
        params = {}
        if room_id: params["room_id"] = room_id
        if q_seat:  params["q"]       = q_seat

        with st.spinner("Sitzplätze werden geladen..."):
            r = api_get("/seats", params=params)

        if r is None:
            st.error("❌ Backend nicht erreichbar.")
        elif r.status_code == 200:
            seats = r.json()
            if not seats:
                st.info("Keine Sitzplätze gefunden.")
            else:
                st.success(f"✅ {len(seats)} Sitzplatz/Sitzplätze gefunden")
                for seat in seats:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{seat.get('name', '—')}**")
                            st.caption(f"Raum-ID: {seat.get('room_id', '—')}")
                            if seat.get("description"):
                                st.caption(seat["description"])
                        with col2:
                            st.code(str(seat.get("id", "")), language=None)
                            st.caption("Sitzplatz-ID")
        else:
            st.error(f"❌ Fehler {r.status_code}: {r.text}")


# ══════════════════════════════════════════════════════════════════════════════
# SEITE: Assets
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Assets":
    st.title("🖥️ Assets")
    st.caption("GET /api/assets – Beamer, Laptops, Kameras und andere Ressourcen")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        q_asset    = st.text_input("Suchbegriff")
        asset_type = st.text_input("Typ (z.B. Beamer, Laptop)")
    with col2:
        avail_asset = st.checkbox("Nur verfügbare Assets anzeigen")
        if avail_asset:
            a_start = st.date_input("Verfügbar ab")
            a_end   = st.date_input("Verfügbar bis")

    if st.button("🔍 Assets laden", use_container_width=True):
        params = {}
        if q_asset:    params["q"]    = q_asset
        if asset_type: params["type"] = asset_type
        if avail_asset:
            params["start"] = datetime.combine(a_start, datetime.min.time()).isoformat()
            params["end"]   = datetime.combine(a_end, datetime.min.time()).isoformat()

        with st.spinner("Assets werden geladen..."):
            r = api_get("/assets", params=params)

        if r is None:
            st.error("❌ Backend nicht erreichbar.")
        elif r.status_code == 200:
            assets = r.json()
            if not assets:
                st.info("Keine Assets gefunden.")
            else:
                st.success(f"✅ {len(assets)} Asset(s) gefunden")
                cols = st.columns(3)
                for i, asset in enumerate(assets):
                    with cols[i % 3]:
                        with st.container(border=True):
                            st.write(f"**{asset.get('name', '—')}**")
                            st.caption(f"Typ: {asset.get('type', '—')}")
                            if asset.get("description"):
                                st.caption(asset["description"])
                            st.code(str(asset.get("id", "")), language=None)
                            st.caption("Asset-ID (für Buchung)")
        else:
            st.error(f"❌ Fehler {r.status_code}: {r.text}")
    else:
        with st.spinner("Lade Assets..."):
            r = api_get("/assets")
        if r and r.status_code == 200:
            st.write(f"**{len(r.json())} Assets** insgesamt verfügbar.")
        elif r is None:
            st.warning("⚠️ Backend nicht erreichbar.")


# ══════════════════════════════════════════════════════════════════════════════
# SEITE: Meine Buchungen
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Meine Buchungen":
    st.title("📋 Meine Buchungen")
    st.caption("GET /api/bookings – Alle eigenen Buchungen anzeigen")
    st.divider()

    if not st.session_state.logged_in:
        st.warning("⚠️ Bitte zuerst einloggen, um deine Buchungen zu sehen.")
        if st.button("Zum Login"):
            st.session_state.page = "Login"
            st.rerun()
    else:
        with st.spinner("Buchungen werden geladen..."):
            r = api_get("/bookings")

        if r is None:
            st.error("❌ Backend nicht erreichbar.")
        elif r.status_code == 401:
            st.error("❌ Sitzung abgelaufen. Bitte erneut einloggen.")
        elif r.status_code == 200:
            bookings = r.json()
            if not bookings:
                st.info("📭 Keine Buchungen vorhanden.")
                if st.button("➕ Erste Buchung erstellen"):
                    st.session_state.page = "Buchung erstellen"
                    st.rerun()
            else:
                st.success(f"✅ {len(bookings)} Buchung(en) gefunden")
                for booking in bookings:
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            btype = booking.get("booking_type", "—")
                            if btype == "room":
                                st.write(f"🏢 **Raumbuchung** – Raum-ID: {booking.get('room_id', '—')}")
                            elif btype == "seat":
                                st.write(f"🪑 **Sitzplatzbuchung** – Sitzplatz-ID: {booking.get('seat_id', '—')}")
                            elif btype == "asset":
                                st.write(f"🖥️ **Asset-Buchung** – Asset-ID: {booking.get('asset_id', '—')}")
                            else:
                                st.write(f"📌 **Buchung** (Typ: {btype})")
                        with col2:
                            st.write(f"🕐 {format_dt(booking.get('start_time'))} → {format_dt(booking.get('end_time'))}")
                            st.write(status_badge(booking.get("status", "")))
                        with col3:
                            booking_id = booking.get("id")
                            if booking.get("status") != "cancelled":
                                if st.button("❌ Stornieren", key=f"cancel_{booking_id}"):
                                    r2 = api_delete(f"/bookings/{booking_id}")
                                    if r2 and r2.status_code in (200, 204):
                                        st.success("Buchung storniert!")
                                        st.rerun()
                                    else:
                                        st.error("Stornierung fehlgeschlagen.")
        else:
            st.error(f"❌ Fehler {r.status_code}: {r.text}")


# ══════════════════════════════════════════════════════════════════════════════
# SEITE: Buchung erstellen
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Buchung erstellen":
    st.title("➕ Buchung erstellen")
    st.caption("POST /api/bookings – Raum, Sitzplatz oder Asset buchen")
    st.divider()

    if not st.session_state.logged_in:
        st.warning("⚠️ Bitte zuerst einloggen, um eine Buchung zu erstellen.")
        if st.button("Zum Login"):
            st.session_state.page = "Login"
            st.rerun()
    else:
        booking_type = st.selectbox(
            "Was möchtest du buchen?",
            ["Raum 🏢", "Sitzplatz 🪑", "Asset 🖥️"]
        )

        st.divider()

        with st.form("booking_form"):
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Startdatum", value=datetime.today())
                start_time = st.time_input("Startzeit", value=datetime.now().replace(minute=0, second=0))
            with col2:
                end_date = st.date_input("Enddatum", value=datetime.today())
                end_time = st.time_input("Endzeit", value=(datetime.now() + timedelta(hours=1)).replace(minute=0, second=0))

            st.divider()

            if "Raum" in booking_type:
                resource_id = st.text_input("Raum-ID", placeholder="z.B. 1 – aus der Räume-Seite kopieren")
                auto_seat   = st.checkbox("Sitzplatz automatisch zuweisen")
                payload_key = "room_id"
                btype_val   = "room"
            elif "Sitzplatz" in booking_type:
                resource_id = st.text_input("Sitzplatz-ID", placeholder="z.B. 3 – aus der Sitzplätze-Seite kopieren")
                auto_seat   = False
                payload_key = "seat_id"
                btype_val   = "seat"
            else:
                resource_id = st.text_input("Asset-ID", placeholder="z.B. 5 – aus der Assets-Seite kopieren")
                auto_seat   = False
                payload_key = "asset_id"
                btype_val   = "asset"

            notes     = st.text_area("Notizen (optional)")
            submitted = st.form_submit_button("✅ Buchung erstellen", use_container_width=True)

        if submitted:
            if not resource_id:
                st.error("Bitte eine ID eingeben.")
            else:
                start_iso = datetime.combine(start_date, start_time).isoformat()
                end_iso   = datetime.combine(end_date, end_time).isoformat()

                payload = {
                    "booking_type": btype_val,
                    payload_key:    resource_id,
                    "start_time":   start_iso,
                    "end_time":     end_iso,
                }
                if notes:
                    payload["notes"] = notes
                if "Raum" in booking_type and auto_seat:
                    payload["auto_assign_seat"] = True

                with st.spinner("Buchung wird erstellt..."):
                    r = api_post("/bookings", payload)

                if r is None:
                    st.error("❌ Backend nicht erreichbar.")
                elif r.status_code in (200, 201):
                    st.success("🎉 Buchung erfolgreich erstellt!")
                    st.json(r.json())
                elif r.status_code == 409:
                    st.error("❌ Zeitkonflikt! Objekt ist in diesem Zeitraum bereits gebucht.")
                    data = r.json()
                    if "conflicting_booking" in data:
                        st.write("Bestehende Buchung:")
                        st.json(data["conflicting_booking"])
                elif r.status_code == 401:
                    st.error("❌ Sitzung abgelaufen. Bitte erneut einloggen.")
                elif r.status_code == 404:
                    st.error("❌ ID nicht gefunden. Bitte prüfe die eingegebene ID.")
                else:
                    st.error(f"❌ Fehler {r.status_code}: {r.text}")


# ══════════════════════════════════════════════════════════════════════════════
# SEITE: Verfügbarkeit prüfen
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Verfügbarkeit prüfen":
    st.title("🔎 Verfügbarkeit prüfen")
    st.caption("GET /api/bookings/availability – Ist ein Objekt im Zeitraum frei?")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        check_type = st.selectbox("Typ", ["room", "seat", "asset"])
        check_id   = st.text_input("ID des Objekts")
    with col2:
        c_start_d = st.date_input("Von")
        c_start_t = st.time_input("Uhrzeit Von")
        c_end_d   = st.date_input("Bis")
        c_end_t   = st.time_input("Uhrzeit Bis")

    if st.button("🔍 Verfügbarkeit prüfen", use_container_width=True):
        if not check_id:
            st.error("Bitte eine ID eingeben.")
        else:
            params = {
                "type":  check_type,
                "id":    check_id,
                "start": datetime.combine(c_start_d, c_start_t).isoformat(),
                "end":   datetime.combine(c_end_d, c_end_t).isoformat(),
            }
            with st.spinner("Verfügbarkeit wird geprüft..."):
                r = api_get("/bookings/availability", params=params)

            if r is None:
                st.error("❌ Backend nicht erreichbar.")
            elif r.status_code == 200:
                data = r.json()
                if data.get("available"):
                    st.success("✅ Das Objekt ist in diesem Zeitraum **verfügbar**!")
                else:
                    st.error("❌ Das Objekt ist in diesem Zeitraum **nicht verfügbar**.")
                    if data.get("conflicts"):
                        st.write("Konflikte:")
                        for c in data["conflicts"]:
                            st.json(c)
            else:
                st.error(f"❌ Fehler {r.status_code}: {r.text}")
