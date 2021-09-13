import os
import pathlib

from typing import Union

from xappt.utilities.command_runner import CommandRunner

from xappt.config import log as logger


def is_path_repository(path: Union[str, pathlib.Path]) -> bool:
    """ Check if a path contains a git repository. """
    return CommandRunner(cwd=path).run(("git", "rev-parse")).result == 0


def commit_id(path: Union[str, pathlib.Path], *, short: bool = False) -> str:
    """ Fetch the current commit id (optionally the short version) from a git
     repository located at `path`. """
    command = ["git", "rev-parse"]
    if short:
        command.append("--short")
    command.append("HEAD")
    output = CommandRunner(cwd=path).run(command)
    if output.result == 0:
        return output.stdout.strip()
    raise RuntimeError(output.stderr)


def is_dirty(path: Union[str, pathlib.Path]) -> bool:
    cmd = CommandRunner(cwd=path)

    # are we a git repository?
    if not is_path_repository(path):
        logger.warning(f"Not a git repository: {path}")
        return True

    cmd.run(("git", "fetch", "origin"))

    # check for local change
    result = cmd.run(("git", "diff-index", "--quiet", "HEAD", "--"))
    if result.result != 0:
        logger.warning(f"Local changes detected: {path}")
        return True

    # check for remote change
    result = cmd.run(("git", "diff", "--quiet", "master", "origin/master"))
    if result.result != 0:
        logger.warning(f"Remote changes detected: {path}")
        return True

    return False
