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
              help="Print debugging statements and keep tarball and patchset around.")
              
    op.add_option("-u", "--username",
              dest="username", 
              help="Your username, default is %s" % getpass.getuser(), 
              default=getpass.getuser())
    
    op.add_option("-s", "--summary",
              dest="summary",
              help="The summary for a new ticket - required if -t is not set.")
    
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
              help="Build a patch set from all patches in the series.")
              
    op.add_option("-r", "--reviewer",
              dest="reviewer", 
              help="Assigning  the ticket to REVIEWER")
              
    op.add_option("-c", "--component",
              dest="component", 
              help="Assigning the ticket to COMPONENT")

    op.add_option("-e", "--milestone",
              dest="milestone",
              help="The ticket milestone.")
                        
    op.add_option("--server",
              dest="server",
              default="https://svnweb.cern.ch/no_sso/trac/CMSDMWM/login/xmlrpc",
              help="The trac server to use.")

    op.add_option("--noclean",
              dest="clean", 
              action="store_false",
              default=True, 
              help="Don't clean up the tarball and patchset, over ridden by --debug.")
    
    op.add_option("--realm",
              dest="realm",
              default="Subversion at CERN",
              help="The HTTP auth realm")

    op.add_option("--dryrun",
              dest="dryrun",
              action="store_true",
              default=False, 
              help="Do a dry run, build the patch set locally but don't send to trac.")              


    options, args = op.parse_args()
    
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger('submit_patch')
    if args == [] and not options.all:
      logger.critical("You must provide the names of one or more patches, or use the -a/--all flag.")
      sys.exit(101)
    if options.ticket == None and options.summary == None:
      logger.critical("You must provide a ticket id to update an exisitng ticket or a summary to create a new ticket")
      sys.exit(102)
    if options.verbose:
        logger.setLevel(logging.INFO)
    if options.debug:
        logger.setLevel(logging.DEBUG)

    logger.info('options: %s, args: %s' % (options, args))
    
    return options, args, logger
    
def run(command, logger, cwd=None):
    proc = subprocess.Popen(
            [command], shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd
            )
    stdout, stderr =  proc.communicate()
    rc = proc.returncode
    return stdout, stderr, rc

    if rc != 0:
        logger.warning("failure to run %s" % command)
        logger.debug(stdout)
        logger.debug(stderr)
        sys.exit(rc)

def build_patchset(patches, user, logger, basedir):
  """
  Call stg and build up the necessary path/patchset tarball, return the name of
  the tar file and the tar as base64 encoded data. 
  """  
  patchseries = "patch-series-%s" % (user)
  filename = "patch-series-%s.tar.gz" % (user)
  
  stg_cmd = "stg export -d %s -p -n %s" % (patchseries, " ".join(patches))
  logger.debug(stg_cmd)
  assert run(stg_cmd, logger, basedir)[2] == 0, '%s failed - check debug output' % stg_cmd
  
  tar_cmd = "tar -zcf %s %s" % (filename, patchseries)
  logger.debug(tar_cmd)
  assert run(tar_cmd, logger, basedir)[2] == 0, '%s failed - check debug output' % tar_cmd
  
  return filename

def clean_patchset(user, basedir):
  """
  Delete the tar ball and patchset directory.
  """
  patchset = "patch-series-%s" % (user)
  filename = "patch-series-%s.tar.gz" % (user)
  
  clean_cmd = 'rm -rf %s %s' % (patchset, filename)
  
  assert run(clean_cmd, logger, basedir)[2] == 0, '%s failed - check debug output' % clean_cmd

def list_patchset_contents():
  """
  Build a list of all active patches
  """
  series_cmd = "stg series"
  stdout, stderr, rc = run(series_cmd, logger)
  lines = stdout.strip().split('\n')
  patch_set = []
  patch_set_app = patch_set.append
  for l in lines:
    if not l.startswith("-"):
      patch_set_app(l.split()[1])
  return patch_set

def determine_git_version():
  # First get the git version
  version_cmd = "stg --version"
  stdout, stderr, rc = run(version_cmd, logger)
  lines = stdout.split('\n')
  version = {}
  for l in lines:
    tokens = l.strip().split()
    if len(tokens) == 3:
      verParts = tokens[2].split(".")
      version[tokens[0]] = int(verParts[0]) + int(verParts[1]) / 10.0
      
  return version
  
def build_patchset_message(patches):
  """
  Build an appropriate message from stg messages
  """
  msg_cmd = "stg series -a -d"
  stdout, stderr, rc = run(msg_cmd, logger)
  lines = stdout.strip().split('\n')
  message = []
  msg_app = message.append

  for l in lines:
    if not l.startswith("-"):
      if determine_git_version()['Stacked'] >= 0.15:
        patch, patch_message = l.split('#', 1)
      else:
        patch, patch_message = l.split('|', 1)
      patch = patch.split()[1]
      if patch in patches:
        msg_app(patch_message.strip())
  return "\n".join(message)
  
def determine_git_basedir():
  """
  Attempts to work out the current basedir
  """

  version = determine_git_version()['git']
  # Now use the correct magic depending on git version
  basedir = None
  if version >= 1.7:
    # Plays nicely
    baserev, err, rc = run("git rev-parse --show-toplevel", logger)
    if rc == 0:
      basedir = baserev.strip()
  else:
    # Plays in the mud
    cwd = os.getcwd()
    cdup, err, rc = run("git rev-parse --show-cdup", logger)
    if rc == 0:
      # Calculate how many directories to move up
      cdup = cdup.strip().split("/")
      def map_func(a):
        if a == "..":
          return 1
        return 0
      count = sum(map(map_func, cdup))

      # Now strip this many entries from the cwd
      if count > 0:
        parts = cwd.split("/")
        if parts[0] == "":
          parts[0] = "/"
        count = count * -1
        basedir = os.path.join(*parts[0:count])
      else:
        basedir = cwd

  # All done (hopefully)
  return basedir

if __name__ == "__main__":
  options, patches, logger = do_options()
  
  # Get the base directory for the git repository
  basedir = determine_git_basedir()
  component = None
  if basedir:
    if options.component:
      component = options.component
    else:
      # Make an educated guess
      component = basedir.split('/')[-1]

  logger.info('Guessing that the component is %s' % component)
  if options.all:
    # over write patches with everything in the series
    patches = list_patchset_contents()
  logger.debug('Patchset contents:\n\t%s' % '\n\t'.join(patches))

  if options.message == "":
    options.message = build_patchset_message(patches)
  else:
    options.message = '%s\n------------\n%s' % (build_patchset_message(patches), options.message)
  logger.debug('Submitting patchset with the following message:\n%s' % options.message)
  
  
  filename = build_patchset(patches, options.username, logger, basedir)

  if not options.dryrun:
    options.password = getpass.getpass()
  
    basicTransport = HTTPSBasicTransport(options.username, 
                                           options.password, 
                                           options.realm)
    
    server = xmlrpclib.ServerProxy(options.server, transport=basicTransport)
  #['101', <DateTime '20100812T10:49:09' at d34440>, <DateTime '20100824T23:06:29' at d344b8>, {'status': 'closed', 'description': '', 'reporter': 'metson', 'cc': '', 'type': 'defect', 'component': 'SiteDB', 'summary': 'second egroup mailing test', 'priority': 'major', 'owner': 'metson', 'version': '', 'milestone': '', 'keywords': '', 'resolution': 'invalid'}]

    # Build ticket owner / reviewer
    attributes = {}
    if component:
      attributes['component'] = component
    if options.reviewer:
      attributes['owner'] = options.reviewer
    if options.milestone:
      attributes['milestone'] = options.milestone
    
    if not options.ticket:
      logger.info("Creating new ticket")
      options.ticket = server.ticket.create(options.summary, options.message, attributes, True)
      logger.info("Created ticket #%s" % options.ticket)
    logger.debug("Attaching patch to ticket")  
    assert options.ticket == server.ticket.get(options.ticket)[0], 'ticket %s not known' % options.ticket
    ticket_id = int(options.ticket)
    localFileName = filename
    if basedir:
      localFileName = basedir + "/" + localFileName
    server.ticket.putAttachment(ticket_id, 
                                filename,
                                options.message, 
                                xmlrpclib.Binary(open(localFileName).read()))
    if options.reviewer:
      server.ticket.update(ticket_id, 'Please Review', attributes, True)
    
    print 'Patch %s successfully submitted to trac' % options.ticket
  else:
    print 'Dry run complete'
  if options.clean and not options.debug:
    logger.info("Cleaning up temporary files")
    clean_patchset(options.username, basedir)

