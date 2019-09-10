import sqlite3
from pathlib import Path


queries_drop = [
    'drop table if exists boss',
    'drop table if exists channels',
    'drop table if exists contribution',
    'drop table if exists events',
    'drop table if exists guild',
    'drop table if exists offset',
    'drop table if exists owner',
    'drop table if exists roles',
    'drop table if exists tz',
    # Obsolete tables
    'drop table if exists permissions',
    'drop table if exists reminders',
    'drop table if exists talt',
    ]

queries_create = [
    """create table boss(
    name text, channel integer, map text, status text,
    text_channel text,
    year integer, month integer, day integer,
    hour integer, minute integer)""",
    'create table channels(type text, channel integer)',
    'create table contribution(mention integer, points integer)',
    """create table events(
    name text, year integer, month integer, day integer,
    hour integer, minutes integer, enabled integer)""",
    'create table guild(level integer, points integer)',
    'create table offset(hours integer)',
    'create table owner(mention integer)',
    'create table roles(role text, mention integer)',
    'create table tz(time_zone text)',
    ]


def get_db_dir():
    """Checks whether the db directory exist, and gets its path.

    Returns:
        Path: the directory itself

    Raises:
        FileNotFoundError: if directory was not found

    """
    for path in ['db', '../db']:
        db_dir = Path(path)
        if db_dir.is_dir():
            return db_dir

    raise FileNotFoundError('No db directory detected!')


def rebuild_dbs(db_dir: Path):
    """Updates databases in a `db_dir`.

    This assumes the existing databases, if they exist at all, are valid.

    Args:
        db_dir (str): the location of the database files

    Returns:
        list of str: Exceptions

    """
    errs = []

    for db in db_dir.glob('*.db'):
        try:
            conn = sqlite3.connect(db.resolve())
            cursor = conn.cursor()
        except Exception as e:
            errs.append(db, e)
            print('Could not open file:', db)
            continue

        for query in queries_drop:
            try:
                cursor.execute(query)
            except Exception as e:
                print('Exception caught:', e, 'in', db)
                errs.append(db, query)

        for query in queries_create:
            try:
                cursor.execute(query)
            except Exception as e:
                print('Exception caught:', e, 'in', db)
                errs.append(db, query)

        conn.commit()
        conn.close()

    return errs

if __name__ == '__main__':
    errs = rebuild_dbs(get_db_dir()):
    if errs:
        print('Could not rebuild all. Check permissions.')
        print('\n-', '\n- '.join(errs))
    else:
        print('Successfully rebuilt all db\'s.')
