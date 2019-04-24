import sqlite3
import os


def get_dirs():
    """Checks whether the db directory exist, and gets its path.

    Returns:
        str: the file name of the directory

    """
    if os.path.isdir('db'):
        db_dir = 'db'
    elif os.path.isdir('../db'):
        db_dir = '../db'
    else:
        print('No db directory found!')
        return False

    return db_dir


queries = [
    'drop table if exists permissions',
    'drop table if exists reminders',
    'drop table if exists talt',
    'drop table if exists boss',
    'drop table if exists channels',
    'drop table if exists roles',
    'drop table if exists guild',
    'drop table if exists offset',
    'drop table if exists owner',
    'drop table if exists contribution',
    'create table contribution(mention integer, points integer)',
    'create table owner(mention integer)',
    'create table offset(hours integer)',
    'create table guild(level integer, points integer)',
    'create table roles(role text, mention integer)',
    'create table channels(type text, channel intege)r',
    """create table boss(name text,channel {0},
       map text,status text,text_channel text,
       year {0},month {0},day {0},
       hour {0},minute {0})"""
    .format('integer')
    ]


def rebuild_dbs(db_dir: str):
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

if rebuild_dbs(get_dirs()):
    print('Could not rebuild all. Check permissions.')
else:
    print('Successfully rebuilt all db\'s.')
