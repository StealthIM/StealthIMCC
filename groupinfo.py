import network
import sys
import shutil
from getchar import get_char
import threading
import time
from textcalc import wrap


def run(group_id: str):
    group_info = network.get_group_info(group_id)
    w, h = shutil.get_terminal_size()
    exit_flag = True
    offset_block = 0
    msg_info = ""
    boardcast_id = -1
    now_ln = 0

    def flush():
        nonlocal offset_block, w, h, msg_info, boardcast_id, now_ln
        w, h = shutil.get_terminal_size()
        sys.stdout.write("\033[2J\033[0m\033[?25l")
        sys.stdout.write(f"\033[0;0f")
        sys.stdout.write(
            "\033[1m\033[34m群聊信息\033[0m  [ESC*2] 退出\r\n")
        sys.stdout.write(
            "="*w+"\r\n")
        sys.stdout.write("\033[32m* \033[90m群聊名称:\033[0m " +
                         group_info["name"][:max(w-14, 0)]+"\r\n")
        sys.stdout.write("\033[32m* \033[90m群聊ID:\033[0m " +
                         group_info["id"][:max(w-14, 0)]+"\r\n")

        def show_usertype(usertype):
            if (usertype == "owner"):
                text = "\033[33m[\033[0m\033[43m群主\033[0m\033[33m]\033[0m"
            elif (usertype == "manager"):
                text = "\033[34m[\033[0m\033[44m管理\033[0m\033[34m]\033[0m"
            else:
                text = "\033[90m[\033[0m\033[100m群员\033[0m\033[90m]\033[0m"
            return text
        sys.stdout.write("\033[32m* \033[90m我的身份:\033[0m " +
                         wrap(show_usertype(group_info["nowuser_type"]), w-14).split("\n")[0]+"\r\n\r\n")
        sys.stdout.write(
            "\033[34m群公告\033[0m\r\n")
        if (len(group_info["boardcast"]) > 0 and boardcast_id != -1):
            sys.stdout.write(
                "="*(max(w-20, 0)))
            sys.stdout.write(
                " [,]上一条 下一条[.]\r\n")
            wrap_text = wrap(group_info["boardcast"][boardcast_id], w)
            wp_len = len(wrap_text.split("\n"))
            sys.stdout.write(
                wrap_text.replace("\n", "\r\n"))
            sys.stdout.write("\r\n")
            sys.stdout.write("="*w)
            sys.stdout.write("\r\n")
            wp_len += 2
        else:
            sys.stdout.write(
                "="*(max(w-14, 0)))
            sys.stdout.write(
                " 显示群公告[.]\r\n")
            wp_len = 0
        now_ln = max(0, h-(wp_len+11))
        if (now_ln > 0):
            sys.stdout.write(
                "\r\n\033[34m用户列表\033[0m\r\n")
            sys.stdout.write(
                "="*(max(w-5-len(str(len(group_info['users']))), 0))+f" 共{len(group_info['users'])}人")

        sys.stdout.write('\r\n'.join([f"\033[36m{"["+str(i_cnt+1)+"]":>4} \033[0m"+wrap(i["nickname"]+(show_usertype(
            i["type"]))+" \033[90m("+i["username"]+")\033[0m", w-5).split("\n")[0]+"\033[0m" for i_cnt, i in enumerate(group_info["users"][offset_block:offset_block+now_ln])]))

    def input():
        nonlocal exit_flag
        nonlocal offset_block, msg_info, boardcast_id, now_ln
        while 1:
            ch = get_char()
            if ch == b'\x1b':
                next_byte = get_char()
                if next_byte == b'[':
                    next_byte = get_char()
                    if next_byte == b'5':
                        next_byte = get_char()
                        if next_byte == b'~':
                            offset_block -= min(h//6, 9)
                            if offset_block < 0:
                                offset_block = 0
                    elif next_byte == b'6':
                        next_byte = get_char()
                        if next_byte == b'~':
                            offset_block += max(min(now_ln//2, 9), 1)
                            if offset_block > len(group_info["users"])-1:
                                offset_block = len(group_info["users"])-1
                else:
                    exit_flag = False
                    break
            elif (ch in (b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9')):
                pass
            #     rel_id = max(0, offset_block) + int(ch)-1
            #     if rel_id > len(group_lst):
            #         continue
            #     msg_info = ("加载聊天记录中")
            #     ret = network.load_msg(group_lst[rel_id]["id"])
            #     ret.reverse()
            #     chat.main(
            #         ret, network.user_info["nickname"], network.user_info["userid"], network.send)
            #     start_page = 1
            #     msg_info = ""
            #     break
            elif (ch == b","):
                if (boardcast_id <= -1):
                    boardcast_id = -1
                else:
                    boardcast_id -= 1
                flush()
            elif (ch == b"."):
                if (boardcast_id+1 >= len(group_info["boardcast"])):
                    boardcast_id = len(group_info["boardcast"])-1
                else:
                    boardcast_id += 1
                flush()

    threading.Thread(target=input).start()

    while exit_flag:
        flush()
        time.sleep(0.1)
