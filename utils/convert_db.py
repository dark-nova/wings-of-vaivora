import json
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


def get_ss_dir():
    """Checks whether the db directory exist, and gets its path.

    Returns:
        Path: the directory itself

    Raises:
        FileNotFoundError: if directory was not found

    """
    for path in ['server_settings', '../server_settings']:
        ss_dir = Path(path)
        if ss_dir.is_dir():
            return ss_dir

    raise FileNotFoundError('No server settings directory detected!')


def check_db_dir(parent: Path):
    """Checks whether the db directory exists.
    If not, create it.

    Args:
        parent (Path): the parent to both server_settings and db

    Returns:
        Path: the directory itself

    Raises:
        Exception: the db dir path exists, but it isn't a directory

    """
    db_dir = parent / 'db'
    if db_dir.exists() and not db_dir.is_dir():
        raise Exception(f"""{db_dir} exists, but it isn't a directory!""")
    elif not db_dir.exists():
        db_dir.mkdir()

    return db_dir


def update_db(db_dir: Path):
    """Updates databases in a `db_dir`.

    This assumes the existing databases, if they exist at all, are valid.

    Args:
        db_dir (Path): the location of the database files

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

    for db in db_dir.glob('*.db'):
        ss = Path(f"""{db.name.rstrip('.db')}.json""")
        if skips and db in skips:
            continue
        if not ss.exists():
            print(f'Server settings {ss.name} doesn\'t exist. Skipping...')
            errs.append(ss)
            continue

        try:
            with open(ss, 'r') as f:
                ssjson = json.load(f)
        except json.JSONDecodeError as e:
            print(f'Couldn\'t read JSON {ss.name}!', e)
            errs.append(ss)
            continue

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # Add users back to their assigned roles
        for role, user in ssjson['users'].items():
            # Don't add back super-authorized; let the bot handle this
            if role == 's-authorized':
                continue
            for _u in user:
                cursor.execute(
                    'insert into roles values(?, ?)',
                    (role, _u)
                    )

        conn.commit()

        # Add groups back to their assigned roles
        for role, group in ssjson['group'].items():
            if role == 's-authorized':
                continue
            for _g in group:
                cursor.execute(
                    'insert into roles values(?, ?)',
                    (role, _g)
                    )

        conn.commit()

        # Add only groups back to boss role
        for role, group in ssjson['role'].items():
            for _g in group:
                # In the old server settings, an '@' indicated a user mention
                if '@' in _g:
                    continue
                cursor.execute(
                    'insert into roles values(?, ?)',
                    (role, _g)
                    )

        conn.commit()

        # Add channels
        for ch_type, channels in ssjson['channel'].items():
            if ch_type == 'management':
                ch_type = 'settings'
            for channel in channels:
                cursor.execute(
                    'insert into channels values(?, ?)',
                    (ch_type, channel)
                    )

        conn.commit()

        # Add contribution points to guild
        for user, points in ssjson['talt'].items():
            if type(points) is not int:
                points = int(points)*20
            if user == 'guild':
                cursor.execute(
                    'insert into guild values(?, ?)',
                    (ssjson['guild_level'], points)
                    )
            elif user == 'remainder':
                cursor.execute(
                    'insert into contribution values(?, ?)',
                    ('0', points)
                    )
            else:
                cursor.execute(
                    'insert into contribution values(?,?)',
                    (user, points)
                    )

        conn.commit()
        conn.close()

    return errs


ss_dir = get_ss_dir()
db_dir = check_db_dir(ss_dir.parent)
errs = update_db(db_dir)
errs = transfer_data(db_dir, ss_dir)

if not errs:
    print('It is now safe to remove the server settings directory')