import os, sys
try:
    from urllib.parse import quote as urlQuote
except ImportError:
    from urllib import quote as urlQuote

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
    return 'http://buildbot.twistedmatrix.com/boxes-supported?branch=%s' % (urlQuote(branch),)



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
    url = url + '?' + '&'.join([k + '=' + urlQuote(v) for (k, v) in args])
    headers = {'user-agent': [USER_AGENT]}
    # We don't actually care about the result and buildbot returns a
    # relative redirect here. Until recently (#5434) twisted didn't
    # handle them, so avoid following the redirect to support released
    # versions of twisted.
    d = treq.get(url, headers, allow_redirects=False, reactor=reactor)
    d.addCallback(lambda _: getURLForBranch(branch))
    return d
