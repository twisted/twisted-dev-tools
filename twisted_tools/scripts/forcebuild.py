"""
Force the Twisted buildmaster to run a builds on all supported builders for
a particular branch.
"""

import os.path, pwd, urllib

from yaml import safe_load

from twisted.python.filepath import FilePath
from twisted.python import usage
from twisted.internet.defer import inlineCallbacks

from twisted_tools import buildbot, git
from twisted_tools.util import findConfig

class Options(usage.Options):
    synopsis = "force-build [options]"

    optParameters = [['branch', 'b', None, 'Branch to build'],
                     ['tests', 't', None, 'Tests to run'],
                     ['comments', None, None, 'Build comments'],
                     ['config', None, None, 'Path to configuration file', os.path.expanduser],
                     ]


    def postOptions(self):
        if self['config'] is not None:
            path = FilePath(self['config'])
        else:
            path = findConfig(FilePath(b'.'), b'.force-build.yml')

        if path and path.exists():
            self.config = safe_load(path.getContents())
        else:
            self.config = {}


    def get(self, origin, key, default=None):
        return self.config.get(key, default)


@inlineCallbacks
def main(reactor, *argv):
    config = Options()
    config.parseOptions(argv[1:])

    try:
        origin = yield git.ensureGitRepository(reactor=reactor)
    except git.NotAGitRepository:
        if config['branch'] is None:
            raise SystemExit("Must specify a branch to build or be in a git repository.")
        origin = None

    if config['branch'] is None:
        try:
            mirror = int(config.get(origin, b"svn_mirror", b"1"))
            if mirror:
                config['branch'] = yield git.getCurrentSVNBranch(reactor=reactor)
            else:
                config['branch'] = yield git.getCurrentBranch(reactor=reactor)
        except git.NotASVNRevision:
            raise SystemExit("Current commit hasn't been pushed to svn.")

    url = config.get(origin, b"url")
    scheduler = config.get(origin, b"scheduler")
    username = config.get(origin, b"username")
    password = config.get(origin, b"password")
    results = config.get(origin, b"results")
    prefix = config.get(origin, b"branch-prefix", b"/branches/")
    branchKey = config.get(origin, b"branch-key", b"branch")
    extra = config.get(origin, b"extra", {})

    branch = config['branch']
    if not branch.startswith(prefix):
        branch = prefix + branch

    reason = '%s: %s' % (pwd.getpwuid(os.getuid())[0], config['comments'])

    tests = config['tests']

    print 'Forcing...', url
    yield buildbot.forceBuild(
            url=url, username=username, password=password,
            scheduler=scheduler, branch=branch, branchKey=branchKey,
            tests=tests, extraArgs=extra, reason=reason,
            reactor=reactor)
    print 'Forced.'
    print 'See', results % (urllib.quote(branch),), 'for results.'
