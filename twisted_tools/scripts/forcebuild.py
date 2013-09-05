"""
Force the Twisted buildmaster to run a builds on all supported builders for
a particular branch.
"""

import os.path, pwd, urllib

from ConfigParser import NoSectionError, NoOptionError, ConfigParser

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
        if not path.exists():
            self.config = None
        else:
            config = ConfigParser()
            with path.open() as configFile:
                config.readfp(configFile)
            self.config = config


    def get(self, origin, key, default):
        try:
            return self.config.get(origin, key)
        except (NoOptionError, NoSectionError):
            return default


@inlineCallbacks
def main(reactor, *argv):
    config = Options()
    config.parseOptions(argv[1:])

    try:
        origin = yield git.ensureGitRepository(reactor=reactor)
        if config['branch'] is None:
            mirror = int(config.get(origin, b"svn_mirror", b"1"))
            if mirror:
                config['branch'] = yield git.getCurrentSVNBranch(reactor=reactor)
            else:
                config['branch'] = yield git.getCurrentBranch(reactor=reactor)
    except git.NotAGitRepository:
        raise SystemExit("Must specify a branch to build or be in a git repository.")
    except git.NotASVNRevision:
        raise SystemExit("Current commit hasn't been pushed to svn.")

    url = config.get(origin, b"url", b"http://buildbot.twistedmatrix.com/")
    scheduler = config.get(origin, b"scheduler", b"force-supported")
    username = config.get(origin, b"username", b"twisted")
    password = config.get(origin, b"password", b"matrix")
    results = config.get(origin, b"results", b"%sboxes-supported?branch=%%s" % (url,))
    prefix = config.get(origin, b"branch-prefix", b"/branches/")
    branchKey = config.get(origin, b"branch-key", b"branch")
    extra = config.get(origin, b"extra", None)

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
        ('reason', reason),
        ]

    if extra:
        args.extend(item.split(b"=", 1) for item in extra.split(b"&"))

    if tests is not None:
        args += [('test-case-name', tests)]

    print 'Forcing...', url, args
    yield buildbot.forceBuild(url, args, reactor=reactor)
    print 'Forced.'
    print 'See', results % (urllib.quote(branch),), 'for results.'
