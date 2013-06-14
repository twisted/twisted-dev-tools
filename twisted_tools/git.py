import os
from twisted.internet.defer import Deferred
from twisted.internet.endpoints import connectProtocol, ProcessEndpoint
from twisted.internet.error import ConnectionDone
from twisted.internet.utils import getProcessOutput, getProcessValue
from twisted.test.proto_helpers import AccumulatingProtocol

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



def applyPatch(patch, patchLevel="0", reactor=None):
    """
    Apply a patch to the current git repository.

    @param patch: Patch to apply
    @type patch: L{str}

    @param patchLevel: Number of directries to strip from paths in patch
    """
    proto = AccumulatingProtocol()
    done = Deferred()
    proto.closedDeferred = done
    def feedPatch(proto):
        proto.transport.write(patch)
        proto.transport.closeStdin()
    connectProtocol(
            ProcessEndpoint(reactor, "git", ("git", "apply", "--index",
                                             "-p", patchLevel)),
            proto).addCallback(feedPatch)
    def eb(_):
        # Note, we can't print why git apply failed due to https://tm.tl/#6576
        proto.closedReason.trap(ConnectionDone)
    done.addCallback(eb)
    return done


def commit(summary, body, reactor=None):
    """
    Commit the current state of the index.

    @param summary: First line of commit message.
    @param body: Body of commit message
    @return: L{deferred<twisted.internet.defer.Deferred>} that fires with the output of git-commit.
    """
    return getProcessOutput("git", ("commit",
        '--no-edit',
        '-m', summary,
        '-m', body),
        env = os.environ)
