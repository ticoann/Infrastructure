"""
submit_patch.py

Send a patch set to a trac ticket.
"""
import sys
import xmlrpclib
import getpass
import logging
import subprocess
import base64
import os
import urllib2
import tarfile
import tempfile
import StringIO
import glob

from urlparse import urlparse, urlunparse
from optparse import OptionParser

class HTTPSBasicTransport(xmlrpclib.SafeTransport):
    """
    Transport that uses urllib2 so that we can do Basic authentication.

    Based upon code at http://bytes.com/topic/python/answers/509382-solution-xml-rpc-over-proxy
    """

    def __init__(self, username, pw, realm, verbose = None, use_datetime=0):
        self.__username = username
        self.__pw = pw
        self.__realm = realm
        self.verbose = verbose
        self._use_datetime = use_datetime

    def request(self, host, handler, request_body, verbose):
        url='https://'+host+handler
        if verbose or self.verbose:
            print "ProxyTransport URL: [%s]"%url

        request = urllib2.Request(url)
        request.add_data(request_body)
        # Note: 'Host' and 'Content-Length' are added automatically
        request.add_header("User-Agent", self.user_agent)
        request.add_header("Content-Type", "text/xml") # Important

        # setup basic authentication
        authhandler = urllib2.HTTPBasicAuthHandler()
        authhandler.add_password(self.__realm, url, self.__username, self.__pw)
        opener = urllib2.build_opener(authhandler)

        #proxy_handler=urllib2.ProxyHandler()
        #opener=urllib2.build_opener(proxy_handler)
        f=opener.open(request)
        return(self.parse_response(f))

def do_options():
    op = OptionParser()

    op.add_option("-v", "--verbose",
              dest="verbose",
              action="store_true",
              default=False,
              help="Be more verbose")

    op.add_option("-d", "--debug",
              dest="debug",
              action="store_true",
              default=False,
              help="Print debugging statements and keep a record of the patchset in /tmp")

    op.add_option("-u", "--username",
              dest="username",
              help="Your username, default is %s" % getpass.getuser(),
              default=getpass.getuser())

    op.add_option("-s", "--summary",
              dest="summary",
              help="The summary for a new ticket - required if -t is not set")

    op.add_option("-m", "--message",
              dest="message",
              default="",
              help="Your commit message.")

    op.add_option("-t", "--ticket",
              dest="ticket",
              help="The id of the ticket")

    op.add_option("-a", "--all",
              dest="all",
              action="store_true",
              default=False,
              help="Build a patch set from all patches in the series")

    op.add_option("-r", "--reviewer",
              dest="reviewer",
              help="Assigning the ticket to REVIEWER")

    op.add_option("-c", "--component",
              dest="component",
              help="Assigning the ticket to COMPONENT")

    op.add_option("-e", "--milestone",
              dest="milestone",
              help="The ticket milestone.")

    op.add_option("--mode",
              dest="mode", type="choice",
              default="tarball",
              choices=("diff", "multidiff", "tarball"),
              help="Attachment mode: diff, multidiff, tarball")

    op.add_option("-n", "--name",
            dest="name",
            default=None,
            help="Append NAME to the name tarball or multidiff to create")

    op.add_option("--server",
              dest="server",
              default="https://svnweb.cern.ch/no_sso/trac/CMSDMWM/login/xmlrpc",
              help="The trac server to use.")

    op.add_option("--noclean",
              dest="clean",
              action="store_false",
              default=True,
              help="If set keep a record of the patchset in /tmp")

    op.add_option("--realm",
              dest="realm",
              default="Subversion at CERN",
              help="The HTTP auth realm")

    op.add_option("--dryrun",
              dest="dryrun",
              action="store_true",
              default=False,
              help="Do a dry run, build the patch set locally but don't send to trac")


    options, args = op.parse_args()

    log_level = logging.WARNING
    if options.verbose:
        log_level = logging.INFO
    if options.debug:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)
    logger = logging.getLogger('submit_patch')
    if args == [] and not options.all:
      logger.critical("You must provide the names of one or more patches, or use the -a/--all flag.")
      sys.exit(101)
    if options.ticket == None and options.summary == None:
      logger.critical("You must provide a ticket id to update an exisitng ticket or a summary to create a new ticket")
      sys.exit(102)

    logger.info('options: %s, args: %s' % (options, args))

    return options, args, logger

class GitInterface:
    "Encapsulate all the stuff related to talking to git/stgit"
    def __init__(self):
        self.logger = logging.getLogger("GitInterface")
        self.stg_version, self.git_version = self._version()
        self.basedir = self._basedir()

    def _run(self, cmd, cwd=None):
        "Use subprocess to run a command, and return the stdout. Raise an exception for returncode != 0."
        proc = subprocess.Popen([cmd], shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                cwd=cwd)
        stdout, stderr = proc.communicate()
        rc = proc.returncode
        if rc != 0:
            self.logger.critical("Non-zero return code (%d) from command: %s",
                                 rc, ' '.join(cmd))
            self.logger.critical("STDOUT was: %s", stdout)
            self.logger.critical("STDERR was: %s", stderr)
            raise Exception("Subprocess Error")

        return stdout

    def _version(self):
        "Determine the versions of git and stgit in use"
        git_v = (0,)
        stg_v = (0,)
        for line in self._run('stg -v').lower().split('\n'):
            if 'stacked' in line:
                for item in line.split():
                    if '.' in item:
                        stg_v = tuple(map(int, item.split('.')))
                        self.logger.info("Found stgit version %s", stg_v)
            elif 'git' in line:
                for item in line.split():
                    if '.' in item:
                        git_v = tuple(map(int, item.split('.')))
                        self.logger.info("Found git version %s", git_v)

        return stg_v, git_v

    def _basedir(self):
        "Locate the base directory of the git repository. os.path is your friend."
        if self.git_version >= (1,7):
            basedir = self._run('git rev-parse --show-toplevel').strip()
        else:
            path_to = self._run('git rev-parse --show-cdup').strip()
            basedir = os.path.abspath(path_to)
        self.logger.debug("Found git basedir: %s", basedir)
        return basedir

    def guess_component(self):
        return self.basedir.split('/')[-1]

    def check_file_status(self):
        stdout = self._run('stg status|grep ?').strip().split('\n')
        if len(stdout) > 0:
            print "The following files are not known to stg:"
            print "\n".join(stdout)
            check = raw_input('continue? [y/N]')
            if check != 'y':
                print 'OK, exiting'
                sys.exit(200)

    def list_all_patches(self):
        "List all the patches known to stg that are currently applied"
        stdout = self._run('stg series')
        return [line.split()[1] for line in stdout.strip().split('\n') if not line[0]=='-']

    def generate_message(self, patch_list):
        "Generate a message by concating (with newlines) the short descriptions of the currently applied patches"
        stdout = self._run('stg series -a -d')
        separator = '|'
        if self.stg_version >= (0,15):
            separator = '#'
        messages = [line.split(separator, 1)[-1] for line in stdout.strip().split('\n') if not line[0]=='-']
        return '\n'.join(messages)

    def generate_plaintext(self, patch_list):
        return self._run('stg export -s %s' % ' '.join(patch_list))

    def generate_tarball(self, patch_list, dirname):
        tempdir = tempfile.mkdtemp()
        self._run('stg export -d %s -p -n %s' % (tempdir, ' '.join(patches)))
        tar_buffer = StringIO.StringIO()
        tar_file = tarfile.open(name='tempfile',fileobj=tar_buffer, mode='w:gz')
        tar_file.add(tempdir, arcname=dirname)
        tar_file.close()
        for f in glob.glob(tempdir +'/*'):
            self.logger.debug('Removing %s from %s' % (f, tempdir))
            os.remove(f)
        os.rmdir(tempdir)
        return tar_buffer.getvalue()


if __name__ == '__main__':
    options, patches, logger = do_options()

    gi = GitInterface()

    gi.check_file_status()

    if options.component:
        component = options.component
    else:
        component = gi.guess_component()
        logger.info('Guessing that the component is %s' % component)

    # these are attributes associated to the ticket
    attributes = {}
    logger.debug('Assigning ticket to component: %s' % options.component)
    attributes['component'] = component

    if options.milestone:
        logger.debug('Assigning ticket to milestone: %s' % options.milestone)
     	attributes['milestone'] = options.milestone

    if options.reviewer:
        logger.debug('Assigning ticket to reviewer: %s' % options.reviewer)
        attributes['owner'] = options.reviewer

    all_patches = gi.list_all_patches()

    if options.all:
        patches = all_patches
    else:
        for patch in patches:
            if not patch in all_patches:
                logger.error('Specified patch "%s" is not known to stgit', patch)
        patches = filter(lambda x: x in all_patches, patches)
        if not patches:
            logger.critical('No patches remaining')
            sys.exit(103)

    logger.info("Patchset contains:\n\t%s", "\n\t".join(patches))

    if options.message:
        message = options.message
    else:
        message = gi.generate_message(patches)
        logger.debug('Generated message: %s', message)

    uploads = {} #filename -> data

    if options.mode == 'multidiff':
        for i, patch in enumerate(patches):
            name = '%02d-%s-%s.patch' % (i, options.username, patch)
            uploads[name] = gi.generate_plaintext([patch])
    else:
        # set the base name for the patch
        if options.name:
            basename = '%s-%s' % (options.username, options.name)
        else:
            basename = options.username
        # set the full name for the patch
        if options.mode == 'diff':
            name = 'patch-series-%s.patch' % basename
        elif options.mode == 'tarball':
            name = 'patch-series-%s.tar.gz' % basename

        # generate the patch in memory
        if options.mode == 'diff':
            uploads[name] = gi.generate_plaintext(patches)
        elif options.mode == 'tarball':
            uploads[name] = gi.generate_tarball(patches, name.split('.')[0])

    if options.debug or not options.clean:
        # keep a record of the patch in /tmp
        for name, payload in uploads.items():
            open('/tmp/%s'%name,'wb').write(payload)
            if not options.clean:
                logger.warning('The contents of your patch %s is available in /tmp' % uploads.keys())
            else:
                logger.debug('The contents of your patch %s is available in /tmp' % uploads.keys())

    logger.debug("Upload list contains: %s", uploads.keys())

    if not options.dryrun:
        password = getpass.getpass()

        transport = HTTPSBasicTransport(options.username, password, options.realm)
        server = xmlrpclib.ServerProxy(options.server, transport=transport)

        if not options.ticket:
            logger.info("Creating new ticket")
            options.ticket = server.ticket.create(options.summary, options.message, attributes, True)
            logger.info("Created ticket #%s" % options.ticket)

        logger.debug("Attaching patch to ticket")
        assert options.ticket == server.ticket.get(options.ticket)[0], 'ticket %s not known' % options.ticket
        ticket_id = int(options.ticket)
        for name, payload in uploads.items():
            logger.info("Uploading attachment: %s", name)
            server.ticket.putAttachment(ticket_id,
                                        name,
                                        options.message,
                                        xmlrpclib.Binary(payload))
            logger.info("...upload complete")
        if options.reviewer or options.milestone:
            # Need to update the ticket
            logger.debug("Updating ticket with reviewer/milestone information")

            if options.reviewer and options.milestone:
                msg = 'Please include in the %s milestone\nPlease review' % options.milestone
            elif options.reviewer:
                msg = 'Please Review'
            elif options.milestone:
                msg = 'Please include in the %s milestone' % options.milestone

            server.ticket.update(ticket_id, msg, attributes, True)

        logger.info("Patch successfully submitted to ticket %s", options.ticket)
    else:
        logger.warning("Dry run complete")