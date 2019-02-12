import json
import sqlite3
import os
import sys


def get_dirs():
    """
    :func:`get_dirs` checks whether the directories exist, and gets their paths.

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

    return db_dir, ss_dir


def update_db(db_dir):
    """
    :func:`update_db` amends databases given a `db_dir`.
    This assumes the existing databases, if they exist at all, are valid.

    Returns:
        list: len of 0 for no errors, +1 for each additional error
    """
    errs = []

    for db in os.listdir(db_dir):
        if db.endswith('.db'):
            try:
                db = os.path.join(os.path.abspath(db_dir), db)
                conn = sqlite3.connect(db)
                cursor = conn.cursor()
                cursor.execute('create table roles(role text, mention text)')
                cursor.execute('create table channels(type text, channel text)')
                cursor.execute('create table contribution(userid text, points real)')
                conn.commit()
                conn.close()
            except:
                errs.append(db)


db_dir, ss_dir = get_dirs()
update_db(db_dir)