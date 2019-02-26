import sqlite3
import os


def get_dirs():
    """
    :func:`get_dirs` checks whether the directories exist, and gets their paths.

    Returns:
        tuple if successful; False otherwise
    """
    if os.path.isdir('db'):
        db_dir = 'db'
    elif os.path.isdir('../db'):
        db_dir = '../db'
    else:
        print('No db directory found!')
        return False

    return db_dir


def rebuild_dbs(db_dir):
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
                # old tables that were unused
                cursor.execute('drop table if exists permissions')
                cursor.execute('drop table if exists reminders')
                cursor.execute('drop table if exists talt')

                # tables still in use
                cursor.execute('drop table if exists boss')
                cursor.execute('drop table if exists channels')
                cursor.execute('drop table if exists roles')
                cursor.execute('drop table if exists guild')
                cursor.execute('drop table if exists offset')
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

if rebuild_dbs(get_dirs()):
    print('Could not rebuild all. Check permissions.')
else:
    print('Successfully rebuilt all db\'s.')
