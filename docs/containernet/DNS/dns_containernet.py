#!/usr/bin/python

from containernet.cli import CLI
from containernet.link import TCLink
from containernet.net import Containernet
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Link
from mininet.term import makeTerm
import os


def topology():
    "Create a network with some docker containers acting as hosts."

    net = Containernet()

    #Setting the display to output on the monitor
    os.system('sudo xhost +local:docker')
    os.system('export DISPLAY=:0')

    info('*** Adding docker containers\n')

    d1 = net.addDocker('postgres', ip='10.0.0.240', dimage="thiagoabreulima/postgres_validacao:latest",
                       port_bindings={5432: 5432}, volumes=["doo-postgres-data:/var/lib/postgresql/data"],
                       environment={"POSTGRES_DB": "doo",
                                    "POSTGRES_PASSWORD": "postgres",
                                    "POSTGRES_USER": "postgres"})

    d2 = net.addDocker('gitlab', ip='10.0.0.241', dimage="gitlab/gitlab-ce:latest",
                       port_bindings={80: 80, 443: 443},
                       environment={'GITLAB_OMNIBUS_CONFIG':"external_url 'http://10.0.0.241'",
                                    'GITLAB_ROOT_PASSWORD':'doo$654321',
                                    'GITLAB_SHARED_RUNNERS_REGISTRATION_TOKEN':'j5ZKrgztV5Qm9Cyg5ZFz'},
                       volumes=["/etc/gitlab", "/var/log/gitlab", "/var/opt/gitlab"])

    d3 = net.addDocker('runner', ip='10.0.0.242', dimage="thiagoabreulima/gitlab_runner:latest",
                       environment={"CI_SERVER_URL": "10.0.0.241",
                                    "REGISTRATION_TOKEN": "j5ZKrgztV5Qm9Cyg5ZFz"},
                       volumes=["/etc/gitlab-runner", "/var/run/docker.sock"])

    d4 = net.addDocker('doo', ip='10.0.0.243', dimage="devopsorchestrator/doo:latest",
                       port_bindings={8000: 8000},
                       environment={"DB_NAME": "doo",
                                    "DB_PASSWORD": "postgres",
                                    "DB_USER": "postgres",
                                    "DB_HOST": "10.0.0.240",
                                    "DEBUG": True,
                                    "DB_WAIT_DEBUG": 1,
                                    "SKIP_SUPERUSER": "false",
                                    "SUPERUSER_API_TOKEN": "0123456789abcdef0123456789abcdef01234567",
                                    "SUPERUSER_EMAIL": "admin@example.com",
                                    "SUPERUSER_NAME": "admin",
                                    "SUPERUSER_PASSWORD": "admin"},
                        volumes=["repositorio:/home/app/repository",])

    d5 = net.addDocker('apache1', ip='10.0.0.244', volumes=['/tmp/.X11-unix:/tmp/.X11-unix:rw'],
                       privileged=True, environment={'DISPLAY': ":0"},
                       dimage="thiagoabreulima/validacao:latest",
                       port_bindings={8080: 80, 9922: 22})
    
    d6 = net.addDocker('bind9', ip='10.0.0.245', volumes=['/tmp/.X11-unix:/tmp/.X11-unix:rw'],
                       privileged=True, environment={'DISPLAY': ":0"},
                       dimage="thiagoabreulima/validacao:latest",
                       port_bindings={9953: 53, 2222: 22})
    
    d7 = net.addDocker('client', ip='10.0.0.246', volumes=['/tmp/.X11-unix:/tmp/.X11-unix:rw'],
                       privileged=True, environment={'DISPLAY': ":0"},
                       dimage="thiagoabreulima/validacao:latest",
                       port_bindings={4622: 22})

    info('*** Adding switch\n')
    s1 = net.addSwitch('s1', failMode='standalone')

    info('*** Creating links\n')
    net.addLink(d1, s1)
    net.addLink(d2, s1)
    net.addLink(d3, s1)
    net.addLink(d4, s1)
    net.addLink(d5, s1)
    net.addLink(d6, s1)
    net.addLink(d7, s1)

    info('*** Starting network\n')
    net.start()

    d1.cmd('/usr/local/bin/docker-entrypoint.sh postgres &')
    d2.cmd('/assets/wrapper &')
    d3.cmd('gitlab-runner start &')
    d4.cmd('/home/app/doo/docker-entrypoint.sh &')
    d5.cmd('service ssh start')
    d6.cmd('service ssh start')
    d7.cmd('service ssh start')

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network')
    net.stop()


if __name__ == '__main__':
    setLogLevel('debug')
    topology()
