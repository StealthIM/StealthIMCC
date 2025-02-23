import unicodedata


def calc_len(s: str):
    return sum(1 for c in s if unicodedata.east_asian_width(c) in 'FWA')


def wrap(text, max_length):
    result = []
    current_line = ""
    current_length = 0

    ansi_mode = False
    ansi_text = ""

    for i, char in enumerate(text):
        if (char == '\n'):
            result.append(current_line)
            current_line = ""
            current_length = 0
            continue
        if (char == '\033'):
            ansi_mode = True
            ansi_text = char
            continue
        elif ansi_mode:
            ansi_text += char
            if not (char.isdigit() or char in [';', '?', '!', '[', ']']):
                ansi_mode = False
                current_line += ansi_text
            continue

        char_width = 2 if unicodedata.east_asian_width(char) in 'WF' else 1

        if current_length + char_width > max_length:
            result.append(current_line)
            current_line = char
            current_length = char_width
        else:
            current_line += char
            current_length += char_width

    if current_line:
        result.append(current_line)

    return "\n".join(result)
