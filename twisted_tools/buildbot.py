import os, sys
import urllib
import treq
import twisted

USER_AGENT = (
    "force-builds (%(name)s; %(platform)s) Twisted/%(twisted)s "
    "Python/%(python)s" % dict(
        name=os.name, platform=sys.platform,
        twisted=twisted.__version__, python=hex(sys.hexversion)))



def getURLForBranch(branch):
    """
    Get URL for build results corresponding to a branch.
    """
    return 'http://buildbot.twistedmatrix.com/boxes-supported?branch=%s' % (urllib.quote(branch),)



def forceBuild(branch, reason, tests=None, reactor=None):
    """
    Force a build of a given branch.

    @return: URL where build results can be found.
    """
    if not branch.startswith('/branches/'):
        branch = '/branches/' + branch

    args = [
        ('username', 'twisted'),
        ('passwd', 'matrix'),
        ('forcescheduler', 'force-supported'),
        ('revision', ''),
        ('submit', 'Force Build'),
        ('branch', branch),
        ('reason', reason)]

    if tests is not None:
        args += [('test-case-name', tests)]

    url = "http://buildbot.twistedmatrix.com/builders/_all/forceall"
    url = url + '?' + '&'.join([k + '=' + urllib.quote(v) for (k, v) in args])
    headers = {'user-agent': [USER_AGENT]}
    d = treq.get(url, headers, reactor=reactor)
    d.addCallback(lambda _: getURLForBranch(branch))
    return d
