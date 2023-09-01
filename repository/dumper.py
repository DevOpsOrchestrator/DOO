# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import yaml

from ansible.module_utils.six import text_type, binary_type
from ansible.module_utils.common.yaml import SafeDumper
from ansible.parsing.yaml.objects import AnsibleUnicode, AnsibleSequence, AnsibleMapping, AnsibleVaultEncryptedUnicode
from ansible.utils.unsafe_proxy import AnsibleUnsafeText, AnsibleUnsafeBytes, NativeJinjaUnsafeText, NativeJinjaText
from ansible.template import AnsibleUndefined
from ansible.vars.hostvars import HostVars, HostVarsVars
from ansible.vars.manager import VarsWithSources

from ansible.playbook.block import Block
from ansible.playbook.task import Task
from ansible.playbook.handler import Handler



class AnsibleDumperRepository(SafeDumper):
    '''
    A simple stub class that allows us to add representers
    for our overridden object types.
    '''


def represent_hostvars(self, data):
    return self.represent_dict(dict(data))


# Note: only want to represent the encrypted data
def represent_vault_encrypted_unicode(self, data):
    return self.represent_scalar(u'!vault', data._ciphertext.decode(), style='|')


def represent_unicode(self, data):
    return yaml.representer.SafeRepresenter.represent_str(self, text_type(data))


def represent_binary(self, data):
    return yaml.representer.SafeRepresenter.represent_binary(self, binary_type(data))


def represent_undefined(self, data):
    # Here bool will ensure _fail_with_undefined_error happens
    # if the value is Undefined.
    # This happens because Jinja sets __bool__ on StrictUndefined
    return bool(data)

def represent_block(self, data):
    blocks = {'block':[]}
    for task in data.block:
        blocks['block'].append(task_to_dict(task))
    return self.represent_dict(blocks)

def represent_task(self, data):
    task = task_to_dict(data)
    return self.represent_dict(task)

def task_to_dict(data):
    task = {}
    if hasattr(data, 'name') and data.name:
        task['name'] = data.name
    if hasattr(data, 'action') and data.action:
        task[data.action] = data.args
    if hasattr(data, 'notify') and data.notify:
        task['notify'] = data.notify

    return task

AnsibleDumperRepository.add_representer(
    Handler,
    represent_task,
)

AnsibleDumperRepository.add_representer(
    Block,
    represent_block,
)

AnsibleDumperRepository.add_representer(
    Task,
    represent_task,
)

AnsibleDumperRepository.add_representer(
    AnsibleUnicode,
    represent_unicode,
)

AnsibleDumperRepository.add_representer(
    AnsibleUnsafeText,
    represent_unicode,
)

AnsibleDumperRepository.add_representer(
    AnsibleUnsafeBytes,
    represent_binary,
)

AnsibleDumperRepository.add_representer(
    HostVars,
    represent_hostvars,
)

AnsibleDumperRepository.add_representer(
    HostVarsVars,
    represent_hostvars,
)

AnsibleDumperRepository.add_representer(
    VarsWithSources,
    represent_hostvars,
)

AnsibleDumperRepository.add_representer(
    AnsibleSequence,
    yaml.representer.SafeRepresenter.represent_list,
)

AnsibleDumperRepository.add_representer(
    AnsibleMapping,
    yaml.representer.SafeRepresenter.represent_dict,
)

AnsibleDumperRepository.add_representer(
    AnsibleVaultEncryptedUnicode,
    represent_vault_encrypted_unicode,
)

AnsibleDumperRepository.add_representer(
    AnsibleUndefined,
    represent_undefined,
)

AnsibleDumperRepository.add_representer(
    NativeJinjaUnsafeText,
    represent_unicode,
)

AnsibleDumperRepository.add_representer(
    NativeJinjaText,
    represent_unicode,
)
