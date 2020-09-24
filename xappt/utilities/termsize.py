import os
import subprocess

from typing import Optional, Tuple


def get_terminal_size() -> Tuple[int, int]:
    import platform
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        tuple_xy = 80, 25  # default value
    return tuple_xy


# noinspection PyBroadException,SpellCheckingInspection
def _get_terminal_size_windows() -> Optional[Tuple[int, int]]:
    import struct
    try:
        from ctypes import windll, create_string_buffer
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy) = \
                struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except BaseException:
        pass


# noinspection PyBroadException,SpellCheckingInspection
def _get_terminal_size_tput() -> Optional[Tuple[int, int]]:
    import shlex
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return cols, rows
    except BaseException:
        pass


# noinspection PyBroadException
def _get_terminal_size_linux() -> Optional[Tuple[int, int]]:
    import struct

    # noinspection PyShadowingNames,PyBroadException,SpellCheckingInspection
    def ioctl_gwinsz(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, b'1234'))
            return cr
        except BaseException:
            pass

    cr = ioctl_gwinsz(0) or ioctl_gwinsz(1) or ioctl_gwinsz(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_gwinsz(fd)
            os.close(fd)
        except BaseException:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except BaseException:
            return None
    return int(cr[1]), int(cr[0])
