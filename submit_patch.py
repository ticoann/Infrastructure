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

class HTTPSDigestTransport(xmlrpclib.SafeTransport):
    """
    Transport that uses urllib2 so that we can do Digest authentication.
    
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

        # setup digest authentication
        authhandler = urllib2.HTTPBasicAuthHandler()
        authhandler.add_password(self.__realm, url, self.__username, self.__pw)
        opener = urllib2.build_opener(authhandler)

        #proxy_handler=urllib2.ProxyHandler()
        #opener=urllib2.build_opener(proxy_handler)
        f=opener.open(request)
        return(self.parse_response(f))

def do_options():
    op = OptionParser()
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
              
    op.add_option("-t", "--ticket",
              dest="ticket", 
              help="The id of the ticket")
              
    op.add_option("--server",
              dest="server",
              default="https://svnweb.cern.ch/no_sso/trac/CMSDMWM/login/xmlrpc",
              help="The trac server to use")

    op.add_option("--noclean",
              dest="clean", 
              action="store_false",
              default=True, 
              help="Don't clean up the tarball and patchset, over ridden by --debug.")
    
    op.add_option("--realm",
              dest="realm",
              default="Subversion at CERN",
              help="The HTTP digest realm")
              
    options, args = op.parse_args()
    
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger('submit_patch')
    if args == []:
      logger.critical("You must provide the names of one or more patches")
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
    
def run(command):
    proc = subprocess.Popen(
            [command], shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
            )
    stdout, stderr =  proc.communicate()
    rc = proc.returncode
    return stdout, stderr, rc

    if rc != 0:
        logger.warning("failure to run %s" % command)
        logger.debug(stdout)
        logger.debug(stderr)
        sys.exit(rc)

def build_patchset(patches, user, logger):
  """
  Call stg and build up the necessary path/patchset tarball, return the name of
  the tar file and the tar as base64 encoded data. 
  """  
  patchseries = "patch-series-%s" % (user)
  filename = "patch-series-%s.tar.gz" % (user)
  
  stg_cmd = "stg export -d %s -p -n %s" % (patchseries, " ".join(patches))
  logger.debug(stg_cmd)
  assert run(stg_cmd, logger)[2] == 0, '%s failed - check debug output' % stg_cmd
  
  tar_cmd = "tar -zcf %s %s" % (filename, patchseries)
  logger.debug(tar_cmd)
  assert run(tar_cmd, logger)[2] == 0, '%s failed - check debug output' % tar_cmd
  
  initial_data = open(filename, 'rt').read()

  encoded_data = base64.b64encode(initial_data)

  return filename, encoded_data

def clean_patchset(user):
  """
  Delete the tar ball and patchset directory.
  """
  patchset = "patch-series-%s" % (user)
  filename = "patch-series-%s.tar.gz" % (user)
  
  clean_cmd = 'rm -rf %s %s' % patchset, filename
  
  assert run(clean_cmd, logger)[2] == 0, '%s failed - check debug output' % clean_cmd
  
if __name__ == "__main__":
  options, patches, logger = do_options()
  options.password = getpass.getpass()

  digestTransport = HTTPSDigestTransport(options.username, 
                                         options.password, 
                                         options.realm)
  
  server = xmlrpclib.ServerProxy(options.server, transport=digestTransport)

  filename, tarball = build_patchset(patches, options.username, logger)
  
  if options.ticket:
    assert options.ticket == server.ticket.get(options.ticket)[0], 'ticket %s not known' % options.ticket
    server.ticket.putAttachment(options.ticket, 
                                filename,
                                options.message, 
                                xmlrpclib.Binary(open(filename).read()))
  else: 
    logger.info("creating new ticket")
    
  if options.clean and not options.debug:
      clean_patchset(options.username)