import db
import os
import config
import ip
import os
import sys
import network
import choose_group

os.makedirs(config.IM_CFG_PATH, exist_ok=True)
os.makedirs(config.IM_CFG_PATH+os.sep+"session", exist_ok=True)

print("\033[2J\033[1;1f\r")
print("StealthIM Console Client\r")
print("by cxykevin\r")
print("\r")


def new_session():
    server = input("\r输入服务器地址：")
    server = ip.base64_2_ip(server)
    username = input("\r输入用户名：")
    os.makedirs(config.IM_CFG_PATH+os.sep+"session" +
                os.sep+"user", exist_ok=True)
    if (os.path.exists(config.IM_CFG_PATH+os.sep+"session" +
       os.sep+"user"+os.sep+"user.db")):
        os.remove(config.IM_CFG_PATH+os.sep+"session" +
                  os.sep+"user"+os.sep+"user.db")
    db.init(config.IM_CFG_PATH+os.sep+"session" +
            os.sep+"user"+os.sep+"user.db", server, username, username)


def solve_ip():
    server = input("\r输入服务器地址：")
    print(ip.ip_2_base64(ip.base64_2_ip(server)))
    sys.exit(0)


if (len(sys.argv) > 1 and sys.argv[1] == "transform"):
    solve_ip()

if ((len(sys.argv) > 1 and sys.argv[1] == "login") or not os.path.exists(config.IM_CFG_PATH+os.sep+"session" +
                                                                         os.sep+"user")):
    new_session()

if (not network.connect()):
    print("\r登录失败！")
    sys.exit(1)

print("\r登录成功！")

choose_group.choose_group()
