"""
Force the Twisted buildmaster to run a builds on all supported builders for
a particular branch.
"""

import os, sys, pwd

from twisted.python import log
from twisted_tools import buildbot

def main(reactor, *args):
    if len(args) == 2:
        branch, comments = args
        tests = None
    elif len(args) == 3:
        branch, comments, tests = args
    else:
        raise SystemExit("Usage: %s <branch> <comments> [test-case-name]" % (sys.argv[0],))

    reason = '%s: %s' % (pwd.getpwuid(os.getuid())[0], comments)

    print 'Forcing...'
    d = buildbot.forceBuild(branch, reason, tests, reactor=reactor)

    def forced(url):
        print 'Forced.'
        print 'See %s for results' % (url,)

    d.addCallback(forced)
    d.addErrback(log.err, "Build force failure")
    return d