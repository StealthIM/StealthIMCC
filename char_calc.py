import unicodedata


def char_width_b(char):
    char = char.decode()  # 将字节编码的字符解码为字符串
    if (char in ('\n', '\r', '\t')):  # 如果字符是换行符、回车符或制表符，则宽度为0
        return 0
    east_asian_width = unicodedata.east_asian_width(char)  # 获取字符的宽度
    if east_asian_width in ('F', 'W'):  # 全角或宽字符，则宽度为2
        return 2
    else:
        return 1


def char_width(char):
    east_asian_width = unicodedata.east_asian_width(char)
    if (char in ('\n', '\r', '\t')):
        return 0
    if east_asian_width in ('F', 'W'):
        return 2
    else:
        return 1
