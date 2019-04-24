import json
import sqlite3
import os


def get_dirs():
    """Checks whether the directories exist, and gets their paths.

    Returns:
        tuple of str: if successful
        bool: False otherwise

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


queries = [
    'drop table if exists permissions',
    'drop table if exists reminders',
    'drop table if exists talt',
    'drop table if exists boss',
    'drop table if exists roles',
    'drop table if exists owner',
    'drop table if exists contribution',
    'create table contribution(mention integer, points integer',
    'create table owner(mention integer)',
    'create table offset(hours integer)',
    'create table guild(level integer, points integer)',
    'create table roles(role text, mention integer)',
    'create table channels(type text, channel integer)',
    """create table boss(name text,channel {0},
    map text,status text,text_channel text,
    year {0},month {0},day {0},
    hour {0},minute {0},"""
    .format('integer',)
    ]


def update_db(db_dir: str):
    """Updates databases in a `db_dir`.

    This assumes the existing databases, if they exist at all, are valid.

    Args:
        db_dir (str): the location of the database files

    Returns:
        list of str: Exceptions

    """
    errs = []

    for db in os.listdir(db_dir):
        if db.endswith('.db'):
            try:
                db_fp = os.path.join(os.path.abspath(db_dir), db)
                conn = sqlite3.connect(db_fp)
                cursor = conn.cursor()
            except Exception as e:
                errs.append(db, e)
                print('Could not open file:', db)
                return errs

            for query in queries:
                try:
                    cursor.execute(query)
                except Exception as e:
                    print('Exception handled:', e, 'in', db)
                    errs.append(db, query)

            conn.commit()
            conn.close()
            
    return errs


def transfer_data(db_dir, ss_dir, skips=None):
    """Transfers data existing from files in `ss_dir` to `db_dir`.

    `ss_dir` contains the legacy `server_settings` JSON files.

    `db_dir` contains the sqlite3 db files.

    Args:
        db_dir (str): the location of the database files
        ss_dir (str): the location of the existing server settings files
        skips (list, optional): a list of invalid databases to skip;
            defaults to None

    Returns:
        list: containing file names of files that produced errors

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
                    points = int(points)*20
                if user == 'guild':
                    cursor.execute('insert into guild values(?, ?)',
                                   (ssjson['guild_level'], points))
                elif user == 'remainder':
                    cursor.execute('insert into contribution values(?, ?)',
                                   ('0', points))
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