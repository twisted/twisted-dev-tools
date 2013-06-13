# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import sys, textwrap, time, datetime, re
from twisted.python import usage
from amptrac.client import connect, DEFAULT_AMP_ENDPOINT

class Options(usage.Options):
    synopsis = "fetch-tickets [options] <ticket id>"

    optParameters = [['port', 'p', DEFAULT_AMP_ENDPOINT,
                      'Service description for the AMP connector.']]

    def parseArgs(self, id):
        self['id'] = int(id)



def termsize():
    try:
        import fcntl, termios, struct
        return struct.unpack('hh', fcntl.ioctl(0, termios.TIOCGWINSZ,
                                               '1234'))
    except:
        return 25, 80


def convertTime(unixtime):
    return datetime.datetime(*time.gmtime(unixtime)[:6])


def splitLines(content):
    return content.split('\r\n')

def splitParagrahs(content):
    para = []
    paras = []
    for line in content:
        if line.strip() == '':
            paras.append(' '.join(para))
            continue


def wrapParagraphs(content, width, indentLevel):
    indent = " " * indentLevel
    lines = splitLines(content)
    for line in lines:
        match = re.match("((?: *>)*)( *(?:[0-9]*\.|-) *)?(.*)", line)
        if match:
            quote, number, line = match.groups()
            number = number or ''
            numberReplace = " " * len(number)
            prefixWidth = len(quote) + len(number) + indentLevel
            initialIndent = indent + quote + number
            subsequentIndent = indent + quote + numberReplace
        else:
            initialIndent = subsequentIndent = indent
        yield textwrap.fill(
                line, width=width - len(initialIndent),
                replace_whitespace=False,
                break_long_words=False,
                initial_indent=initialIndent,
                subsequent_indent=subsequentIndent)



def formatTicket(response):
    height, width = termsize()
    response['time'] = convertTime(response['time'])
    headlines = []
    headlines.append("* #%(id)s - %(summary)s - %(owner)s [%(status)s]" % response)
    headlines.append("`-- keywords: %(keywords)s reporter: %(reporter)s component: %(component)s" % response)
    headlines.append("`-- branch: %(branch)s" % response)
    indent = " " * 4
    body = textwrap.wrap(response['description'], width=width - 8,
                         replace_whitespace=False,
                         initial_indent=indent, subsequent_indent=indent)

    changes = ['\n']
    for item in response['changes']:
        item['time'] = convertTime(item['time'])
        if item['field'] == 'comment':
            changes.append('    ** %(author)s - %(time)s #%(oldvalue)s' % item)
            comment = wrapParagraphs(item['newvalue'], width, 8)
            changes.extend(comment)
        else:
            changes.append('# %(author)s changed %(field)s: '
                           '%(oldvalue)s -> %(newvalue)s' % item)
    sys.__stdout__.write('\n'.join(headlines + body + changes +
                                   ['\n']).encode('utf-8'))



def main(reactor, *argv):
    config = Options()
    config.parseOptions(argv[1:])
    def fetch(client):
        return client.fetchTicket(config['id'], asHTML=False).addCallback(formatTicket)

    return connect(reactor, config['port']).addCallback(fetch)
