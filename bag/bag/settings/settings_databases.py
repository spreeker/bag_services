import os
import re


def get_docker_host():
    """
    Looks for the DOCKER_HOST environment variable to find the VM
    running docker-machine.
    If the environment variable is not found, it is assumed that
    you're running docker on localhost.
    """
    d_host = os.getenv('DOCKER_HOST', None)
    if d_host:
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', d_host):
            return d_host

        return re.match(r'tcp://(.*?):\d+', d_host).group(1)
    return 'localhost'


def in_docker():
    """
    Checks pid 1 cgroup settings to check with reasonable certainty we're in a
    docker env.
    :return: true when running in a docker container, false otherwise
    """
    try:
        return ':/docker/' in open('/proc/1/cgroup', 'r').read()
    except:
        return False


OVERRIDE_HOST_ENV_VAR = 'DATABASE_HOST_OVERRIDE'
OVERRIDE_PORT_ENV_VAR = 'DATABASE_PORT_OVERRIDE'

OVERRIDE_EL_HOST_VAR = 'ELASTIC_HOST_OVERRIDE'
OVERRIDE_EL_PORT_VAR = 'ELASTIC_PORT_OVERRIDE'

class LocationKey:
    local = 'local'
    docker = 'docker'
    override = 'override'


def get_database_key():
    if os.getenv(OVERRIDE_HOST_ENV_VAR) and os.getenv(OVERRIDE_EL_HOST_VAR):
        return LocationKey.override
    elif in_docker():
        return LocationKey.docker

    return LocationKey.local