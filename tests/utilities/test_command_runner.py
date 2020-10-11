import os
import re
import unittest

from xappt.utilities import CommandRunner
from xappt.utilities import temp_path


class TestCommandRunner(unittest.TestCase):
    def test_basic_command(self):
        with temp_path() as tmp:
            cmd = CommandRunner(cwd=tmp)
            if os.name == "nt":
                cmd.run(("mkdir", "test"), silent=False, shell=True)
            else:
                cmd.run(("mkdir", "test"), silent=False)
            self.assertTrue(os.path.isdir(os.path.join(tmp, "test")))

    def test_basic_command_silent(self):
        with temp_path() as tmp:
            cmd = CommandRunner(cwd=tmp)
            if os.name == "nt":
                cmd.run(("mkdir", "test"), silent=True, shell=True)
            else:
                cmd.run(("mkdir", "test"), silent=True)
            self.assertTrue(os.path.isdir(os.path.join(tmp, "test")))

    def test_basic_command_output(self):
        with temp_path() as tmp:
            cmd = CommandRunner(cwd=tmp)
            if os.name == "nt":
                cmd.run(("mkdir", "test"), silent=True, shell=True)
                self.assertTrue(os.path.isdir(os.path.join(tmp, "test")))
                output = cmd.run("dir", silent=True, shell=True)
                match_pattern = r"^.*?<DIR>\s+test$"
            else:
                cmd.run(("mkdir", "test"), silent=True)
                self.assertTrue(os.path.isdir(os.path.join(tmp, "test")))
                output = cmd.run(("ls", "-l"), silent=True)
                match_pattern = r"^[d].*\s(?:test)$"
            matched = False
            for line in output.stdout.split("\n"):
                line = line.strip()
                if re.match(match_pattern, line):
                    matched = True
            if not matched:
                self.fail(f"No matches in '{output.stdout}'")

    def test_environment_add(self):
        cmd = CommandRunner(env={})
        cmd.env_var_add("TEST", "12345")
        self.assertIn("TEST", cmd.env)
        self.assertEqual(cmd.env["TEST"], "12345")
        cmd.env_var_add("TEST", "abcde")
        self.assertEqual(cmd.env["TEST"], "abcde")

    def test_environment_rem(self):
        cmd = CommandRunner(env={})
        cmd.env_var_add("TEST", "12345")
        self.assertIn("TEST", cmd.env)
        cmd.env_var_remove("TEST")
        self.assertNotIn("TEST", cmd.env)
        try:
            cmd.env_var_remove("INVALID")
        except KeyError:
            self.fail("A KeyError should not have been raised.")

    def test_environment_path(self):
        cmd = CommandRunner(env={})
        cmd.env_var_add("TESTPATH", "3")
        cmd.env_path_append("TESTPATH", "4")
        cmd.env_path_prepend("TESTPATH", "2")
        cmd.env_path_append("TESTPATH", "5")
        cmd.env_path_prepend("TESTPATH", "1")
        self.assertEqual(cmd.env["TESTPATH"], os.pathsep.join("12345"))
