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
