"""
Verifie que schema.sql et analysis_queries.sql fonctionnent reellement :
charge les CSV synthetiques dans une base SQLite locale (equivalent de
demonstration pour PostgreSQL, meme schema), execute chaque requete
documentee et exporte les resultats dans docs/query_results.md.

Usage :
    python src/sql/run_queries.py
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
SYNTHETIC_DIR = BASE_DIR / "data" / "synthetic"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
QUERIES_PATH = Path(__file__).parent / "analysis_queries.sql"
OUTPUT_PATH = BASE_DIR / "docs" / "query_results.md"


def build_database(conn: sqlite3.Connection) -> None:
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)

    fournisseurs = pd.read_csv(SYNTHETIC_DIR / "fournisseurs.csv")
    pieces = pd.read_csv(SYNTHETIC_DIR / "pieces_rechange.csv")
    interventions = pd.read_csv(SYNTHETIC_DIR / "interventions_pieces.csv")

    fournisseurs.to_sql("fournisseurs", conn, if_exists="append", index=False)
    pieces.to_sql("pieces_rechange", conn, if_exists="append", index=False)
    interventions.to_sql("interventions_pieces", conn, if_exists="append", index=False)


def split_queries(sql_text: str) -> list[tuple[str, str]]:
    """Decoupe le fichier .sql en (commentaire d'objectif, requete) sur la base des blocs '-- n)'."""
    blocks = re.split(r"\n(?=-- \d\))", sql_text)
    result = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        title = lines[0].lstrip("- ").strip()
        query = "\n".join(l for l in lines if not l.strip().startswith("--")).strip()
        if query:
            result.append((title, query))
    return result


def main() -> None:
    if not (SYNTHETIC_DIR / "interventions_pieces.csv").exists():
        print("ERREUR : donnees synthetiques introuvables. Executez d'abord :")
        print("  python src/collect/download_ai4i.py")
        print("  python src/collect/generate_synthetic_parts.py")
        raise SystemExit(1)

    conn = sqlite3.connect(":memory:")
    build_database(conn)

    queries = split_queries(QUERIES_PATH.read_text(encoding="utf-8"))

    lines = ["# Resultats des requetes d'analyse (`analysis_queries.sql`)", ""]
    lines.append("Genere automatiquement par `src/sql/run_queries.py` a partir des donnees synthetiques.")
    lines.append("")

    for title, query in queries:
        print(f"--- {title} ---")
        df = pd.read_sql_query(query, conn)
        print(df.to_string(index=False))
        print()

        lines.append(f"## {title}")
        lines.append("")
        lines.append(df.to_markdown(index=False))
        lines.append("")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Resultats exportes : {OUTPUT_PATH}")

    conn.close()


if __name__ == "__main__":
    main()
