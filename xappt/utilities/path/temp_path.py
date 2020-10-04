import contextlib
import errno
import os
import shutil
import stat
import tempfile

from xappt.config import log as logger


def handle_remove_readonly(func, path, exc):
    """ Sometimes `shutil.rmtree` needs some help when it cones across read-only
    files or folders. This seems to be especially True when working with git
    repositories on Windows systems. Passing this method as `rmtree`'s `onerror`
    argument will attempt to change permissions on any problem files or folders,
    and retry the failed operation. If the operation still fails the original
    exception will be re-raised.
    """
    exc_value = exc[1]
    if func in (os.rmdir, os.remove, os.unlink):
        if exc_value.errno == errno.EACCES:
            if func is not os.rmdir:
                # make sure parent folder is writable
                parent_path = os.path.dirname(path)
                os.chmod(parent_path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            func(path)
            return
    raise


@contextlib.contextmanager
def temp_path():
    """ Context manager to create a temporary path and clean it up automatically.

    >>> with temp_path() as tmp:
    ...     os.path.isdir(tmp)
    True
    >>> os.path.isdir(tmp)
    False

    """
    tmp_dir = tempfile.mkdtemp()
    logger.debug(f"created temp folder {tmp_dir}")
    try:
        yield tmp_dir
    finally:
        logger.debug(f"removing temp folder {tmp_dir}")
        shutil.rmtree(tmp_dir, onerror=handle_remove_readonly)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
