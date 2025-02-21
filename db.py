import sqlite3
import config
import os
import weakrefdict
db_path = config.IM_CFG_PATH+os.sep+"session"+os.sep+"user"+os.sep+"user.db"


def init(db_path: str, server: str, username: str, nickname: str):
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE info (k TEXT PRIMARY KEY,v TEXT);")
    conn.execute("INSERT INTO info VALUES ('server', ?);", (server,))
    conn.execute("INSERT INTO info VALUES ('username', ?);", (username,))
    conn.execute("INSERT INTO info VALUES ('nickname', ?);", (nickname,))
    conn.execute("INSERT INTO info VALUES ('session', ?);", ("",))
    conn.execute("""CREATE TABLE history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        msgid INT,
        groupid INT,
        nickname TEXT,
        userid TEXT,
        self BOOLEAN,
        msg TEXT,
        at_list TEXT,
        type TEXT
    );""")
    conn.execute("""CREATE TABLE drafts (
        groupid INTEGER PRIMARY KEY,
        msg TEXT
    );""")
    conn.commit()
    conn.close()


def get_info(key: str):
    conn = sqlite3.connect(db_path)
    c = conn.execute("SELECT v FROM info WHERE k = ?;", (key,))

    return c.fetchone()[0]


def set_info(key: str, value: str):
    conn = sqlite3.connect(db_path)
    conn.execute("UPDATE info SET v = ? WHERE k = ?;", (value, key))
    conn.commit()
    conn.close()


def init_info(key: str, value: str):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT OR IGNORE INTO info (k, v) VALUES (?, ?);", (key, value))
    conn.commit()
    conn.close()


def load_msg_history(gid: int):
    global conn
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    # 执行查询
    cursor.execute("SELECT * FROM history WHERE groupid = ?;", (gid,))

    # 获取所有匹配的记录
    records = cursor.fetchall()

    return [weakrefdict.WeakReferencableDict({
        "from": i[3],
        "pos": ("right" if i[5] else "left"),
        "msg": i[6],
        "actions": {},
        "userid": i[4],
        "id": i[1]
    }) for i in records]


def save_msg_history(gid: int, msg: weakrefdict.WeakReferencableDict):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO history VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?);", (
        msg["id"], gid, msg["from"], msg["userid"], msg["pos"] == "right", msg["msg"], msg.get(
            "at_list", ""), "markdown"
    ))
    conn.commit()
    conn.close()
    return cursor.lastrowid


def replace_msg_history(msgid: str, msg: weakrefdict.WeakReferencableDict):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # 刷新所有项目
    cursor.execute(
        "UPDATE history SET msg = ?,msgid = ?,at_list = ? WHERE id = ?;", (msg["msg"], msg["id"], msg.get(
            "at_list", ""), msgid))
    conn.commit()
    conn.close()
