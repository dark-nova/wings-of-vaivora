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

    Args:
        db_dir (str): the location of the database files

    Returns:
        list: len of 0 for no errors, +1 for each additional error
    """
    errs = []

    for db in os.listdir(db_dir):
        if db.endswith('.db'):
            try:
                db_fp = os.path.join(os.path.abspath(db_dir), db)
                conn = sqlite3.connect(db_fp)
                cursor = conn.cursor()
                cursor.execute('drop table if exists permissions')
                cursor.execute('drop table if exists reminders')
                cursor.execute('drop table if exists talt')
                cursor.execute('drop table if exists boss')
                cursor.execute('drop table if exists roles')
                cursor.execute('drop table if exists owner')
                cursor.execute('drop table if exists contribution')
                cursor.execute(
                    'create table contribution(mention integer, points integer)')
                cursor.execute(
                    'create table owner(mention integer)')
                cursor.execute(
                    'create table offset(hours integer)')
                cursor.execute(
                    'create table guild(level integer, points integer)')
                cursor.execute(
                    'create table roles(role text, mention integer)')
                cursor.execute(
                    'create table channels(type text, channel integer)')
                cursor.execute(
                    """create table boss(name text,channel {0},
                                   map text,status text,text_channel text,
                                   year {0},month {0},day {0},
                                   hour {0},minute {0})"""
                    .format('integer'))
                conn.commit()
                conn.close()
            except Exception as e:
                print('Exception handled:', e, 'in', db)
                errs.append(db)
    return errs


def transfer_data(db_dir, ss_dir, skips=None):
    """
    :func:`transfer_data` moves data existing from files in `ss_dir` to `db_dir`.

    Args:
        db_dir (str): the location of the database files
        ss_dir (str): the location of the existing server settings files
        skips: (default: None) the invalid databases to skip

    Returns:
        list: len of 0 of no errors, +1 for each additional error
    """
    errs = []

    for db in os.listdir(db_dir):
        if db.endswith('.db'):
            ss = db.rstrip('.db') + '.json'
            ss = os.path.join(os.path.abspath(ss_dir), ss)
            db = os.path.join(os.path.abspath(db_dir), db)
            if skips and db in skips:
                errs.append(db)
                continue
            if not os.path.isfile(ss):
                errs.append(ss)
                continue

            try:
                with open(ss, 'r') as ssf:
                    ssjson = json.load(ssf)
            except json.JSONDecodeError as e:
                print('Couldn\'t read JSON!', e)
                errs.append(ss)
                continue

            conn = sqlite3.connect(db)
            cursor = conn.cursor()


            # add users back to their assigned roles
            for role, user in ssjson['users'].items():
                if role == 's-authorized':
                    continue
                for _u in user:
                    cursor.execute('insert into roles values(?, ?)',
                                   (role, _u))

            conn.commit()

            # add groups back to their assigned roles
            for role, group in ssjson['group'].items():
                if role == 's-authorized':
                    continue
                for _g in group:
                    cursor.execute('insert into roles values(?, ?)',
                                   (role, _g))

            conn.commit()

            # add only groups back to boss role
            for role, group in ssjson['role'].items():
                for _g in group:
                    if '@' in _g:
                        continue
                    cursor.execute('insert into roles values(?, ?)',
                                   (role, _g))

            conn.commit()

            # add channels
            for ch_type, channels in ssjson['channel'].items():
                if ch_type == 'management':
                    ch_type = 'settings'
                for channel in channels:
                    cursor.execute('insert into channels values(?, ?)',
                                   (ch_type, channel))

            conn.commit()

            # add contribution points to guild
            for user, points in ssjson['talt'].items():
                if type(points) is not int:
                    points = int(points)
                if user == 'guild':
                    cursor.execute('insert into guild values(?, ?)',
                                   (ssjson['guild_level'], points))
                else:
                    cursor.execute(
                        'insert into contribution values(?,?)',
                        (user, points))

            conn.commit()
            conn.close()

    return errs


db_dir, ss_dir = get_dirs()
errs = update_db(db_dir)
errs = transfer_data(db_dir, ss_dir)

if not errs:
    print('It is now safe to remove the server settings directory')