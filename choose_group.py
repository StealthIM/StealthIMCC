import network
import sys
import shutil
from getchar import enable_base_mode, disable_base_mode, get_char
import threading
import time
import chat
import settings
import groupinfo


def choose_group():
    w, h = shutil.get_terminal_size()
    group_lst = network.get_group_list()
    enable_base_mode()
    exit_flag = True
    offset_block = 0
    start_page = 0
    msg_info = ""
    start_ginfo = 0

    def flush():
        nonlocal offset_block, w, h, msg_info
        w, h = shutil.get_terminal_size()
        sys.stdout.write("\033[2J\033[0m\033[?25l")
        sys.stdout.write(f"\033[0;0f")
        cnt = 0
        ln_cnt = 0
        offset_block = max(0, min(offset_block, (len(group_lst)*3-h)//3+1))
        for i in group_lst[offset_block:]:
            cnt += 1
            if (ln_cnt >= h-3):
                break
            sys.stdout.write(
                f"\033[36m{"["+str(cnt)+"]":>5}\033[0m \033[1m{i["name"][:w-8]}\033[0m\r\n")
            ln_cnt += 1
            if (ln_cnt >= h-3):
                break
            sys.stdout.write(
                f"\033[31m{(""if i["msg_cnt"] == 0 else str(i["msg_cnt"])):>5}\033[0m \033[90m{i["last_msg"][:w-8]}\033[0m\r\n")
            ln_cnt += 1
            if (ln_cnt >= h-3):
                break
            sys.stdout.write(" "+"-"*(w-2)+" \r\n")
            ln_cnt += 1
        sys.stdout.write(f"\033[{h-2};0f")
        sys.stdout.write("="*(w)+"\r\n")
        sys.stdout.write(f"\033[{h-1};0f")
        if (not msg_info):
            sys.stdout.write(
                "[ESC*2] 退出      [s] 设置  \r\n[1-9]   进入群聊  [m] 更多")
        else:
            sys.stdout.write(f"{msg_info}")

    def input():
        nonlocal exit_flag
        nonlocal offset_block, group_lst, msg_info, start_page, start_ginfo
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
                            offset_block += min(h//6, 9)
                else:
                    exit_flag = False
                    break
            elif (ch in (b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9')):
                rel_id = max(0, offset_block) + int(ch)-1
                if rel_id > len(group_lst):
                    continue
                msg_info = ("加载聊天记录中")
                ret = network.load_msg(group_lst[rel_id]["id"])
                ret.reverse()
                chat.main(
                    ret, network.user_info["nickname"], network.user_info["userid"], network.send)
                start_page = 1
                msg_info = ""
                break
            elif (ch == b"s"):
                start_page = 2
                msg_info = ""
                break
            elif (ch == b"m"):
                msg_info = ("[x] 返回          [a] 添加好友/群聊\r\n[1-9] 查看群聊信息")
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
                                    offset_block += min(h//6, 9)
                    elif ch == b'x':
                        msg_info = ""
                        break
                    elif (ch in (b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9')):
                        rel_id = max(0, offset_block) + int(ch)-1
                        if rel_id > len(group_lst):
                            continue
                        gid = group_lst[rel_id]["id"]
                        start_ginfo = gid
                        start_page = 3
                        msg_info = ""
                        return
                msg_info = ""

    threading.Thread(target=input).start()

    while exit_flag:
        flush()
        if (start_page == 1):
            chat.start()
            threading.Thread(target=input).start()
            start_page = 0
        elif (start_page == 2):
            settings.start()
            threading.Thread(target=input).start()
            start_page = 0
        elif (start_page == 3):
            groupinfo.run(start_ginfo)
            threading.Thread(target=input).start()
            start_page = 0
        time.sleep(0.1)
    disable_base_mode()
