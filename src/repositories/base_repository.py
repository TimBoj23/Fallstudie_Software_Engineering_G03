"""
Base Repository – Generisches JSON-Repository

Architekturentscheidung:
    Das Repository-Pattern trennt die Datenzugriffslogik von der Geschäftslogik.
    Die JSON-Dateien fungieren als einfacher, dateibasierter Datenspeicher für den MVP.
    Durch diese Abstraktion kann der Datenspeicher später ohne Änderungen an den
    Services gegen eine relationale Datenbank (PostgreSQL) oder einen NoSQL-Store
    (MongoDB) ausgetauscht werden – ein zentrales Skalierungsprinzip.

Skalierungsnotiz:
    - Thread-Safety: Datei-Locking mit threading.Lock() für Multi-Thread-Betrieb
    - Für Prod: Austausch gegen SQLAlchemy ORM oder ähnliches
    - Caching-Schicht (Redis) kann vor diesem Repository transparent eingezogen werden
"""

import json
import os
import sqlite3
import threading
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class JsonRepository(Generic[T]):
    """
    Generisches Repository für JSON-Dateipersistenz.

    Verwaltet eine Liste von Objekten (serialisiert als Dictionaries)
    in einer einzelnen JSON-Datei. Alle Lese-/Schreiboperationen sind
    durch einen Threading-Lock abgesichert.

    Unterklassen implementieren from_dict() und to_dict() für
    typspezifische Serialisierung.
    """

    def __init__(self, filepath: str):
        """
        Args:
            filepath: Absoluter Pfad zur JSON-Datei.
                      Wird angelegt, falls sie nicht existiert.
        """
        self._filepath = filepath
        self._lock = threading.Lock()
        self._storage = os.environ.get("REPLAN_STORAGE", "sqlite").lower()
        self._db_path = os.environ.get(
            "REPLAN_DB_PATH",
            os.path.join(os.path.dirname(self._filepath), "replan.sqlite"),
        )
        self._ensure_file_exists()

    def _use_sqlite(self) -> bool:
        return getattr(self, "_storage", os.environ.get("REPLAN_STORAGE", "sqlite")).lower() == "sqlite"

    def _collection_name(self) -> str:
        return os.path.splitext(os.path.basename(self._filepath))[0]

    def _connect(self):
        db_path = getattr(
            self,
            "_db_path",
            os.environ.get("REPLAN_DB_PATH", os.path.join(os.path.dirname(self._filepath), "replan.sqlite")),
        )
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        self._ensure_sqlite_schema(conn)
        return conn

    def _ensure_sqlite_schema(self, conn) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                collection TEXT NOT NULL,
                id TEXT NOT NULL,
                data TEXT NOT NULL,
                PRIMARY KEY (collection, id)
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_records_collection ON records(collection)"
        )

    def _ensure_file_exists(self) -> None:
        """Legt die Datei und Verzeichnisstruktur an, wenn sie nicht existiert."""
        os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
        if self._use_sqlite():
            with self._connect():
                pass
            return
        if not os.path.exists(self._filepath):
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read_all_raw(self) -> List[Dict[str, Any]]:
        """Liest alle Einträge als rohe Dictionaries aus der JSON-Datei."""
        if self._use_sqlite():
            self._migrate_json_if_needed()
            with self._connect() as conn:
                rows = conn.execute(
                    "SELECT data FROM records WHERE collection = ? ORDER BY rowid",
                    (self._collection_name(),),
                ).fetchall()
            return [json.loads(row["data"]) for row in rows]
        with open(self._filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_all_raw(self, data: List[Dict[str, Any]]) -> None:
        """Schreibt alle Einträge als Dictionaries in die JSON-Datei."""
        if self._use_sqlite():
            collection = self._collection_name()
            with self._connect() as conn:
                conn.execute("DELETE FROM records WHERE collection = ?", (collection,))
                conn.executemany(
                    "INSERT INTO records(collection, id, data) VALUES (?, ?, ?)",
                    [
                        (collection, str(item.get("id")), json.dumps(item, ensure_ascii=False))
                        for item in data
                    ],
                )
            return
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _migrate_json_if_needed(self) -> None:
        """Importiert vorhandene JSON-Dateien einmalig in SQLite."""
        if not os.path.exists(self._filepath):
            return
        collection = self._collection_name()
        with self._connect() as conn:
            existing = conn.execute(
                "SELECT COUNT(*) AS count FROM records WHERE collection = ?",
                (collection,),
            ).fetchone()["count"]
            if existing:
                return
            try:
                with open(self._filepath, "r", encoding="utf-8") as f:
                    raw = json.load(f)
            except (json.JSONDecodeError, OSError):
                raw = []
            conn.executemany(
                "INSERT OR REPLACE INTO records(collection, id, data) VALUES (?, ?, ?)",
                [
                    (collection, str(item.get("id")), json.dumps(item, ensure_ascii=False))
                    for item in raw
                    if item.get("id")
                ],
            )

    def from_dict(self, data: Dict[str, Any]) -> T:
        """Konvertiert ein Dictionary in ein typisiertes Objekt. Muss überschrieben werden."""
        raise NotImplementedError("Unterklassen müssen from_dict() implementieren.")

    def to_dict(self, obj: T) -> Dict[str, Any]:
        """Konvertiert ein Objekt in ein Dictionary. Muss überschrieben werden."""
        raise NotImplementedError("Unterklassen müssen to_dict() implementieren.")

    # ──────────────────────────────────────────────────────────────────────────
    # Öffentliche CRUD-Methoden
    # ──────────────────────────────────────────────────────────────────────────

    def find_all(self) -> List[T]:
        """Gibt alle Einträge zurück."""
        with self._lock:
            return [self.from_dict(d) for d in self._read_all_raw()]

    def find_by_id(self, obj_id: str) -> Optional[T]:
        """Gibt einen Eintrag anhand seiner ID zurück oder None."""
        with self._lock:
            for d in self._read_all_raw():
                if d.get("id") == obj_id:
                    return self.from_dict(d)
        return None

    def save(self, obj: T) -> T:
        """
        Speichert ein neues Objekt. Wirft ValueError, wenn die ID bereits existiert.
        """
        with self._lock:
            all_data = self._read_all_raw()
            new_data = self.to_dict(obj)
            for existing in all_data:
                if existing.get("id") == new_data.get("id"):
                    raise ValueError(f"Eintrag mit ID '{new_data.get('id')}' existiert bereits.")
            all_data.append(new_data)
            self._write_all_raw(all_data)
        return obj

    def update(self, obj: T) -> Optional[T]:
        """
        Aktualisiert einen bestehenden Eintrag anhand der ID.
        Gibt None zurück, wenn der Eintrag nicht gefunden wurde.
        """
        with self._lock:
            all_data = self._read_all_raw()
            new_data = self.to_dict(obj)
            for i, existing in enumerate(all_data):
                if existing.get("id") == new_data.get("id"):
                    all_data[i] = new_data
                    self._write_all_raw(all_data)
                    return obj
        return None

    def delete(self, obj_id: str) -> bool:
        """
        Entfernt einen Eintrag permanent anhand seiner ID.
        Gibt True zurück, wenn erfolgreich gelöscht, sonst False.

        Hinweis: Für Soft-Delete wird is_active=False gesetzt (über update()).
        """
        with self._lock:
            all_data = self._read_all_raw()
            new_data = [d for d in all_data if d.get("id") != obj_id]
            if len(new_data) == len(all_data):
                return False
            self._write_all_raw(new_data)
        return True

    def delete_all(self) -> int:
        """Entfernt alle Einträge dieser Collection und liefert deren Anzahl."""
        with self._lock:
            all_data = self._read_all_raw()
            self._write_all_raw([])
        return len(all_data)

    def retain(self, predicate) -> int:
        """Behält nur passende Objekte und liefert die Zahl entfernter Einträge."""
        with self._lock:
            all_data = self._read_all_raw()
            objects = [self.from_dict(item) for item in all_data]
            kept = [item for item in objects if predicate(item)]
            self._write_all_raw([self.to_dict(item) for item in kept])
        return len(all_data) - len(kept)

    def count(self) -> int:
        """Gibt die Gesamtanzahl der Einträge zurück."""
        with self._lock:
            return len(self._read_all_raw())

    def exists(self, obj_id: str) -> bool:
        """Prüft ob ein Eintrag mit der gegebenen ID existiert."""
        return self.find_by_id(obj_id) is not None
