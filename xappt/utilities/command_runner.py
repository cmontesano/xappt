import os
import subprocess

from collections import namedtuple
from queue import Queue
from threading import Thread
from typing import List, Sequence, Union

from xappt.config import log as logger


CommandResult = namedtuple("CommandResult", ["result", "stdout", "stderr"])


class PipeMonitor(Thread):
    def __init__(self, fd, queue):
        super().__init__()
        self._fd = fd
        self._queue = queue

    def run(self):
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)

    def eof(self):
        return not self.is_alive() and self._queue.empty()


class CommandRunner(object):
    """ A wrapper around `subprocess.Popen` with basic environment manipulation.
    The results of a subprocess operation will be returned as a `CommandResult`
    object, which includes the return code, and stdout/stderr. Note that
    stdout/stderr will only be populated if the command was run silently.

    >>> c = CommandRunner(env={})
    >>> c.env_var_add("TEST", "1234")
    >>> c.env['TEST']
    '1234'
    >>> if os.name == "nt":
    ...     command = "set"
    ... elif os.name == "posix":
    ...     command = "printenv"
    >>> result = c.run(command, silent=True)
    >>> result.result == 0
    True
    >>> result.stdout.count("TEST=1234")
    1

    """
    def __init__(self, **kwargs):
        self.cwd = kwargs.get('cwd', os.getcwd())
        self.env = kwargs.get('env', os.environ.copy())

    def _split_path_var(self, key: str) -> List[str]:
        values = self.env.get(key, "").split(os.pathsep)
        return [v for v in values if len(v.strip())]

    def env_path_append(self, key: str, value: str):
        values = self._split_path_var(key)
        values.append(value)
        self.env[key] = os.pathsep.join(values)

    def env_path_prepend(self, key: str, value: str):
        values = self._split_path_var(key)
        values.insert(0, value)
        self.env[key] = os.pathsep.join(values)

    def env_var_add(self, key: str, value: str):
        self.env[key] = value

    def env_var_remove(self, key: str):
        try:
            del self.env[key]
        except KeyError:
            pass

    def run(self, command: Union[bytes, str, Sequence], **kwargs) -> CommandResult:
        env = kwargs.get('env', self.env)

        subprocess_args = {
            'cwd': kwargs.get('cwd') or self.cwd,
            'env': env,
            'shell': False,
            'universal_newlines': True,
            'encoding': 'utf8',
        }

        silent = kwargs.get('silent', True)
        if silent:
            subprocess_args['stdout'] = subprocess.PIPE
            subprocess_args['stderr'] = subprocess.PIPE

        logger.debug("Running command %s", str(command))
        logger.debug("Command environment %s", str(env))
        logger.debug("Command working directory %s", subprocess_args['cwd'])
        proc = subprocess.Popen(command, **subprocess_args)

        if silent:
            def io_fn_default(_: str):
                pass

            stdout_fn = kwargs.get('stdout_fn', io_fn_default)
            stderr_fn = kwargs.get('stderr_fn', io_fn_default)
            stdout = []
            stderr = []
            stdout_fn(" ".join(command))

            q_out = Queue()
            q_err = Queue()
            t_out = PipeMonitor(proc.stdout, q_out)
            t_err = PipeMonitor(proc.stderr, q_err)
            while proc.poll() is None:
                t_out.start()
                t_err.start()
                while not t_out.eof() or not t_err.eof():
                    while not q_out.empty():
                        line = q_out.get().rstrip()
                        stdout.append(line)
                        stdout_fn(line)
                    while not q_err.empty():
                        line = q_err.get().rstrip()
                        stderr.append(line)
                        stderr_fn(line)
                t_out.join()
                t_err.join()
            proc.stdout.close()
            proc.stderr.close()
            result = proc.returncode
            return CommandResult(result, "\n".join(stdout), "\n".join(stderr))
        else:
            proc.communicate()
            return CommandResult(proc.returncode, None, None)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
