"""
SQLite registry for tracking vector databases.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

REGISTRY_PATH = "/home/brian/soar/vectordb_registry.db"


def get_conn():
    conn = sqlite3.connect(REGISTRY_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_registry():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS vector_databases (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT NOT NULL UNIQUE,
                path        TEXT NOT NULL,
                description TEXT,
                model       TEXT NOT NULL,
                collection  TEXT NOT NULL,
                doc_count   INTEGER DEFAULT 0,
                created_at  TEXT NOT NULL,
                updated_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS vdb_documents (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                vdb_id      INTEGER NOT NULL REFERENCES vector_databases(id),
                doc_id      TEXT NOT NULL,
                topic       TEXT,
                source_url  TEXT,
                added_at    TEXT NOT NULL,
                UNIQUE(vdb_id, doc_id)
            );

            CREATE TABLE IF NOT EXISTS vdb_tags (
                vdb_id  INTEGER NOT NULL REFERENCES vector_databases(id),
                tag     TEXT NOT NULL,
                PRIMARY KEY (vdb_id, tag)
            );
        """)
    print(f"Registry initialized at {REGISTRY_PATH}")


def register_vdb(name, path, description, model, collection, doc_ids_and_topics=None, tags=None):
    """Register or update a vector database entry."""
    now = datetime.utcnow().isoformat()
    doc_count = len(doc_ids_and_topics) if doc_ids_and_topics else 0

    with get_conn() as conn:
        conn.execute("""
            INSERT INTO vector_databases (name, path, description, model, collection, doc_count, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                path=excluded.path,
                description=excluded.description,
                model=excluded.model,
                collection=excluded.collection,
                doc_count=excluded.doc_count,
                updated_at=excluded.updated_at
        """, (name, path, description, model, collection, doc_count, now, now))

        vdb_id = conn.execute("SELECT id FROM vector_databases WHERE name=?", (name,)).fetchone()["id"]

        if doc_ids_and_topics:
            conn.executemany("""
                INSERT OR REPLACE INTO vdb_documents (vdb_id, doc_id, topic, source_url, added_at)
                VALUES (?, ?, ?, ?, ?)
            """, [(vdb_id, d["id"], d.get("topic"), d.get("source_url"), now)
                  for d in doc_ids_and_topics])

        if tags:
            conn.executemany("""
                INSERT OR IGNORE INTO vdb_tags (vdb_id, tag) VALUES (?, ?)
            """, [(vdb_id, tag) for tag in tags])

    print(f"Registered VDB '{name}' (id={vdb_id}, docs={doc_count})")
    return vdb_id


def list_vdbs():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT v.*, GROUP_CONCAT(t.tag, ', ') as tags
            FROM vector_databases v
            LEFT JOIN vdb_tags t ON t.vdb_id = v.id
            GROUP BY v.id
            ORDER BY v.created_at
        """).fetchall()
    return [dict(r) for r in rows]


def get_vdb(name):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM vector_databases WHERE name=?", (name,)).fetchone()
        if not row:
            return None
        vdb = dict(row)
        vdb["tags"] = [r["tag"] for r in conn.execute(
            "SELECT tag FROM vdb_tags WHERE vdb_id=?", (vdb["id"],)).fetchall()]
        vdb["documents"] = [dict(r) for r in conn.execute(
            "SELECT doc_id, topic, source_url, added_at FROM vdb_documents WHERE vdb_id=?",
            (vdb["id"],)).fetchall()]
    return vdb


def print_registry():
    dbs = list_vdbs()
    if not dbs:
        print("No vector databases registered.")
        return
    print(f"\n{'ID':<4} {'Name':<30} {'Docs':<6} {'Model':<25} {'Tags':<30} {'Updated'}")
    print("-" * 110)
    for db in dbs:
        print(f"{db['id']:<4} {db['name']:<30} {db['doc_count']:<6} {db['model']:<25} "
              f"{(db['tags'] or ''):<30} {db['updated_at'][:19]}")


if __name__ == "__main__":
    import sys
    init_registry()

    if len(sys.argv) > 1 and sys.argv[1] == "list":
        print_registry()
    elif len(sys.argv) > 1 and sys.argv[1] == "show" and len(sys.argv) > 2:
        vdb = get_vdb(sys.argv[2])
        if vdb:
            docs = vdb.pop("documents")
            print(json.dumps(vdb, indent=2))
            print(f"\nDocuments ({len(docs)}):")
            for d in docs:
                print(f"  [{d['doc_id']}] {d['topic']}")
        else:
            print(f"No VDB named '{sys.argv[2]}'")
    else:
        print("Usage: python vectordb_registry.py [list | show <name>]")
