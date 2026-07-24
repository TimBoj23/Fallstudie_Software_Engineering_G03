"""Offizieller Modul-Einstiegspunkt für RePlan.

Der Root-Einstieg `app.py` bleibt aus Kompatibilitätsgründen bestehen. Diese
Datei verhindert einen leeren Placeholder und erlaubt den Start per:

    python -m src.main
"""

from app import create_app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
