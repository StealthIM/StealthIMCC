import pygments
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
import re


def process_markdown(markdown: str, screen_w: int):
    md_lst = (markdown+"\n").split("\n")
    result = ""
    code_str = ""
    code_mode = 0
    code_leftsp = 0
    link_lst = []
    for line in md_lst:
        endline_str = ""
        l = line.strip(" ")
        b_level = len(line)-len(line.lstrip(" "))
        # s_level = b_level//2
        if (code_mode == 1 and not l.startswith("```")):
            code_str += line[min(code_leftsp, len(line)):]+"\n"
            continue
        if (result == "" or result[-1] == "\n"):
            result += " "*b_level
        l = re.sub(r'\s+', ' ', l)
        if (l.startswith("#")):
            ln_flag = True
            result += "\033[90m"
            for i in l:
                if (ln_flag):
                    if (i == "#"):
                        result += "#"
                    else:
                        result += "\033[0m \033[34m\033[1m"
                        ln_flag = False
                        if (i != " "):
                            result += i
                else:
                    result += i
            result += "\033[0m\n"
        elif (l == ""):
            result = result.rstrip("\n")
            result += "\033[0m\n\n"
        elif (l.startswith("```")):
            if (code_mode == 0):
                result = result.rstrip("\n")
                result += "\033[0m\n"
                code_mode = 1
                code_lang = l[3:].strip(" ")
                code_leftsp = b_level
            else:
                code_mode = 0
                try:
                    code_str = highlight(code_str,
                                         get_lexer_by_name(code_lang), TerminalFormatter())
                except pygments.util.ClassNotFound:
                    pass
                result = result.rstrip(" ")
                for i in code_str.split("\n"):
                    result += "\033[0m"+" "*(code_leftsp)+i+"\n"
                code_str = ""
        elif (l.startswith("---")):
            result += "\033[90m"+"-"*screen_w+"\033[0m"
            continue
        else:
            if (l.startswith(">")):
                result += "\033[32m\033[2m"+"||\033[0m"
                l = l.lstrip(">")
            elif (l.startswith("* ")):
                result += "\033[34m\033[2m"+"* \033[0m"
                l = l.lstrip("* ")
                endline_str = "\n"
            elif (l.startswith("- ")):
                result += "\033[34m\033[2m"+"* \033[0m"
                l = l.lstrip("- ")
                endline_str = "\n"
            elif (l.startswith("+ ")):
                result += "\033[34m\033[2m"+"* \033[0m"
                l = l.lstrip("+ ")
                endline_str = "\n"
            elif (bool(re.match(r'^\d\.', l))):
                num_t = l.split(".")[0]
                result += "\033[34m\033[2m"+" " * \
                    (2-len(num_t))+num_t+". \033[0m"
                l = l[3:].rstrip(" ")
                endline_str = "\n"
            if (l.startswith("|") and l.endswith("|")):
                endline_str = "\n"
            star_cnt = 0
            bold_mode = 0
            italic_mode = 0
            ignore_mode = 0
            inlinecode_mode = 0
            img_mode = 0
            link_str = ""
            link_mode = 0
            quote_mode = 0
            quote_str = ""
            for i in l:
                if (i == "\\"):
                    ignore_mode = 1
                    continue
                elif (ignore_mode == 1):
                    result += i
                    ignore_mode = 0
                else:
                    ignore_mode = 0
                if (i == "`"):
                    inlinecode_mode = 1-inlinecode_mode
                    if (inlinecode_mode):
                        result += "\033[33m\033[2m[\033[0m\033[33m\033[1m"
                    else:
                        result += "\033[0m\033[33m\033[2m]\033[0m"
                        if (bold_mode):
                            result += "\033[1m"
                        else:
                            result += "\033[22m"
                        if (italic_mode):
                            result += "\033[3m"
                        else:
                            result += "\033[23m"
                    continue
                if (inlinecode_mode):
                    result += i
                    continue
                if (img_mode > 0):
                    if (img_mode == 1 and i != "["):
                        img_mode = 0
                        result += "!"
                        continue
                    elif (img_mode == 1 and i == "["):
                        img_mode = 2
                        continue
                    elif (img_mode == 2 and i == "("):
                        img_mode = 3
                        link_str = ""
                        continue
                    elif (img_mode == 3 and i == ")"):
                        img_mode = 0
                        result = result.rstrip("\n")
                        result += '\n\033[47m          \033[0m\n'\
                            f'\033[30;47m  IMG[{len(link_lst)+1}]  \033[0m\n'\
                            '\033[47m          \033[0m\n'
                        link_lst.append({
                            "type": "img", "link": link_str})
                        continue
                    elif (img_mode == 2):
                        continue
                    elif (img_mode == 3):
                        link_str += i
                        continue
                elif (i == "!"):
                    img_mode = 1
                    continue
                if (i == "@"):
                    quote_mode = 1
                    quote_str = ""
                    continue
                if (quote_mode > 0):
                    if (quote_mode == 1 and i == "["):
                        quote_mode = 2
                        result += "\033[34m\033[2m[\033[0m\033[34m^ \033[4m"
                        continue
                    elif (quote_mode == 1):
                        result += "@"
                        result += i
                        quote_mode = 0
                        continue
                    elif (quote_mode == 2 and i == "]"):
                        quote_mode = 3
                        result += f"\033[0m\033[34m\033[2m]\033[0m\033[34m[{len(link_lst)+1}]\033[0m"
                        if (bold_mode):
                            result += "\033[1m"
                        else:
                            result += "\033[22m"
                        if (italic_mode):
                            result += "\033[3m"
                        else:
                            result += "\033[23m"
                        continue
                    elif (quote_mode == 2):
                        result += i
                        continue
                    elif (quote_mode == 3 and i == "("):
                        quote_mode = 4
                        quote_str = ""
                        continue
                    elif (quote_mode == 4 and i == ")"):
                        quote_mode = 0
                        link_lst.append({
                            "type": "quote", "link": quote_str
                        })
                        continue
                    elif (quote_mode == 4):
                        quote_str += i
                        continue
                if (i == "["):
                    link_mode = 1
                    link_str = ""
                    result += "\033[34m\033[4m"
                    continue
                if (link_mode > 0):
                    if (link_mode == 1 and i == "]"):
                        link_mode = 2
                        result += f"[{len(link_lst)+1}]\033[0m"
                        if (bold_mode):
                            result += "\033[1m"
                        else:
                            result += "\033[22m"
                        if (italic_mode):
                            result += "\033[3m"
                        else:
                            result += "\033[23m"
                        continue
                    elif (link_mode == 2 and i == "("):
                        link_mode = 3
                        link_str = ""
                        continue
                    elif (link_mode == 3 and i == ")"):
                        link_mode = 0
                        link_lst.append({
                            "type": "link", "link": link_str
                        })
                        continue
                    elif (link_mode == 1):
                        result += i
                        continue
                    elif (link_mode == 3):
                        link_str += i
                        continue

                if (i == "*"):
                    star_cnt += 1
                    continue
                elif (i == "_"):
                    star_cnt += 1
                    continue
                else:
                    if (star_cnt == 3):
                        bold_mode = 1-bold_mode
                        italic_mode = 1-italic_mode
                        star_cnt = 0
                        if (bold_mode):
                            result += "\033[1m"
                        else:
                            result += "\033[22m"
                        if (italic_mode):
                            result += "\033[3m"
                        else:
                            result += "\033[23m"
                    elif (star_cnt == 2):
                        bold_mode = 1-bold_mode
                        star_cnt = 0
                        if (bold_mode):
                            result += "\033[1m"
                        else:
                            result += "\033[22m"
                        if (italic_mode):
                            result += "\033[3m"
                        else:
                            result += "\033[23m"
                    elif (star_cnt == 1):
                        italic_mode = 1-italic_mode
                        star_cnt = 0
                        if (bold_mode):
                            result += "\033[1m"
                        else:
                            result += "\033[22m"
                        if (italic_mode):
                            result += "\033[3m"
                        else:
                            result += "\033[23m"

                result += i
        result += endline_str
    result = result.rstrip().replace("\033[0m\033[0m", "\033[0m")
    return result, link_lst
