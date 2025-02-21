import shutil
import sys
import time
import threading
import render
import platform
import weakrefdict
import openimg
from char_calc import char_width, char_width_b
from getchar import get_char, enable_base_mode, disable_base_mode
try:
    import webbrowser
except ImportError:
    pass
import upload_modules

os_name = platform.system()

inputed_str = [[]]  # 初始化输入字符串列表，每个元素是一个字符(bytes)列表
show_ln = 0
cursor = (0, 0)  # 光标位置，(行, 列)
cursor_select = (0, 0)  # 选择起点光标位置，(行, 列)
cursor_select_mode = False  # 是否处于选择模式
window = (0, 0)  # 输入窗口原点，(宽, 高)
msgs = []
w = 80  # 窗口宽度
h = 24  # 窗口高度
show_menu = False  # 是否显示菜单
menustr = ""  # 菜单字符串
content_offset = 0  # 内容偏移量，用于滚动显示内容

username = "You"

MAX_SHOW_LN = 5  # 定义输入时最大显示行数为5
MSG_SPACE = 6  # 定义消息与边框的空格数为6
BG_COLOR = "\033[0m"

disable_flush = False  # 禁用刷新的标志
fullscreen_input = False  # 全屏输入的标志

choose_id_lst = {}

w_cache = {}
w_cache_info = 0
refresh_lock = False

exit_flag = False
userid = 0


def send_func(msg): return None


def main(input_msg, nickname, s_userid, send_func_r):
    global inputed_str, show_ln, cursor, cursor_select, cursor_select_mode, window, msgs, w, h, show_menu, menustr, content_offset, username, MAX_SHOW_LN, MSG_SPACE, BG_COLOR, disable_flush, fullscreen_input, choose_id_lst, w_cache, w_cache_info, refresh_lock, exit_flag, send_func, userid
    send_func = send_func_r
    userid = s_userid
    inputed_str = [[]]  # 初始化输入字符串列表，每个元素是一个字符(bytes)列表
    show_ln = 0
    cursor = (0, 0)  # 光标位置，(行, 列)
    cursor_select = (0, 0)  # 选择起点光标位置，(行, 列)
    cursor_select_mode = False  # 是否处于选择模式
    window = (0, 0)  # 输入窗口原点，(宽, 高)
    msgs = input_msg
    w = 80  # 窗口宽度
    h = 24  # 窗口高度
    show_menu = False  # 是否显示菜单
    menustr = ""  # 菜单字符串
    content_offset = 0  # 内容偏移量，用于滚动显示内容

    username = nickname

    MAX_SHOW_LN = 5  # 定义输入时最大显示行数为5
    MSG_SPACE = 6  # 定义消息与边框的空格数为6
    BG_COLOR = "\033[0m"

    disable_flush = False  # 禁用刷新的标志
    fullscreen_input = False  # 全屏输入的标志

    choose_id_lst = {}

    w_cache = {}
    w_cache_info = 0
    refresh_lock = False

    exit_flag = False


def calc_ln():  # 计算从字符串 inputed_str 的起始位置到光标位置之间的字符宽度总和
    cnt = 0
    for i in inputed_str[cursor[1]][:cursor[0]]:
        cnt += char_width_b(i)
    return cnt


def calc_ln_al():
    cnt = 0
    for i in inputed_str[cursor[1]]:
        cnt += char_width_b(i)
    return cnt


def warp(width: int, txt_base: str, bg_ansi: str = "\033[0m", left_str: str = "", msg_obj: int = -1, lspace: int = 2, rspace: int = 2):
    txt, info = render.process_markdown(txt_base, width-lspace-rspace)
    if (msg_obj != -1):
        msgs[msg_obj]["actions"] = info
    txt = txt.rstrip(" \n\r\t")
    while (txt.endswith("\033[0m")):
        txt = txt[:-4].rstrip(" \n\r\t")
    txt += "\033[0m"
    txt = txt.replace("\033[0m", "\033[0m"+bg_ansi)
    strs = [left_str+bg_ansi]  # 初始化strs列表，包含左边界字符串和背景ANSI代码
    strs[-1] += "+"
    strs[-1] += "-"*(width-2)  # 在最后一个字符串中添加width个空格
    strs[-1] += "+"
    strs[-1] += "\033[0m"  # 在最后一个字符串中添加ANSI重置代码
    strs.append(left_str + bg_ansi)  # 将左侧字符串和背景ANSI代码拼接后添加到strs列表中
    strs[-1] += "|"
    strs[-1] += " "*(lspace-1)
    width_sum = 0
    now_ansi_mode = False
    last_ansi_full_text = ""
    width_r = width-lspace-rspace
    char_w = 0
    for i in txt:
        if (i == "\033"):  # 如果字符是ANSI转义字符（\033）
            now_ansi_mode = True
            last_ansi_full_text += i  # 更新上一个ANSI转义完整内容
            strs[-1] += i
            continue  # 跳过当前循环，继续下一个字符
        elif (now_ansi_mode and (i.isupper() or i.islower())):  # 如果当前处于ANSI模式且字母，退出ANSI模式
            now_ansi_mode = False
            last_ansi_full_text += i  # 添加字符到上一个ANSI转义完整内容
            strs[-1] += i
            continue  # 跳过当前循环，继续下一个字符
        elif (now_ansi_mode):  # 如果当前处于ANSI模式且字符不是大写或小写字母
            last_ansi_full_text += i  # 添加字符到上一个ANSI转义完整内容
            strs[-1] += i
            continue  # 跳过当前循环，继续下一个字符
        if (last_ansi_full_text.endswith("\033[0m")):
            last_ansi_full_text = ""
        char_w = char_width(i)
        if (i == "\n"):
            strs[-1] += " "*(width_r-width_sum)
            strs[-1] += " "*(rspace-1)
            strs[-1] += "\033[0m|"
            strs[-1] += "\033[0m"  # 在当前行的末尾添加ANSI重置代码
            # 添加新的行，包含左侧字符串、背景ANSI代码和上一个ANSI转义
            strs.append(left_str + bg_ansi)
            strs[-1] += "|"
            strs[-1] += " "*(lspace-1)  # 在新行的开头添加左侧边距的空格
            strs[-1] += last_ansi_full_text
            width_sum = 0  # 重置宽度总和为0，准备计算新行的宽度
        elif (width_sum+char_w > width_r):
            strs[-1] += " "*(width_r-width_sum)
            strs[-1] += " "*(rspace-1)
            strs[-1] += "\033[0m|"
            strs[-1] += "\033[0m"
            strs.append(left_str + bg_ansi)
            strs[-1] += "|"
            strs[-1] += " "*(lspace-1)  # 在新行的开头添加左侧边距的空格
            strs[-1] += last_ansi_full_text
            strs[-1] += i
            width_sum = char_w
        else:
            strs[-1] += i
            width_sum += char_w
    strs[-1] += " "*(width_r-width_sum)
    strs[-1] += " "*(rspace-1)
    strs[-1] += "\033[0m|"
    strs[-1] += "\033[0m"
    strs.append(left_str + bg_ansi)
    strs[-1] += "+"
    strs[-1] += "-"*(width-2)  # 在最后一个字符串中添加width个空格
    strs[-1] += "+"
    strs[-1] += "\033[0m"
    return strs


def calc_msg_h(i):
    out_str_tmp = 0
    if (i["pos"] == "left"):
        out_str_tmp += len((warp(w -
                                 MSG_SPACE-1, i["msg"], BG_COLOR, "")))
        out_str_tmp += 2
    else:
        out_str_tmp += len((warp(w-MSG_SPACE-1, i["msg"],
                                 BG_COLOR, " "*MSG_SPACE)))
        out_str_tmp += 2
    return out_str_tmp


def refresh(access_refresh_lock=False):
    global inputed_str, cursor, cursor_select_mode, window, w, h, show_menu, show_ln, content_offset, MAX_SHOW_LN, choose_id_lst, w_cache, w_cache_info, refresh_lock
    if (refresh_lock and access_refresh_lock):
        return
    refresh_lock = True
    if (disable_flush):
        return
    w, h = shutil.get_terminal_size()
    out_lst = b""

    def write(st):
        nonlocal out_lst
        if (type(st) == str):
            st = st.encode()
        out_lst += st
    write("\033[2J\033[0m\033[?25l")
    write(f"\033[0;0f")
    out_str = ""
    show_choose_id = 0
    ln_sum = 0
    msg_id = -1
    choose_id_lst = {}
    id_sum = -1
    for i in msgs:
        msg_id += 1
        id_sum += 1
        if (ln_sum > h-show_ln+content_offset):
            break
        if (w == w_cache_info):
            out_str_tmp = w_cache[i["id"]]
            out_str = out_str_tmp+out_str
            continue
        out_str_tmp = ""
        if (i["pos"] == "left"):
            out_str_tmp += (" "if (i["id"] != -1)else "\033[41m!\033[0m")+f"\033[35m[{show_choose_id}]\033[34m" + \
                i["from"]+"\033[0m\r\n"
            out_str_tmp += '\r\n'.join(warp(w -
                                       MSG_SPACE-1, i["msg"], BG_COLOR, "", id_sum))
            out_str_tmp += '\r\n'
            ln_sum += len(out_str_tmp.split("\n"))-1
            if (ln_sum > content_offset):
                show_choose_id += 1
                out_str_tmp = ""
                out_str_tmp += (" "if (i["id"] != -1)else "\033[41m!\033[0m")+f"\033[35m[{show_choose_id}]\033[34m" + \
                    i["from"]+"\033[0m\r\n"
                out_str_tmp += '\r\n'.join(warp(w-MSG_SPACE-1,
                                                i["msg"], BG_COLOR, "", id_sum))
                out_str_tmp += '\r\n'
        else:
            out_str_tmp += (" "*(w-2-len(i["from"])-2-len(str(show_choose_id))) +
                            "\033[34m"+i["from"]+f"\033[0m\033[35m[{show_choose_id}]\033[0m"+(" "if (i["id"] != -1)else "\033[41m!\033[0m")+"\r\n")
            out_str_tmp += '\r\n'.join(warp(w-MSG_SPACE-1, i["msg"],
                                            BG_COLOR, " "*MSG_SPACE, id_sum))
            out_str_tmp += '\r\n'
            ln_sum += len(out_str_tmp.split("\n"))-1
            if (ln_sum > content_offset):
                show_choose_id += 1
                out_str_tmp = ""
                out_str_tmp += (" "*(w-2-len(i["from"])-2-len(str(show_choose_id))) +
                                "\033[34m"+i["from"]+f"\033[0m\033[35m[{show_choose_id}]\033[0m"+(" "if (i["id"] != -1)else "\033[41m!\033[0m")+"\r\n")
                out_str_tmp += '\r\n'.join(warp(w-MSG_SPACE-1, i["msg"],
                                                BG_COLOR, " "*MSG_SPACE, id_sum))
                out_str_tmp += '\r\n'
        w_cache[i["id"]] = out_str_tmp
        out_str = out_str_tmp+out_str
        if (0 < show_choose_id <= 9):
            choose_id_lst[show_choose_id] = msg_id
    if (show_menu):
        show_ln = 5
    else:
        if (fullscreen_input):
            MAX_SHOW_LN = h-1
        else:
            MAX_SHOW_LN = 5
        show_ln = min(len(inputed_str), MAX_SHOW_LN)
    out_str_lst = out_str.rstrip("\r\n").split("\r\n")
    if (content_offset > max(0, len(out_str_lst)-(h-show_ln+1)+2)):
        content_offset = max(0, len(out_str_lst)-(h-show_ln+1)+2)
    out_str_lst = out_str_lst[
        max(0, len(out_str_lst)-(h-show_ln+1)+2)-content_offset:len(out_str_lst)-content_offset]
    write('\r\n'.join(out_str_lst))

    write(f"\033[0;0f\033[0m")
    right_text = "^PGUP PGDNv"
    cnt = 2
    for i in right_text:
        write(f"\033[{cnt};{w}f{i}")
        cnt += 1
    write(f"\033[0;0f")

    write(f"\033[{h-min(MAX_SHOW_LN, show_ln)};0f")
    wh_text1 = "[Menu CTRL+X]"
    if (len(inputed_str[0]) != 0):
        wh_text2 = " [Send CTRL+C]"
    else:
        wh_text2 = ""
    write("="*(w-len(wh_text1)-len(wh_text2)-2) +
          " \033[38;5;214m"+wh_text1 + "\033[0m"+"\033[1;32m" + wh_text2+" \033[0m")
    write(f"\033[{h-min(MAX_SHOW_LN, show_ln)};0f")

    if (show_menu):
        write("\r\n")
        write(menustr)
        sys.stdout.write(out_lst.decode())
        return

    ln = window[1]+1
    for i in inputed_str[window[1]:MAX_SHOW_LN+window[1]]:
        write("\r\n")
        write("\033[0m\033[K")
        write("\x1b[34m "*(5-len(str(ln))) +
              str(ln) + "\033[0m \x1b[38;5;240m"+("| " if window[0] == 0 else "||")+"\033[0m")
        now_sumlen = 0
        now_sumchar = 0
        screenw = w-9
        sumlen_flag = window[0] != 0
        for char in i:
            now_sumlen += char_width_b(char)
            if (sumlen_flag and now_sumlen < window[0]):
                continue
            elif (sumlen_flag and window[0] != 0 and now_sumlen > window[0]):
                write("\x1b[34m<\x1b[39m")
                now_sumlen = 1
                sumlen_flag = False
                continue
            elif (sumlen_flag and (now_sumlen == window[0] and window[0] != 0)):
                now_sumlen = 0
                sumlen_flag = False
                continue
            now_sumchar += 1
            if (cursor_select_mode):
                cursor_tmp_1 = cursor
                cursor_tmp_2 = cursor_select
                if (cursor[1] > cursor_select[1]):
                    cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
                elif (cursor[1] == cursor_select[1]):
                    if (cursor[0] > cursor_select[0]):
                        cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
                if (cursor_tmp_1[1] < ln-1 < cursor_tmp_2[1]):
                    write("\033[47m\033[30m")
                elif (ln-1 == cursor_tmp_1[1] == cursor_tmp_2[1]):
                    if (cursor_tmp_1[0] < now_sumchar <= cursor_tmp_2[0]):
                        write("\033[47m\033[30m")
                elif (ln-1 == cursor_tmp_1[1] and now_sumchar > cursor_tmp_1[0]):
                    write("\033[47m\033[30m")
                elif (ln-1 == cursor_tmp_2[1] and now_sumchar <= cursor_tmp_2[0]):
                    write("\033[47m\033[30m")
            if (now_sumlen > screenw):
                write("\x1b[34m>\x1b[39m")
                break
            write(char.decode())
            write("\033[0m")
        ln += 1

    write(
        f"\033[{h+1-min(len(inputed_str), MAX_SHOW_LN)+cursor[1]-window[1]};{max(calc_ln()+8-window[0]+1, 9)}f\033[?25h")
    sys.stdout.write(out_lst.decode())
    refresh_lock = False


def get_output():
    global inputed_str
    out_str = ""
    for i in inputed_str:
        out_str += b''.join(i).decode()
        out_str += "\n"
    return out_str.rstrip("\n")


def input_th():
    global inputed_str, cursor, cursor_select, cursor_select_mode, exit_flag, window, w, h, menustr, show_menu, content_offset, fullscreen_input

    def common_input(read_chr):
        global inputed_str, cursor, cursor_select, cursor_select_mode, window
        if (cursor_select_mode):
            cursor_tmp_1 = cursor
            cursor_tmp_2 = cursor_select
            if (cursor[1] > cursor_select[1]):
                cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
            elif (cursor[1] == cursor_select[1]):
                if (cursor[0] > cursor_select[0]):
                    cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
            if (cursor_tmp_1[1] == cursor_tmp_2[1]):
                inputed_str[cursor_tmp_1[1]
                            ] = inputed_str[cursor_tmp_1[1]][:cursor_tmp_1[0]] + inputed_str[cursor_tmp_1[1]][cursor_tmp_2[0]:]
                cursor = cursor_tmp_1
            else:
                inputed_str[cursor_tmp_1[1]
                            ] = inputed_str[cursor_tmp_1[1]][:cursor_tmp_1[0]]
                for _ in range(cursor_tmp_1[1], cursor_tmp_2[1]-1):
                    del inputed_str[cursor_tmp_1[1]+1]
                inputed_str[cursor_tmp_1[1]
                            ] += inputed_str.pop(cursor_tmp_1[1]+1)[cursor_tmp_2[0]:]
                cursor = cursor_tmp_1
            cursor_select_mode = False
        str_cache = inputed_str[cursor[1]]
        inputed_str[cursor[1]] = str_cache[:cursor[0]] + \
            [read_chr] + str_cache[cursor[0]:]
        cursor = (cursor[0]+1, cursor[1])
        if (len(inputed_str) < window[1]+MAX_SHOW_LN):
            window = (window[0], max(0, len(inputed_str)-MAX_SHOW_LN))
        elif (window[1] + MAX_SHOW_LN <= cursor[1]):
            window = (window[0], cursor[1] - MAX_SHOW_LN+1)
        elif (window[1] > cursor[1]):
            window = (window[0], cursor[1])
        screenw = w-9
        if (calc_ln_al() <= screenw or calc_ln() <= screenw/2):
            window = (0, window[1])
        elif (calc_ln() < window[0]):
            window = (calc_ln(), window[1])
        elif (calc_ln() > window[0]+screenw):
            window = (calc_ln()-screenw, window[1])
    while 1:
        read_chr = b""
        while 1:
            read_chr += get_char()
            try:
                read_chr.decode()
            except:
                pass
            else:
                break
        if (read_chr == b"\x08" or read_chr == b"\x7f"):
            if (cursor_select_mode):
                cursor_tmp_1 = cursor
                cursor_tmp_2 = cursor_select
                if (cursor[1] > cursor_select[1]):
                    cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
                elif (cursor[1] == cursor_select[1]):
                    if (cursor[0] > cursor_select[0]):
                        cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
                if (cursor_tmp_1[1] == cursor_tmp_2[1]):
                    inputed_str[cursor_tmp_1[1]
                                ] = inputed_str[cursor_tmp_1[1]][:cursor_tmp_1[0]] + inputed_str[cursor_tmp_1[1]][cursor_tmp_2[0]:]
                    cursor = cursor_tmp_1
                else:
                    inputed_str[cursor_tmp_1[1]
                                ] = inputed_str[cursor_tmp_1[1]][:cursor_tmp_1[0]]
                    for _ in range(cursor_tmp_1[1], cursor_tmp_2[1]-1):
                        del inputed_str[cursor_tmp_1[1]+1]
                    inputed_str[cursor_tmp_1[1]
                                ] += inputed_str.pop(cursor_tmp_1[1]+1)[cursor_tmp_2[0]:]
                    cursor = cursor_tmp_1
                cursor_select_mode = False
            else:
                if (cursor[0] > 0):
                    inputed_str[cursor[1]] = inputed_str[cursor[1]
                                                         ][:cursor[0]-1] + inputed_str[cursor[1]][cursor[0]:]
                    cursor = (cursor[0]-1, cursor[1])
                elif (cursor[1] > 0):
                    tmp = len(inputed_str[cursor[1]-1])
                    inputed_str[cursor[1]-1] += (inputed_str[cursor[1]])
                    del inputed_str[cursor[1]]
                    cursor = (tmp, cursor[1]-1)
        elif (read_chr == b"\x0d"):
            if (cursor_select_mode):
                cursor_tmp_1 = cursor
                cursor_tmp_2 = cursor_select
                if (cursor[1] > cursor_select[1]):
                    cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
                elif (cursor[1] == cursor_select[1]):
                    if (cursor[0] > cursor_select[0]):
                        cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
                if (cursor_tmp_1[1] == cursor_tmp_2[1]):
                    inputed_str[cursor_tmp_1[1]
                                ] = inputed_str[cursor_tmp_1[1]][:cursor_tmp_1[0]] + inputed_str[cursor_tmp_1[1]][cursor_tmp_2[0]:]
                    cursor = cursor_tmp_1
                else:
                    inputed_str[cursor_tmp_1[1]
                                ] = inputed_str[cursor_tmp_1[1]][:cursor_tmp_1[0]]
                    for _ in range(cursor_tmp_1[1], cursor_tmp_2[1]-1):
                        del inputed_str[cursor_tmp_1[1]+1]
                    inputed_str[cursor_tmp_1[1]
                                ] += inputed_str.pop(cursor_tmp_1[1]+1)[cursor_tmp_2[0]:]
                    cursor = cursor_tmp_1
                cursor_select_mode = False
            inputed_str.insert(cursor[1]+1, inputed_str[cursor[1]][cursor[0]:])
            inputed_str[cursor[1]] = inputed_str[cursor[1]][:cursor[0]]
            cursor = (0, cursor[1]+1)
        elif (read_chr == b"\x1b"):
            read_chr = get_char()
            if (read_chr == b"["):
                read_chr = get_char()
                if (read_chr == b"A"):
                    cursor_select_mode = False
                    if (cursor[1] > 0):
                        cursor = (
                            min(cursor[0], len(inputed_str[cursor[1]-1])), cursor[1]-1)
                    else:
                        cursor = (0, cursor[1])
                elif (read_chr == b"B"):
                    cursor_select_mode = False
                    if (cursor[1] < len(inputed_str)-1):
                        cursor = (
                            min(cursor[0], len(inputed_str[cursor[1]+1])), cursor[1]+1)
                    else:
                        cursor = (len(
                            inputed_str[cursor[1]]), cursor[1])
                elif (read_chr == b"C"):
                    if (cursor_select_mode):
                        cursor_select_mode = False
                        cursor_tmp_1 = cursor
                        cursor_tmp_2 = cursor_select
                        if (cursor[1] > cursor_select[1]):
                            cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
                        elif (cursor[1] == cursor_select[1]):
                            if (cursor[0] > cursor_select[0]):
                                cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
                        cursor = cursor_tmp_2
                    else:
                        if (cursor[0] < len(inputed_str[cursor[1]])):
                            cursor = (cursor[0]+1, cursor[1])
                        elif (cursor[1] < len(inputed_str)-1):
                            cursor = (0, cursor[1]+1)
                elif (read_chr == b"D"):
                    if (cursor_select_mode):
                        cursor_select_mode = False
                        cursor_tmp_1 = cursor
                        cursor_tmp_2 = cursor_select
                        if (cursor[1] > cursor_select[1]):
                            cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
                        elif (cursor[1] == cursor_select[1]):
                            if (cursor[0] > cursor_select[0]):
                                cursor_tmp_1, cursor_tmp_2 = cursor_select, cursor
                        cursor = cursor_tmp_1
                    else:
                        if (cursor[0] > 0):
                            cursor = (cursor[0]-1, cursor[1])
                        elif (cursor[1] > 0):
                            cursor = (
                                len(inputed_str[cursor[1]-1]), cursor[1]-1)
                elif (read_chr == b"1"):
                    read_chr = get_char()
                    if (read_chr == b";"):
                        read_chr = get_char()
                        if (read_chr == b"2"):
                            if (not cursor_select_mode):
                                cursor_select = cursor
                            cursor_select_mode = True
                            read_chr = get_char()
                            if (read_chr == b"A"):
                                if (cursor[1] > 0):
                                    cursor = (
                                        min(cursor[0], len(inputed_str[cursor[1]-1])), cursor[1]-1)
                            elif (read_chr == b"B"):
                                if (cursor[1] < len(inputed_str)-1):
                                    cursor = (
                                        min(cursor[0], len(inputed_str[cursor[1]+1])), cursor[1]+1)
                            elif (read_chr == b"C"):
                                if (cursor[0] < len(inputed_str[cursor[1]])):
                                    cursor = (cursor[0]+1, cursor[1])
                            elif (read_chr == b"D"):
                                if (cursor[0] > 0):
                                    cursor = (cursor[0]-1, cursor[1])
                elif (read_chr == b"5"):
                    read_chr = get_char()
                    if (read_chr == b"~"):
                        content_offset += int((h-6)//2)
                        # content_offset += 1
                elif (read_chr == b"6"):
                    read_chr = get_char()
                    if (read_chr == b"~"):
                        content_offset = max(0, content_offset-(h-6)//2)
                        # content_offset -= 1
            elif (read_chr == b"\x1b"):
                exit_flag = True
                return
        elif (read_chr == b"\x03"):
            if (len(inputed_str[0]) != 0):
                output = get_output()
                msgs.insert(0, weakrefdict.WeakReferencableDict({
                    "from": username,
                    "pos": "right", "msg": output,
                    "actions": {},
                    "userid": userid,
                    "id": -1}))
                send_func(output, weakrefdict.create_weakref(msgs[0]))
                content_offset = 0
            inputed_str = [[]]
            cursor = (0, 0)
        elif (read_chr == b"\x18"):
            cursor_select_mode = False
            show_menu = True
            while 1:
                menustr = """> 菜单\r
[ESC*2] 退出      [b] 回到底部\r
[r]     清空内容  [f] 全屏输入\r
[Any]   关闭      [i] 群聊信息\r
[1-9]   选择信息  [a] 插入图片\r"""
                refresh()
                read_chr = get_char()
                if (read_chr == b'q'):
                    break
                elif (read_chr == b"\x1b"):
                    read_chr = get_char()
                    if (read_chr == b"["):
                        read_chr = get_char()
                        if (read_chr == b"5"):
                            read_chr = get_char()
                            if (read_chr == b"~"):
                                content_offset += int((h-6)//2)
                                # content_offset += 1
                                refresh()
                        elif (read_chr == b"6"):
                            read_chr = get_char()
                            if (read_chr == b"~"):
                                content_offset = max(
                                    0, content_offset-(h-6)//2)
                                # content_offset -= 1
                                refresh()
                    else:
                        exit_flag = True
                        return
                elif (read_chr == b'r'):
                    inputed_str = [[]]
                    cursor = (0, 0)
                    window = (0, 0)
                    break
                elif (read_chr == b'b'):
                    content_offset = 0
                    break
                elif (read_chr == b'f'):
                    fullscreen_input = not fullscreen_input
                    break
                elif (read_chr in (b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9')):
                    read_chr_int = int(read_chr)
                    if (read_chr_int not in choose_id_lst):
                        menustr = """> 菜单/选择消息\r
找不到消息！\r
\r
\r
任意键返回菜单\r"""
                        refresh()
                        get_char()
                        continue
                    if (msgs[choose_id_lst[read_chr_int]]["id"] != -1):
                        menustr = """> 菜单/选择消息\r
[ESC] 返回上级\r
[1-9] 选择对象\r
[r] 引用消息\r
[c] 复制消息\r"""
                    else:
                        menustr = """> 菜单/选择消息\r
[ESC] 返回上级\r
[1-9] 选择对象\r
[r] 重发消息\r
[c] 复制消息\r"""
                    refresh()
                    read_chr = get_char()
                    if (read_chr in (b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9')):
                        read_chr_int2 = int(read_chr)
                        msg_choose_obj = msgs[choose_id_lst[read_chr_int]]["actions"]
                        if (read_chr_int2 > len(msg_choose_obj)):
                            menustr = """> 菜单/选择消息/选择对象\r
找不到对象！\r
\r
\r
任意键返回菜单\r"""
                            refresh()
                            get_char()
                            continue
                        msg_choose_obj = msg_choose_obj[read_chr_int2-1]
                        if (msg_choose_obj["type"] == "img"):
                            obj_name = "图片"
                            menustr = f"""> 菜单/选择消息/选择对象/{obj_name}\r
[ESC] 返回上级\r
[o] 打开图片\r
\r
链接：\"{msg_choose_obj["link"]}\"\r"""
                        elif (msg_choose_obj["type"] == "link"):
                            obj_name = "链接"
                            menustr = f"""> 菜单/选择消息/选择对象/{obj_name}\r
[ESC] 返回菜单\r
[o] 打开链接\r
\r
链接：\"{msg_choose_obj["link"]}\"\r"""
                        elif (msg_choose_obj["type"] == "quote"):
                            obj_name = "引用"
                            menustr = f"""> 菜单/选择消息/选择对象/{obj_name}\r
[ESC] 返回菜单\r
[o] 跳转到内容\r
\r
ID：\"{msg_choose_obj["link"]}\"\r"""
                        refresh()
                        read_chr = get_char()
                        if (read_chr == b'o'):
                            if (msg_choose_obj["type"] == "quote"):
                                content_offset = 0
                                for i in msgs:
                                    content_offset += calc_msg_h(i)-1
                                    if (str(i["id"]) == msg_choose_obj["link"]):
                                        break
                                    else:
                                        pass
                                else:
                                    menustr = """> 菜单/选择消息/选择对象/引用/跳转\r
找不到内容或过于久远！\r
\r
\r
任意键返回菜单\r"""
                                    refresh()
                                    get_char()
                                    continue
                                content_offset -= h-6
                                content_offset = max(content_offset, 0)
                                break
                            elif (msg_choose_obj["type"] == "link"):
                                webbrowser.open(msg_choose_obj["link"])
                                break
                            elif (msg_choose_obj["type"] == "img"):
                                openimg.open_img(msg_choose_obj["link"])
                    elif (read_chr == b"r"):
                        if (msgs[choose_id_lst[read_chr_int]]["id"] != -1):
                            for i in f"@[{msgs[choose_id_lst[read_chr_int]]['msg'].lstrip(" \033[0m\n\r#>`")[:20].replace("\n", "")}]({msgs[choose_id_lst[read_chr_int]]['id']})":
                                common_input(i.encode())
                            break
                        else:
                            output = get_output()
                            msgs.insert(0, weakrefdict.WeakReferencableDict({
                                "from": msgs[choose_id_lst[read_chr_int]]["from"],
                                "pos": msgs[choose_id_lst[read_chr_int]]["pos"],
                                "msg": msgs[choose_id_lst[read_chr_int]]["msg"],
                                "actions": {},
                                "userid": userid,
                                "id": -1}))
                            send_func(
                                output, weakrefdict.create_weakref(msgs[0]))
                            content_offset = 0
                            break
                    elif (read_chr == b"\033"):
                        break
                elif (read_chr == b'a'):
                    img_input_str = ""
                    menustr = """> 菜单/插入图片\r
输入或拖入图片路径\r
\r
[\r
\r"""
                    refresh()
                    chr_cache = b""
                    while True:
                        read_chr = get_char()
                        if (read_chr == b"\x1b"):
                            break
                        elif (read_chr == b"\r"):
                            if (img_input_str == ""):
                                break
                            else:
                                img_input_str = img_input_str.lstrip(
                                    ' \'\"').rstrip(' \'\"')
                                menustr = f"""> 菜单/插入图片\r
上传中...\r
\r
\r
\r"""
                                refresh()
                                err, msg = upload_modules.upload(img_input_str)
                                if (err):
                                    menustr = f"""> 菜单/插入图片\r
上传失败\r
\r
{msg}\r
\r"""
                                    refresh()
                                    get_char()
                                else:
                                    r_msg = f"![]({msg})"
                                    for i in r_msg:
                                        common_input(i.encode())
                                break
                        elif (read_chr == b"\x7f"):
                            if (len(img_input_str) > 0):
                                img_input_str = img_input_str[:-1]
                        elif (read_chr == b"'" or read_chr == b'"'):
                            pass
                        else:
                            chr_cache += read_chr
                            try:
                                img_input_str += chr_cache.decode()
                            except UnicodeDecodeError:
                                pass
                            else:
                                chr_cache = b""
                        menustr = f"""> 菜单/插入图片\r
输入或拖入图片路径\r
\r
[{img_input_str}\r
\r"""
                        refresh()
                    break
                else:
                    break
            show_menu = False
        elif (read_chr == b"\x1c"):
            read_chr = get_char()
            if (read_chr == b"["):
                read_chr = get_char()
                if (read_chr == b"A"):
                    pass
        elif (read_chr == b"\x01"):
            cursor_select = (0, 0)
            cursor_select_mode = True
            cursor = (len(inputed_str[-1]), len(inputed_str)-1)
            window = (window[0], max(0, len(inputed_str)-MAX_SHOW_LN))
        else:
            common_input(read_chr)
        if (len(inputed_str) < window[1]+MAX_SHOW_LN):
            window = (window[0], max(0, len(inputed_str)-MAX_SHOW_LN))
        elif (window[1] + MAX_SHOW_LN <= cursor[1]):
            window = (window[0], cursor[1] - MAX_SHOW_LN+1)
        elif (window[1] > cursor[1]):
            window = (window[0], cursor[1])
        screenw = w-9
        if (calc_ln_al() <= screenw or calc_ln() <= screenw/2):
            window = (0, window[1])
        elif (calc_ln() < window[0]):
            window = (calc_ln(), window[1])
        elif (calc_ln() > window[0]+screenw):
            window = (calc_ln()-screenw, window[1])

        refresh()


def start():
    try:
        enable_base_mode()
        inp_thread = threading.Thread(target=input_th, args=())
        inp_thread.start()
        while not exit_flag:
            refresh(True)
            time.sleep(0.1)
    finally:
        pass
