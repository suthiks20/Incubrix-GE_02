"""SQLite store: one row per (input, slot). Gives refresh-without-duplicates and an audit trail."""
import json, sqlite3, time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS assets(
  key TEXT PRIMARY KEY, asset_id TEXT UNIQUE, input_id TEXT, slot_id TEXT, content_hash TEXT,
  status TEXT, version INTEGER, data TEXT, updated_at REAL);
CREATE TABLE IF NOT EXISTS runs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, started REAL, input_id TEXT, input_chars INTEGER, produced INTEGER,
  rejected INTEGER, duplicates INTEGER, runtime_s REAL, cost_usd REAL, note TEXT);
CREATE TABLE IF NOT EXISTS errors(id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, run_id INTEGER, message TEXT);
"""

class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.executescript(SCHEMA)

    def get(self, key):
        r = self.db.execute("SELECT asset_id,content_hash,status,version,data FROM assets WHERE key=?", (key,)).fetchone()
        return None if not r else {"asset_id": r[0], "content_hash": r[1], "status": r[2], "version": r[3], "data": json.loads(r[4])}

    def all_assets(self):
        rows = self.db.execute("SELECT key,asset_id,status,data FROM assets ORDER BY asset_id").fetchall()
        return [{"key": k, "asset_id": i, "status": s, "data": json.loads(d)} for k, i, s, d in rows]

    def next_id(self):
        n = self.db.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
        return n + 1

    def upsert(self, key, asset_id, input_id, slot_id, content_hash, status, data):
        cur = self.get(key)
        ver = (cur["version"] + 1) if cur else 1
        self.db.execute("INSERT OR REPLACE INTO assets VALUES(?,?,?,?,?,?,?,?,?)",
                        (key, asset_id, input_id, slot_id, content_hash, status, ver, json.dumps(data), time.time()))
        self.db.commit()

    def set_status(self, key, status, data=None):
        cur = self.get(key)
        if data is None: data = cur["data"]
        self.db.execute("UPDATE assets SET status=?, data=?, updated_at=? WHERE key=?", (status, json.dumps(data), time.time(), key))
        self.db.commit()

    def add_run(self, **kw):
        cur = self.db.execute("INSERT INTO runs(started,input_id,input_chars,produced,rejected,duplicates,runtime_s,cost_usd,note) VALUES(?,?,?,?,?,?,?,?,?)",
                              (kw["started"], kw["input_id"], kw["input_chars"], kw["produced"], kw["rejected"], kw["duplicates"], kw["runtime_s"], kw["cost_usd"], kw.get("note", "")))
        self.db.commit(); return cur.lastrowid

    def add_error(self, run_id, message):
        self.db.execute("INSERT INTO errors(ts,run_id,message) VALUES(?,?,?)", (time.time(), run_id, message)); self.db.commit()

    def close(self):
        self.db.close()
