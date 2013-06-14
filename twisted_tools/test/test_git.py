from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath
from twisted.internet.utils import getProcessValue

from twisted_tools import git



class EnsureGitRepository(TestCase):
    """
    Tests for L{git.ensureGitRepository}.
    """

    def test_raiseNotAGitRepository(self):
        """
        When called from a directory that isn't part of a git repository,
        L{git.ensureGitRepository} raises L{git.NotAGitRepository}.

        Since trial is usually run in a subdirectory of the current
        repository, we need to convince C{git rev-parse} that we aren't
        in a repository. It turns out that if there is a file L{.git}
        in the directory that isn't of the format C{gitdir: path/to/git/dir}
        it considers that directory not part of a git repository.
        """
        basedir = FilePath(self.mktemp())
        basedir.createDirectory()
        basedir.child('.git').setContent('blah-blah-blah')
        return self.assertFailure(git.ensureGitRepository(basedir.path), git.NotAGitRepository)


    def test_isGitRepository(self):
        """
        When called from a git repository, L{git.ensureGitRepository} returns
        a deferred that doesn't errback.
        """
        basedir = FilePath(self.mktemp())
        basedir.createDirectory()
        basedir.child('.git').setContent('blah-blah-blah')
        gitRepo = basedir.child('git-repo')

        # Create a git repository
        d = getProcessValue('git', ('init', gitRepo.path))

        d.addCallback(lambda _: git.ensureGitRepository(gitRepo.path))
        return d



class SVNLogTests(TestCase):
    """
    Tests for L{git._getSVNPathFromGitLog}.
    """

    def test_succesfulParse(self):
        """
        When passed a commit message with a proper C{git-svn-id} line,
        L{git._getSVNPathFromGitLog} returns the branch and revision of
        from the tag.
        """
        message = """\
Merge tcpclient-endpoint-bindaddress-6465: Parse the bindAddress keyword in TCP related client endpoint strings

Author: rwall
Reviewer: therve,exarkun
Fixes: #6465
Refs: #6562

Parse the bindAddress keyword argument in TCP related client endpoint
strings. The value is treated as a host string and is coerced to a
(host, port) tuple. The port is set to 0 to bind the client to any
ephemeral port.

git-svn-id: svn://svn.twistedmatrix.com/svn/Twisted/trunk@38706 bbbe8e31-12d6-0310-92fd-ac37d47ddeeb
"""
        result = git._getSVNPathFromGitLog(message)
        self.assertEqual(result, ('/trunk', '38706'))


    def test_missingTag(self):
        """
        When L{git._getSVNPathFromGitLog} is given a message whose last line
        contains three words but without the C{git-svn-id} tag, it raises
        L{git.NotASVNRevision}
        """
        message = "three word line"
        self.assertRaises(git.NotASVNRevision, git._getSVNPathFromGitLog, message)


    def test_notThreeWords(self):
        """
        When L{git._getSVNPathFromGitLog} is given a message whose last line
        doesn't contain three words, it raises L{git.NotASVNRevision}
        """
        message = """\
Parse the bindAddress keyword argument in TCP related client endpoint
strings. The value is treated as a host string and is coerced to a
(host, port) tuple. The port is set to 0 to bind the client to any
ephemeral port.
"""
        self.assertRaises(git.NotASVNRevision, git._getSVNPathFromGitLog, message)


    def test_wrongSVNPath(self):
        """
        When L{git._getSVNPathFromGitLog} is given a message whose last line
        contains a proper C{git-svn-id} line, but which isn't the canonical
        twisted repository, it raises L{git.NotASVNRevision}
        """
        message = """\
git-svn-id: svn+ssh://svn.twistedmatrix.com/svn/Twisted/trunk@38706 bbbe8e31-12d6-0310-92fd-ac37d47ddeeb
"""
        self.assertRaises(git.NotASVNRevision, git._getSVNPathFromGitLog, message)
