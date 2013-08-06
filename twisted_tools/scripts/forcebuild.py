"""
Force the Twisted buildmaster to run a builds on all supported builders for
a particular branch.
"""

import os.path, pwd, urllib

from ConfigParser import ConfigParser

from twisted.python.filepath import FilePath
from twisted.python import usage
from twisted.internet.defer import inlineCallbacks

from twisted_tools import buildbot, git

class Options(usage.Options):
    synopsis = "force-build [options]"

    optParameters = [['branch', 'b', None, 'Branch to build'],
                     ['tests', 't', None, 'Tests to run'],
                     ['comments', None, None, 'Build comments'],
                     ['config', None,
                      os.path.expanduser(b'~/.config/twisted-dev-tools/force-build.cfg'),
                      'Path to configuration file', os.path.expanduser],
                     ]


    def postOptions(self):
        path = FilePath(self['config'])
        print path
        if not path.exists():
            self.config = None
        else:
            config = ConfigParser()
            with path.open() as configFile:
                config.readfp(configFile)
            self.config = config


@inlineCallbacks
def main(reactor, *argv):
    config = Options()
    config.parseOptions(argv[1:])

    try:
        origin = yield git.ensureGitRepository(reactor=reactor)
        if config['branch'] is None:
            mirror = int(config.config.get(origin, b"svn_mirror", b"1"))
            if mirror:
                config['branch'] = yield git.getCurrentSVNBranch(reactor=reactor)
            else:
                config['branch'] = yield git.getCurrentBranch(reactor=reactor)
    except git.NotAGitRepository:
        raise SystemExit("Must specify a branch to build or be in a git repository.")
    except git.NotASVNRevision:
        raise SystemExit("Current commit hasn't been pushed to svn.")

    url = config.config.get(origin, b"url", b"http://buildbot.twistedmatrix.com/")
    scheduler = config.config.get(origin, b"scheduler", b"force-supported")
    username = config.config.get(origin, b"username", b"twisted")
    password = config.config.get(origin, b"password", b"matrix")
    results = config.config.get(origin, b"results", b"")
    prefix = config.config.get(origin, b"branch-prefix", b"/branches/")
    branchKey = config.config.get(origin, b"branch-key", b"branch")

    branch = config['branch']
    if not branch.startswith(prefix):
        branch = prefix + branch

    reason = '%s: %s' % (pwd.getpwuid(os.getuid())[0], config['comments'])

    tests = config['tests']

    args = [
        ('username', username),
        ('passwd', password),
        ('forcescheduler', scheduler),
        ('revision', ''),
        ('submit', 'Force Build'),
        (branchKey, branch),
        ('reason', reason)]

    if tests is not None:
        args += [('test-case-name', tests)]

    print 'Forcing...', url, args
    yield buildbot.forceBuild(url, args, reactor=reactor)
    print 'Forced.'
    print 'See', results % (urllib.quote(branch),), 'for results.'
