import enum
import os
import shlex
import signal
import subprocess
import warnings

from collections import namedtuple
from queue import Queue
from threading import Thread
from typing import List, Sequence, Union


CommandResult = namedtuple("CommandResult", ["result", "stdout", "stderr"])


def io_fn_default(_: str):
    """ Default subprocess io callback. """
    pass


def kill_pid(pid: int):
    try:
        os.kill(pid, signal.SIGTERM)
    except PermissionError:
        pass


class CommandRunnerState(enum.Enum):
    IDLE = 0
    RUNNING = 1
    ABORTED = 2


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
    >>> c.env_var_set("TEST", "1234")
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
        self.cwd = str(kwargs.get('cwd', os.getcwd()))
        self.env = kwargs.get('env', os.environ.copy())
        self._state = CommandRunnerState.IDLE

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
        """ This method was renamed to `env_var_set` to make it clear that
        `value` will replace anything that might already be set for `key`.
        The term "add" didn't really convey this. """
        warnings.warn("Call to deprecated function `env_var_add`. "
                      "Use `env_var_set` instead.", DeprecationWarning)
        self.env[key] = value

    def env_var_set(self, key: str, value: str):
        self.env[key] = value

    def env_var_remove(self, key: str):
        try:
            del self.env[key]
        except KeyError:
            pass

    def abort(self):
        self._state = CommandRunnerState.ABORTED

    @property
    def running(self):
        return self._state == CommandRunnerState.RUNNING

    def run(self, command: Union[bytes, str, Sequence], **kwargs) -> CommandResult:
        self._state = CommandRunnerState.RUNNING
        env = kwargs.get('env', self.env)
        shell = kwargs.get('shell', False)

        subprocess_args = {
            'cwd': str(kwargs.get('cwd') or self.cwd),
            'env': env,
            'shell': shell,
            'universal_newlines': True,
            'encoding': kwargs.get('encoding', 'utf8'),
        }

        if 'silent' in kwargs:
            warnings.warn("Using deprecated keyword argument `silent`. "
                          "Use `capture_output` instead.", DeprecationWarning)

        capture_output = kwargs.get('capture_output', True) or kwargs.get('silent', True)
        if capture_output:
            subprocess_args['stdout'] = subprocess.PIPE
            subprocess_args['stderr'] = subprocess.PIPE
        else:
            subprocess_args['stdout'] = kwargs.get('stdout')
            subprocess_args['stderr'] = kwargs.get('stderr')

        proc = subprocess.Popen(command, **subprocess_args)

        if capture_output:
            stdout_fn = kwargs.get('stdout_fn', io_fn_default)
            stderr_fn = kwargs.get('stderr_fn', io_fn_default)
            stdout = []
            stderr = []

            q_out = Queue()
            q_err = Queue()
            while proc.poll() is None:
                t_out = PipeMonitor(proc.stdout, q_out)
                t_err = PipeMonitor(proc.stderr, q_err)
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
                    if self._state == CommandRunnerState.ABORTED:
                        kill_pid(proc.pid)
                        break
                t_out.join()
                t_err.join()
            proc.stdout.close()
            proc.stderr.close()
            result = proc.returncode
            self._state = CommandRunnerState.IDLE
            return CommandResult(result, "\n".join(stdout), "\n".join(stderr))
        else:
            proc.communicate()
            self._state = CommandRunnerState.IDLE
            return CommandResult(proc.returncode, None, None)

    @staticmethod
    def command_sequence_to_string(command_seq: Sequence):
        if os.name == "nt":
            return subprocess.list2cmdline(command_seq)
        else:
            return shlex.join(command_seq)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
