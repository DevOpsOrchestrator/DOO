#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import argparse
import sys
from os import environ

KEYNAME_UNKNOWN_RC = 2


def build_arg_parser():
    parser = argparse.ArgumentParser(description='Get a vault password from user keyring')

    parser.add_argument('--vault-id', action='store', default=None,
                        dest='vault_id',
                        help='name of the vault secret to get from keyring')
    parser.add_argument('--username', action='store', default=None,
                        help='the username whose keyring is queried')
    parser.add_argument('--set', action='store_true', default=False,
                        dest='set_password',
                        help='set the password instead of getting it')
    return parser


def main():
    arg_parser = build_arg_parser()
    args = arg_parser.parse_args()
    
    vault_pass = str(environ.get('VAULT_PASS', None))
    
    sys.stdout.write('%s\n' % vault_pass)
    sys.exit(0)


if __name__ == '__main__':
    main()