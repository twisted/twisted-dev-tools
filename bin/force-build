#!/usr/bin/python

"""
Force the Twisted buildmaster to run a builds on all supported builders for
a particular branch.
"""

import os, sys, pwd, urllib

import twisted
from twisted.internet import reactor
from twisted.python import log
from twisted.web import client, http_headers

VERSION = "0.1"

USER_AGENT = (
    "force-builds.py/%(version)s (%(name)s; %(platform)s) Twisted/%(twisted)s "
    "Python/%(python)s" % dict(
        version=VERSION, name=os.name, platform=sys.platform,
        twisted=twisted.__version__, python=hex(sys.hexversion)))

def main():
    if len(sys.argv) == 3:
        branch, comments = sys.argv[1:]
        tests = None
    elif len(sys.argv) == 4:
        branch, comments, tests = sys.argv[1:]
    else:
        raise SystemExit("Usage: %s <branch> <comments> [test-case-name]" % (sys.argv[0],))

    log.startLogging(sys.stdout)
    if not branch.startswith('/branches/'):
        branch = '/branches/' + branch

    def forced(result):
        print 'Forced.'

    args = [
        ('username', 'twisted'),
        ('passwd', 'matrix'),
        ('forcescheduler', 'force-supported'),
        ('revision', ''),
        ('submit', 'Force Build'),
        ('branch', branch),
        ('reason', '%s: %s' % (pwd.getpwuid(os.getuid())[0], comments))]

    if tests:
        args += [('test-case-name', tests)]

    agent = client.Agent(reactor, pool=client.HTTPConnectionPool(reactor))

    headers = http_headers.Headers({'user-agent': [USER_AGENT]})

    print 'Forcing...'
    url = "http://buildbot.twistedmatrix.com/builders/_all/forceall"
    url = url + '?' + '&'.join([k + '=' + urllib.quote(v) for (k, v) in args])
    d = agent.request("GET", url, headers)
    d.addCallback(forced)
    d.addErrback(log.err, "Build force failure")
    d.addCallback(lambda ign: reactor.stop())
    reactor.run()
    print 'See http://buildbot.twistedmatrix.com/boxes-supported?branch=%s' % (branch,)


if __name__ == '__main__':
    main()
