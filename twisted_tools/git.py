import os
from twisted.internet.utils import getProcessOutput, getProcessValue

SVN_REPO = 'svn://svn.twistedmatrix.com/svn/Twisted/'



class NotAGitRepository(Exception):
    """
    The specfied directory isn't part of a git repository.
    """


class NotASVNRevision(Exception):
    """
    The specified commit isn't mirrored from svn.
    """



def ensureGitRepository(path=None, reactor=None):
    if path is None:
        path = os.getcwd()
    d = getProcessValue('git', ('rev-parse', '--git-dir'), path=path, reactor=reactor)
    def convertExitCode(res):
        if res != 0:
            raise NotAGitRepository

    d.addCallback(convertExitCode)
    return d


def _getSVNPathFromGitLog(output):
    svnInfoLine = output.splitlines()[-1]
    try:
        tag, path, uuid = svnInfoLine.split(' ')
    except ValueError:
        raise NotASVNRevision
    if tag != 'git-svn-id:':
        raise NotASVNRevision
    if not path.startswith(SVN_REPO):
        raise NotASVNRevision
    branch, revision = path[len(SVN_REPO):].split('@')
    return '/' + branch, revision


def getCurrentSVNBranch(path=None, reactor=None):
    """
    Get the svn branch corresponding to the current commit.
    """
    if path is None:
        path = os.getcwd()
    d = getProcessOutput('git', ('log', '-n1', '--pretty=format:%B'), path=path, reactor=reactor)
    d.addCallback(_getSVNPathFromGitLog)
    d.addCallback(lambda res: res[0])
    return d
