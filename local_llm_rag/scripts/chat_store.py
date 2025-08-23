import json, time, os, sqlite3
DB="conversations.db"
os.makedirs("chats", exist_ok=True)

def init():
    con=sqlite3.connect(DB); cur=con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS chat (
        id TEXT PRIMARY KEY, name TEXT, path TEXT, ts REAL)''')
    con.commit(); con.close()

def save_chat(name, messages):
    init(); cid=str(int(time.time()*1000))
    path=f"chats/{cid}.json"
    json.dump(messages, open(path,"w"), indent=2)
    con=sqlite3.connect(DB); cur=con.cursor()
    cur.execute("INSERT INTO chat VALUES (?,?,?,?)", (cid, name, path, time.time()))
    con.commit(); con.close()
    return cid, path

def load_chat(cid):
    con=sqlite3.connect(DB); cur=con.cursor()
    row=cur.execute("SELECT path FROM chat WHERE id=?",(cid,)).fetchone()
    con.close()
    return json.load(open(row[0])) if row else None
