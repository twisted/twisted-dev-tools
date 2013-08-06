
from os.path import expanduser

from twisted.python.filepath import FilePath
from twisted.trial.unittest import TestCase

from twisted_tools.scripts.forcebuild import Options


class OptionsConfigTests(TestCase):
    """
    Tests for L{twisted_tools.scripts.forcebuild.Options} handling the
    I{--config} option.
    """
    def test_default(self):
        """
        If no value is given for I{--config}, a configuration file beneath the
        user's personal configuration directory is used.
        """
        options = Options()
        options.parseOptions([])
        self.assertEqual(
            expanduser(b"~/.config/twisted-dev-tools/force-build.cfg"),
            options["config"])


    def test_specified(self):
        """
        If a value is given for I{--config}, it is used.
        """
        options = Options()
        options.parseOptions([b"--config", b"/foo/bar"])
        self.assertEqual(b"/foo/bar", options["config"])


    def test_readConfiguration(self):
        """
        The ini-style configuration in the configuration file is read and
        referenced by the C{config} attribute of the L{Options} instance.
        """
        options = Options()
        config = FilePath(self.mktemp())
        config.setContent(b"[hello]\nworld=stuff\n")
        options.parseOptions([b"--config", config.path])
        self.assertEqual(b"stuff", options.config.get(b"hello", b"world"))
