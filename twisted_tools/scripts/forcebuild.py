"""
Force the Twisted buildmaster to run a builds on all supported builders for
a particular branch.
"""

import os, pwd

from twisted.python import usage
from twisted.internet.defer import inlineCallbacks

from twisted_tools import buildbot, git

class Options(usage.Options):
    synopsis = "force-build [options]"

    optParameters = [['branch', 'b', None, 'Branch to build'],
                     ['tests', 't', None, 'Tests to run'],
                     ['comments', None, None, 'Build comments'],
                     ]



@inlineCallbacks
def main(reactor, *argv):
    config = Options()
    config.parseOptions(argv[1:])

    if config['branch'] is None:
        try:
            git.ensureGitRepository(reactor=reactor)
            config['branch'] = yield git.getCurrentSVNBranch(reactor=reactor)
        except git.NotAGitRepository:
            raise SystemExit("Must specify a branch to build or be in a git repository.")
        except git.NotASVNRevision:
            raise SystemExit("Current commit hasn't been pushed to svn.")


    reason = '%s: %s' % (pwd.getpwuid(os.getuid())[0], config['comments'])

    print 'Forcing...'
    url = yield buildbot.forceBuild(config['branch'], reason, config['tests'], reactor=reactor)
    print 'Forced.'
    print 'See %s for results' % (url,)
