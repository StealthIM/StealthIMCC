import sys
import shutil
from getchar import get_char
import time
import threading
import account
import db
import network
from textcalc import wrap


w = 0
h = 0
now_tab = 0
exit_flag = True
choose_cfg = 0


leftbar_lst = ["关于", "系统", "上传", "帐号"]

cfg_list = [
    [],
    [
        {"name": "\033[34m打开图片命令行\033[0m(使用%s替换图片)",
         "type": "input", "key": "img_open_cmd"},
        {"name": "\033[34m打开图片时阻塞\033[0m",
         "type": "bool", "key": "img_open_wait"}
    ],
    [
        {"name": "\033[34m图床api模块名\033[0m\n\033[90m可用：\033[0m\n\033[90m  xesoss 学而思编程OSS存储\033[0m\n\033[90m  yiyunt 一云图床\033[0m\n\033[90m  custom 用户自定义\033[0m", "type": "input",
         "key": "img_api_module_name"},
        {"name": "\033[34mapikey(根据API选填)\033[0m", "type": "input",
         "key": "img_api_key"},
    ],
    [
        {"name": "\033[34m更改用户昵称\033[0m", "type": "input",
         "key": "nickname"},
        {"name": "\033[34m保存用户昵称\033[0m", "type": "button",
         "text": "保存昵称", "func": account.change_nickname},
        {"name": "\033[34m登出账户\033[0m", "type": "button",
         "text": "登出账户", "func": account.logout},
        {"name": "\033[34m更改账户密码\033[0m", "type": "button",
         "text": "更改密码", "func": account.ch_passwd},
        {"name": "\033[34m永久注销账户\033[0m", "type": "button",
         "text": "注销帐户", "func": account.remove_account},
    ]
]

cfg_val = {
    "img_open_cmd": r"%s",
    "img_open_wait": True,
    "img_api_module_name": "xesoss",
    "img_api_key": "",
    "nickname": ""
}


def init():
    global cfg_val
    cfg_val["nickname"] = network.user_info["nickname"]
    for k, v in cfg_val.items():
        if (type(v) == bool):
            v_tmp = ("true" if v else "false")
        else:
            v_tmp = v
        db.init_info("set_"+k, v_tmp)
        ret = db.get_info("set_"+k)
        if (type(v) == bool):
            if (ret == "true"):
                cfg_val[k] = True
            else:
                cfg_val[k] = False
        else:
            cfg_val[k] = ret


def save():
    global cfg_val
    for k, v in cfg_val.items():
        if (type(v) == bool):
            v_tmp = ("true" if v else "false")
        else:
            v_tmp = v
        db.set_info("set_"+k, v_tmp)


def input():
    global w, h, now_tab, exit_flag, choose_cfg, function_call
    while 1:
        ch = get_char()
        if ch == b'\x1b':
            next_byte = get_char()
            if next_byte == b'[':
                next_byte = get_char()
                if next_byte == b'5':
                    next_byte = get_char()
                    if next_byte == b'~':
                        now_tab -= 1
                        if now_tab < 0:
                            now_tab = len(leftbar_lst)-1
                        choose_cfg = 0
                elif next_byte == b'6':
                    next_byte = get_char()
                    if next_byte == b'~':
                        now_tab += 1
                        if now_tab >= len(leftbar_lst):
                            now_tab = 0
                        choose_cfg = 0
            else:
                exit_flag = False
                return
        elif (ch == b'\t'):
            choose_cfg += 1
            if (choose_cfg >= len(cfg_list[now_tab])):
                choose_cfg = 0
        elif (ch == b'\x7f'):
            if (cfg_list[now_tab][choose_cfg]["type"] == "input"):
                cfg_val[cfg_list[now_tab][choose_cfg]["key"]
                        ] = cfg_val[cfg_list[now_tab][choose_cfg]["key"]][:-1]
        elif (ch == b'\n'):
            choose_cfg += 1
            if (choose_cfg >= len(cfg_list[now_tab])):
                choose_cfg = 0
        elif (ch == b' ' and cfg_list[now_tab][choose_cfg]["type"] == "bool"):
            cfg_val[cfg_list[now_tab][choose_cfg]["key"]
                    ] = not cfg_val[cfg_list[now_tab][choose_cfg]["key"]]
        elif (ch == b' ' and cfg_list[now_tab][choose_cfg]["type"] == "button"):
            function_call = cfg_list[now_tab][choose_cfg]["func"]
            return
        elif (ch in b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789[]-=_+;\'\"\\|<>.,?/:;!@#$%^&*(){}[] '):
            try:
                if (cfg_list[now_tab][choose_cfg]["type"] == "input"):
                    cfg_val[cfg_list[now_tab][choose_cfg]["key"]
                            ] += ch.decode("utf-8")
            except IndexError:
                pass
        flush()


def flush():
    global w, h, now_tab, exit_flag, choose_cfg
    w, h = shutil.get_terminal_size()
    sys.stdout.write("\033[2J\033[0m\033[3;1H")
    sys.stdout.write("\033[90m+--+"+"-"*(w-5)+"+\033[0m\r\n")
    for i in range(h-4):
        sys.stdout.write("   \033[90m|\033[0m" +
                         " "*(w-5)+"\033[90m|\033[0m\r\n")
    sys.stdout.write("   \033[90m+"+"-"*(w-5)+"+\033[0m")
    sys.stdout.write(
        "\033[1;5H\033[0m\033[1m\033[34m设置\033[0m  [ESC*2] 返回    [TAB] 切换焦点\r\n          [PAGEUP/DOWN] 翻页")

    ln_cnt = 4
    tab_cnt = 0
    for i in leftbar_lst:
        for j in i:
            sys.stdout.write(
                f"\033[{ln_cnt};1H\033[0m\033[90m|\033[0m{"\033[34m\033[1m" if tab_cnt == now_tab else ""}{j}{"\033[0m" if tab_cnt == now_tab else ""}\033[90m|\033[0m")
            ln_cnt += 1
        sys.stdout.write(f"\033[{ln_cnt};1H\033[0m\033[90m+--+\033[0m")
        ln_cnt += 1
        tab_cnt += 1

    if (now_tab == 0):
        sys.stdout.write(
            f"\033[5;10H\033[0m\033[1m\033[34mStelthIM Console Client\033[6;10H\033[0mby cxykevin\033[7;10Hversion 0.0.1")
    else:
        now_ln_st = 5
        now_ln = 0
        page_offset = 0
        start_left = 7
        txt_tmp_all = ""
        now_cfg = 0
        for i in cfg_list[now_tab]:
            txt_tmp = wrap(i["name"], w-start_left-3)
            for j in txt_tmp.split("\n"):
                txt_tmp_all += f"\033[{now_ln_st+now_ln-page_offset};{start_left}H"+j
                now_ln += 1
                if (now_ln-page_offset > h-2-now_ln_st):
                    break
            if (now_ln-page_offset > h-2-now_ln_st):
                break
            txt_tmp_all += f"\033[{now_ln_st+now_ln-page_offset};{start_left}H"
            if (now_cfg == choose_cfg):
                txt_tmp_all += "\033[1m\033[32m>\033[0m"
            else:
                txt_tmp_all += " "
            if (i["type"] == "bool"):
                if (cfg_val[i["key"]]):
                    txt_tmp_all += "\033[32m[X]\033[0m 启用"
                else:
                    txt_tmp_all += "\033[31m[ ]\033[0m 禁用"
            elif (i["type"] == "input"):
                txt_tmp_all += f"\033[90m[\033[0m{cfg_val[i["key"]]}\033[90m{"."*(w-start_left-3-1-1-len(cfg_val[i["key"]]))}]\033[0m"
            elif (i["type"] == "button"):
                txt_tmp_all += f"\033[31m[\033[0m\033[41m{i["text"]}\033[0m\033[31m]\033[0m"
            now_ln += 1
            if (now_ln-page_offset > h-2-now_ln_st):
                break
            now_ln += 1
            if (now_ln-page_offset > h-2-now_ln_st):
                break
            now_cfg += 1
        sys.stdout.write(txt_tmp_all)
    sys.stdout.flush()


def start():
    global w, h, now_tab, exit_flag, choose_cfg, function_call
    init()
    function_call = None
    choose_cfg = 0
    now_tab = 0
    exit_flag = True
    threading.Thread(target=input).start()
    while exit_flag:
        flush()
        if (function_call):
            save()
            function_call()
            threading.Thread(target=input).start()
            function_call = None
        time.sleep(0.1)
    save()
