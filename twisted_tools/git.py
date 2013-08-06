import os

from twisted.internet.utils import getProcessOutputAndValue

SVN_REPO = 'svn://svn.twistedmatrix.com/svn/Twisted/'



class NotAGitRepository(Exception):
    """
    The specfied directory isn't part of a git repository.
    """


class NotASVNRevision(Exception):
    """
    The specified commit isn't mirrored from svn.
    """



def _git(path, reactor, args):
    if path is None:
        path = os.getcwd()
    return getProcessOutputAndValue('git', args, path=path, reactor=reactor)



def ensureGitRepository(path=None, reactor=None):
    d = _git(path, reactor, ('rev-parse', '--git-dir'))
    def convertExitCode((out, err, code)):
        if code != 0:
            raise NotAGitRepository()
        d = _git(path, reactor, (b"remote", b"-v"))
        d.addCallback(_parseRemotes)
        return d

    d.addCallback(convertExitCode)
    return d



def _parseRemotes((output, err, code)):
    if output.strip():
        return output.splitlines()[0].split()[1]



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
    d = _git(path, reactor, ('log', '-n1', '--pretty=format:%B'))
    d.addCallback(_getSVNPathFromGitLog)
    d.addCallback(lambda res: res[0])
    return d



def getCurrentBranch(path=None, reactor=None):
    d = _git(path, reactor, ('rev-parse', '--abbrev-ref', 'HEAD'))
    d.addCallback(lambda (out, err, code): out.strip())
    return d

