import os
from twisted.internet.utils import getProcessValue



class NotAGitRepository(Exception):
    """
    The specfied directory isn't part of a git repository.
    """



def ensureGitRepository(path=None, reactor=None):
    if path is None:
        path = os.getcwd()
    d = getProcessValue('git', ('rev-parse', '--git-dir'), path=path, reactor=reactor)
    def convertExitCode(res):
        if res != 0:
            raise NotAGitRepository()

    d.addCallback(convertExitCode)
    return d
