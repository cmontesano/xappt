import errno
import os
import shutil


def _find_python_nt(version):
    import winreg

    opened_key = None
    for key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        try:
            opened_key = winreg.OpenKey(key, r"SOFTWARE\Python\PythonCore\{0}".format(version))
        except WindowsError as e:
            if e.errno != errno.ENOENT:
                raise

    if opened_key is None:
        return None

    py_path = winreg.QueryValue(opened_key, "InstallPath")
    py_exe = shutil.which("python", path=py_path)
    if py_exe is not None and os.path.isfile(py_exe):
        return py_exe

    return None


def _find_python_posix(version):
    return shutil.which("python{0}".format(version))


def find_python(major, minor):
    """ Helper to find the executable for a specific python version.

    >>> # find Python 3.6 or higher
    >>> py_bin = find_python(3, 9) or find_python(3, 8) or find_python(3, 7) or find_python(3, 6)
    >>> assert py_bin is not None

    """
    version = "{major}.{minor}".format(**locals())
    if os.name == "nt":
        return _find_python_nt(version)
    elif os.name == "posix":
        return _find_python_posix(version)
    raise NotImplementedError
