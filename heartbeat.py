#!/usr/bin/env python
#
# Heartbeat.py - Monitor health of microservices, and take configurable
#   actions whenever those services change state.

################################################################################
# User defined constants.

DEFAULT_CONFIG = '/usr/local/etc/wiredrive/heartbeat.conf'

################################################################################
# Dependencies.

import argparse
import fcntl
import grp
import logging
import logging.handlers
import multiprocessing
import os
import pwd
import signal
import socket
import sys
import time

from ConfigParser import ConfigParser

import daemon
import requests

if os.name == 'posix' and sys.version_info.major < 3:
    import subprocess32 as subprocess
else:
    import subprocess

################################################################################
# Parse command line arguments and configuration file.

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Monitor health of microservices.')

    parser.add_argument('-c', '--config', dest='config_file',
                        metavar='<file>', default=DEFAULT_CONFIG,
                        help='Specify custom configuration file.')
    parser.add_argument('-d', '--daemonize', dest='daemonize',
                        action='store_const', const=True, default=False,
                        help='Run Heartbeat in the background.')

    args = parser.parse_args()

    return args


def populate_service_checks(parser):
    """Populate service checks from configuration file."""
    service_checks = []

    promotions = dict(
        set(parser.items('promotions')) - set(parser.defaults().items()))
    demotions = dict(
        set(parser.items('demotions')) - set(parser.defaults().items()))

    for section in set(
            parser.sections()) ^ set(['general', 'promotions', 'demotions']):
        check = {}

        check['name'] = section
        check['hostname'] = parser.get(section, 'hostname')
        check['path'] = parser.get(section, 'path')
        check['port'] = parser.getint(section, 'port')
        check['timeout'] = parser.getint(section, 'timeout')
        check['type'] = parser.get(section, 'type').lower()

        check['promotion'] = promotions[parser.get(section, 'action')]
        check['demotion'] = demotions[parser.get(section, 'action')]

        service_checks.append(check)

    return service_checks


def parse_config_file(config_file):
    """Return sanitized configuration option and service check lists."""
    config = {}

    parser = ConfigParser()

    try:
        parser.read(config_file)

        # General options.
        config['daemonize'] = parser.getboolean('general', 'daemonize')
        config['group'] = parser.get('general', 'group')
        config['interval'] = parser.getint('general', 'interval')
        config['logfile'] = parser.get('general', 'logfile')
        config['loglevel'] = parser.get('general', 'loglevel')
        config['pidfile'] = parser.get('general', 'pidfile')
        config['threads'] = parser.getint('general', 'threads')
        config['user'] = parser.get('general', 'user')

        config['service_checks'] = populate_service_checks(parser)

        if config['user'] == 'None':
            config['user'] = pwd.getpwuid(os.getuid()).pw_name
        if config['group'] == 'None':
            config['group'] = grp.getgrgid(os.getgid()).gr_name
    except Exception as error:
        print error
        print 'Failed to parse configuration file %s, exiting.' % config_file
        sys.exit(1)

    return config


################################################################################
# Initialize logging library.

def initialize(config):
    """Set up logger and log message handler."""
    logger = logging.getLogger(__name__)
    handler = logging.handlers.RotatingFileHandler(
        config['logfile'], maxBytes=1000000, backupCount=4)

    # Set desired output level and logging format.
    numeric_loglevel = getattr(logging, config['loglevel'].upper(), None)

    if not isinstance(numeric_loglevel, int):
        print 'Invalid log level: %s' % config['loglevel']
        print 'Defaulting to INFO.'
        numeric_loglevel = 20

    logger.setLevel(numeric_loglevel)
    log_format = logging.Formatter(
        fmt='%(asctime)-19s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(log_format)

    # Add the log message handler to the logger.
    logger.addHandler(handler)

    # Initial log message.
    pid = str(os.getpid())

    if config['daemonize']:
        mode = 'Daemon'
    else:
        mode = 'Run Once'

    logger.info('Heartbeat started (%s). Mode: %s.', pid, mode)
    logger.info('Log level: %s.' % config['loglevel'].upper())

    return logger

################################################################################
# Establish runtime propriety.

def create_pid_file(config):
    # Check for a PID file, and create our own.
    if os.path.isfile(config['pidfile']):
        with open(config['pidfile'], 'r') as openfile:
            old_pid = openfile.readline()
        logger.warning('PID file %s already exists (%s).', pidfile, old_pid)

    try:
        file(config['pidfile'], 'w').write(pid)
    except Exception as error:
        print error
        logger.error('Failed to write to PID file %s.', pidfile)


class LockFile(object):
    def __init__(self, path):
        self.path = path
        self.pidfile = None

    def __enter__(self):
        self.pidfile = open(self.path, 'w+', 0)

        try:
            fcntl.flock(self.pidfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            message = 'Failed to acquire exclusive lock on %s.' % self.path
            raise SystemExit(message)

        self.pidfile.write(str(os.getpid()))

        return self.pidfile

    def __exit__(self, exc_type=None, exc_value=None, exc_tb=None):
        try:
            self.pidfile.close()
        except IOError as err:
            # File descriptor may already be closed.
            if err.errno != 9:
                raise

        os.remove(self.path)

################################################################################
# Core health check functionality.

def check_http(check):
    """Return HTTP status code. True for 200, false otherwise."""
    try:
        vein = requests.get(
            check['type'] + '://' + \
            check['hostname'] + ':' + \
            str(check['port']) + \
            check['path'],
            timeout = check['timeout']
        )

        alive = vein.status_code
    except:
        # Ideally, we'd capture the reason for failure here in a
        # granular fashion, and record it in the debug logs.
        alive = False

    check['status'] = True if alive == 200 else False

    return check


def check_tcp(check):
    """Return the status of the socket. True for open, false for closed."""
    artery = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    artery.settimeout(check['timeout'])
    alive = artery.connect_ex((check['hostname'], check['port']))

    check['status'] = True if alive == 0 else False

    if check['status']:
        artery.shutdown(socket.SHUT_RDWR)
        artery.close()

    return check


def stethoscope(check):
    """Call the appropriate monitor function."""
    if check['type'] == 'http' or check['type'] == 'https':
        pulse = check_http(check)
    if check['type'] == 'tcp':
        pulse = check_tcp(check)

    return pulse


def parse_results(results, logger):
    """Iterate through health check results, and flag any failures."""
    errors = False

    for result in results:
        status = 'Healthly' if result['status'] else 'Unhealthy'

        check_string = '[Service Check] ' + \
            'Name: %s, Endpoint: %s:%i, Type: %s, Timeout: %i, Status: %s' % (
            result['name'], result['hostname'], result['port'], result['type'],
            result['timeout'], status
        )

        if result['status']:
            logger.debug(check_string)
        else:
            errors = True
            logger.error(check_string)

    return errors


def take_action(action, logger):
    """Run subprocess calls defined in configuration file."""
    logger.debug('Running: %s', action)
    try:
        subprocess.check_output(action.split())
    except subprocess.CalledProcessError as error:
        clean_error = error.output.strip()

        logger.error('Action failed: %s.', clean_error)
        logger.debug('Action returned a non-zero exit code: %s.',
                     error.returncode)
        logger.debug('Unsanitized: %s', error.output)


def defibrillate(service_checks, logger):
    """Bring healthy node into rotation."""
    logger.debug('All critical services are up.')
    logger.debug('Running healthy node promotion actions.')

    for action in set(map(lambda x: x['promotion'], service_checks)):
        take_action(action, logger)


def euthanize(service_checks, logger):
    """Remove unhealthy node from rotation."""
    logger.info(
        'One or more critical services detected down. ' + \
        'Running node demotion actions.')

    for action in set(map(lambda x: x['demotion'], service_checks)):
        take_action(action, logger)


def check_pulse(config, logger):
    """Distribute service check operations to subprocesses."""
    parallelize = multiprocessing.Pool(config['threads'])
    bpm = parallelize.map(stethoscope, config['service_checks'])
    flatline = parse_results(bpm, logger)

    if flatline:
        euthanize(config['service_checks'], logger)
    else:
        defibrillate(config['service_checks'], logger)

    parallelize.close()

################################################################################
# Daemonize and run.

def build_context(config):
    """Build daemon context from user defined config."""
    context = daemon.DaemonContext(
        pidfile = LockFile(config['pidfile']),
        uid = pwd.getpwnam(config['user']).pw_uid,
        gid = grp.getgrnam(config['group']).gr_gid,
        working_directory = os.getcwd()
    )

    if config['loglevel'].upper() == 'DEBUG':
        context.stderr = sys.stderr
        context.stdout = sys.stdout

    return context


def terminate(logger):
    """Remove pid file and exit cleanly."""
    logger.info('One-time run-through complete. Goodbye.')
    sys.exit()


def daemonize(context, config):
    """Drop priveleges, launch a child process and terminate the main process."""
    with context:
        # Initial log message.
        logger = initialize(config)

        while True:
            # Check for a pulse.
            check_pulse(config, logger)

            # Better alternative to sleeping here might be to leverage a threaded
            # scheduler (e.g. https://github.com/dbader/schedule).
            time.sleep(config['interval'])


def run_once(context, config):
    """Run through checks once, perform any actions necessary and then exit."""
    with context:
        # Initial log message.
        logger = initialize(config)

        # Check for a pulse.
        check_pulse(config, logger)

        # Exit cleanly.
        terminate(logger)


def run():
    """Parse configuration file and launch daemon."""
    args = parse_arguments()
    config = parse_config_file(args.config_file)
    context = build_context(config)

    if args.daemonize or config['daemonize']:
        daemonize(context, config)
    else:
        run_once(context, config)


if __name__ == '__main__':
    run()
