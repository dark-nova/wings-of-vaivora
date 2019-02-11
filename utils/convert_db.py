import json
import os
import sys

def main():
    """
    :func:`main`.

    Returns:
        tuple if successful; False otherwise
    """
    in_utils = False

    if os.path.isdir('db'):
        db_dir = 'db'
    elif os.path.isdir('../db'):
        db_dir = '../db'
        in_utils = True
    else:
        print('No db directory found!')
        return False

    if in_utils and os.path.isdir('../server_settings'):
        ss_dir = '../server_settings'
    elif in_utils or os.path.isdir('server_settings'):
        ss_dir = 'server_settings'
    else:
        print('No existing system settings directory found!')
        return False
    
main()
