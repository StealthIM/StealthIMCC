import sys
import platform
os_name = platform.system()
if os_name == 'Windows':
    import msvcrt
else:
    import termios
    import tty

enabled_base_mode = False


def enable_base_mode():
    global old_settings, fd, enabled_base_mode
    if (enabled_base_mode):
        return
    enabled_base_mode = True
    if os_name != 'Windows':
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())


if os_name == 'Windows':
    def get_char():
        return msvcrt.getch()
else:
    def get_char():
        return sys.stdin.buffer.read(1)


def disable_base_mode():
    global old_settings, enabled_base_mode
    if (not enabled_base_mode):
        return
    enabled_base_mode = False
    sys.stdout.write("\033[2J\033[1;1f\033[0m\033[?25h")
    if os_name != 'Windows':
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
