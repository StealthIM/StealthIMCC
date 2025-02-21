import sys
import getchar
import getpass
import network
import db
import time
import os


def change_nickname():
    getchar.disable_base_mode()
    ret = network.change_nickname(db.get_info("set_nickname"))
    if (ret == ""):
        getchar.enable_base_mode()
        sys.stdout.write("\033[2J\033[1;1f\033[34m\033[1m昵称修改成功！\033[0m\n")
        network.user_info["nickname"] = db.get_info("set_nickname")
        getchar.get_char()
    else:
        getchar.enable_base_mode()
        sys.stdout.write("\033[2J\033[1;1f\033[1m更改昵称失败！\033[0m\r\n"+ret)
        getchar.get_char()


def logout():
    db.set_info("session", "")
    getchar.disable_base_mode()
    sys.stdout.write("\033[2J\033[1;1f")
    sys.exit(0)


def ch_passwd():
    getchar.disable_base_mode()
    sys.stdout.write("\033[2J\033[1;1f更改用户密码\r\n")
    pass1 = getpass.getpass("\r输入新密码(不会显示): ")
    pass2 = getpass.getpass("\r重复输入密码(不会显示): ")
    while pass1 != pass2 or pass1 == "":
        sys.stdout.write("\r\n\033[31m\033[1m密码为空或不匹配，请重新输入！\033[0m\r\n")
        pass1 = getpass.getpass("\r输入新密码(不会显示): ")
        pass2 = getpass.getpass("\r重复输入密码(不会显示): ")
    ret = network.change_passwd(pass1)
    if (ret == ""):
        sys.stdout.write("\033[2J\033[1;1f\033[32m\033[1m密码修改成功！\033[0m\n")
        sys.exit(0)
    else:
        getchar.enable_base_mode()
        sys.stdout.write("\033[2J\033[1;1f\033[1m更改密码失败！\033[0m\r\n"+ret)
        getchar.get_char()


def remove_account():
    getchar.disable_base_mode()
    sys.stdout.write("\033[2J\033[1;1f\033[31m\033[1m注销用户！\033[0m\r\n")
    sys.stdout.write("\033[31m此操作无法还原！\r\n此操作无法还原！\r\n此操作无法还原！\033[0m\r\n")
    sys.stdout.write("\033[31m请三思而后行！\033[0m\r\n")
    for i in range(3):
        sys.stdout.write("\r\033[31m\033[2m倒计时：\033[0m"+str(3-i))
        time.sleep(1)
    sys.stdout.write("\r\033[31m请在下面输入你的用户名以确认注销：\033[0m\r\n")
    username = input()
    if (network.user_info["username"] != username):
        sys.stdout.write("\033[2J\033[1;1f\033[31m用户名不匹配！\033[0m\r\n")
        sys.exit(1)
    ret = network.remove_account()
    os.remove(db.db_path)
    sys.stdout.write(
        "\033[2J\033[1;1f\033[32m\033[1m注销成功！\033[0m\n感谢您的使用，愿我们下次再见!")
    sys.exit(0)
