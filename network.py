import db
import getpass
import weakref
import weakrefdict
import threading
import time
import connect as conn

user_info = {}

now_gid = 0
dbgmsg_cnt = 1000

fake_uid_table = {
    "a": "114514",
    "b": "1919810",
    "cxykevin": "1",
}
fake_nickname_table = {
    "a": "N/a",
    "b": "N/b",
    "cxykevin": "[N]cxykevin",
}
fake_passwd_table = {
    "a": "114514",
    "b": "1919810",
    "cxykevin": "1",
}
fake_session_table = {
    "a": "fake_session1",
    "b": "fake_session2",
    "cxykevin": "fake_session3",
}


def connect_with_session(username, session):
    global user_info
    # TODO
    if (session == ""):
        return False
    if (session == "fake_session2"):
        return False
    ######## Mock data ########
    user_info = {
        "username": username,
        "nickname": fake_nickname_table[username],
        "userid": fake_uid_table[username]
    }
    db.set_info("nickname", fake_nickname_table[username])
    db.set_info("session", fake_session_table[username])

    ######## Real data ########
    # ret = conn.send_msg({
    #     "Command": "LoginBySession",
    #     "ExInfomationObject": {
    #         "Session": session
    #     }
    # }, True)
    # if (ret["ErrorInfomation"]["ErrorCode"] != 0):
    #     return False
    # user_info = {
    #     "username": username,
    #     "nickname": ret["ExInfomationObject"]["Nickname"],
    #     "userid": ret["ExInfomationObject"]["UserGuid"]
    # }
    # db.set_info("nickname", ret["ExInfomationObject"]["Nickname"])
    # db.set_info("session", ret["ExInfomationObject"]["UserGuid"])
    return True


def connect_with_passwd(username, passwd):
    global user_info
    if (passwd == ""):
        return False

    ######## Mock data ########
    if (username not in fake_passwd_table):
        return None
    if (passwd != fake_passwd_table[username]):
        return False
    user_info = {
        "username": username,
        "nickname": fake_nickname_table[username],
        "userid": fake_uid_table[username]
    }
    db.set_info("nickname", fake_nickname_table[username])
    db.set_info("session", fake_session_table[username])

    ######## Real data ########
    # ret = conn.send_msg({
    #     "Command": "LoginByUnPw",
    #     "ExInfomationObject": {
    #         "Username": username,
    #         "Password": passwd
    #     }
    # }, True)
    # if (ret["ErrorInfomation"]["ErrorCode"] == 103):
    #     return False
    # elif (ret["ErrorInfomation"]["ErrorCode"] == 111):
    #     return None
    # elif (ret["ErrorInfomation"]["ErrorCode"] != 0):
    #     return False
    # user_info = {
    #     "username": username,
    #     "nickname": ret["ExInfomationObject"]["Nickname"],
    #     "userid": ret["ExInfomationObject"]["UserGuid"]
    # }
    # db.set_info("nickname", ret["ExInfomationObject"]["Nickname"])
    # db.set_info("session", ret["ExInfomationObject"]["LoginSession"])
    return True


def register(username, passwd):
    global user_info
    ######## Mock data ########
    user_info = {
        "username": username,
        "nickname": username,
        "userid": fake_uid_table.get(username, "hello")
    }
    return True
    ######## Real data ########
    # ret = conn.send_msg({
    #     "Command": "Register",
    #     "ExInfomationObject": {
    #         "Username": username,
    #         "Nickname": username,
    #         "Password": passwd
    #     }
    # }, True)
    # if (ret["ErrorInfomation"]["ErrorCode"] == 0):
    #     user_info = {
    #         "username": username,
    #         "nickname": username,
    #         "userid": ret["ExInfomationObject"]["UserGuid"]
    #     }
    #     db.set_info("session", ret["ExInfomationObject"]["LoginSession"])
    #     if (ret["ExInfomationObject"]["WarningSamePassword"]):
    #         print("密码可能与其它用户相同，建议尽快修改")
    #         input("[回车继续]")
    #     return True
    # else:
    #     return False


def connect():
    global user_info
    ip = db.get_info("server")
    # conn.connect(ip.split(":")[0], ip.split(":")[1])
    username = db.get_info("username")
    session = db.get_info("session")
    print(f"登录帐号 \"{username}\"\r")
    if (connect_with_session(username, session)):
        return True
    passwd = getpass.getpass("\r请输入密码（不会显示）：")
    if (passwd == ""):
        print("\r密码不能为空！")
        return False
    ret = connect_with_passwd(username, passwd)
    if (ret is True):
        return True
    elif (ret is False):
        return False
    else:
        passwd2 = getpass.getpass("\r请再次输入相同密码：")
        while (passwd != passwd2):
            passwd = getpass.getpass("\r密码不一致\r\n请输入密码（不会显示）：")
            passwd2 = getpass.getpass("\r请再次输入相同密码：")
        print("\r注册中...")
        if (register(username, passwd)):
            print("\r注册成功！")
            return True
        else:
            print("\r注册失败！")
            return False
    return False


def get_group_list():
    ######## Mock data ########
    return [
        {
            "name": "group1",
            "id": "114514",
            "last_msg": "the_last_msg",
            "msg_cnt": 0
        },
        {
            "name": "group2",
            "id": "1919810",
            "last_msg": "the_last_msg2",
            "msg_cnt": 123
        },
        {
            "name": "1group_other33333333333333333333333333333",
            "id": "114",
            "last_msg": "the_last_msg",
            "msg_cnt": 0
        },
        {
            "name": "2group_other33333333333333333333333333333",
            "id": "114",
            "last_msg": "the_last_msg",
            "msg_cnt": 0
        },
    ]
    ######## Real data ########


def load_msg_online(gid: int, last_msg_id: int):
    if (last_msg_id >= 10):
        return []
    return [weakrefdict.WeakReferencableDict({
            "from": "hello",
            "pos": "left", "msg": "hello world",
            "actions": {},
            "id": 10,
            "userid": 123
            })]


def load_msg(gid: int):
    global now_gid
    now_gid = gid
    msg = db.load_msg_history(gid)
    msg_online = load_msg_online(gid, (-1 if len(msg) == 0 else msg[-1]["id"]))
    for i in msg_online:
        db.save_msg_history(gid, i)
    return msg+msg_online


def send_online(old_db_id: int, weakref_dict: weakref.ReferenceType):
    global dbgmsg_cnt
    dbgmsg_cnt += 1
    time.sleep(1)
    weakref_dict()["id"] = dbgmsg_cnt
    db.replace_msg_history(old_db_id, weakref_dict())
    return True


def send(msg_info: str, weakref_dict: weakref.ReferenceType[weakrefdict.WeakReferencableDict]):
    ret = db.save_msg_history(now_gid, weakref_dict())
    threading.Thread(target=send_online, args=(
        ret, weakref_dict)).start()


def change_passwd(new_passwd: str):
    db.set_info("session", "")
    # TODO: 网络请求
    return ""


def remove_account():
    db.set_info("session", "")
    # TODO: 网络请求
    return ""


def change_nickname(nickname: str):
    # TODO: 网络请求
    return ""
