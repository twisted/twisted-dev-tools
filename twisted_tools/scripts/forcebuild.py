"""
Force the Twisted buildmaster to run a builds on all supported builders for
a particular branch.
"""

import os, pwd

from twisted.python import log
from twisted.python import usage
from twisted_tools import buildbot

class Options(usage.Options):
    synopsis = "force-build [options]"

    optParameters = [['branch', 'b', None, 'Branch to build'],
                     ['tests', 't', None, 'Tests to run'],
                     ['comments', None, None, 'Build comments'],
                     ]




def main(reactor, *argv):
    config = Options()
    config.parseOptions(argv[1:])

    if config['branch'] is None:
        raise SystemExit("Must specify a branch to build.")

    reason = '%s: %s' % (pwd.getpwuid(os.getuid())[0], config['comments'])

    print 'Forcing...'
    d = buildbot.forceBuild(config['branch'], reason, config['tests'], reactor=reactor)

    def forced(url):
        print 'Forced.'
        print 'See %s for results' % (url,)

    d.addCallback(forced)
    d.addErrback(log.err, "Build force failure")
    return d
