import sqlite3

import asyncio
import aiosqlite
from operator import itemgetter

import constants.settings
import constants.boss

columns = {}
columns['boss'] = (
    'name',
    'channel',
    'map',
    'status',
    'text_channel',
    'year',
    'month',
    'day',
    'hour',
    'minute'
    )

columns['roles'] = (
    'role',
    'mention'
    )

columns['channels'] = (
    'type',
    'channel'
    )

columns['guild'] = (
    'level',
    'points'
    )

columns['contribution'] = (
    'mention',
    'points'
    )

columns['offset'] = (
    'hours',
    )

columns['tz'] = (
    'time_zone',
    )

columns['events'] = (
    'name',
    'year',
    'month',
    'day',
    'hour',
    'minutes',
    'enabled'
    )

types = {}
types['boss'] = (
    # ('text', 'integer')
    # + ('text',)*3
    # + ('integer',)*5
    'text',
    'integer',
    'text',
    'text',
    'text',
    'integer',
    'integer',
    'integer',
    'integer',
    'integer',
    )

types['roles'] = (
    'text',
    'integer'
    )

types['guild'] = (
    # ('integer',)*2
    'integer',
    'integer'
    )

types['contribution'] = (
    'integer',
    'integer'
    )

types['channels'] = types['contribution']

types['offset'] = (
    'integer',
    )

types['tz'] = (
    'text',
    )

types['events'] = (
    'text',
    'integer',
    'integer',
    'integer',
    'integer',
    'integer',
    'integer'
    )

tables = [
    'boss',
    'roles',
    'guild',
    'contribution',
    'channels',
    'offset',
    'tz',
    'events'
    ]

tables_to_clean = [
    'roles',
    'channels',
    'contribution'
    ]

spec = {}
spec['roles'] = 'role, mention'
spec['channels'] = 'type, channel'
spec['contribution'] = 'mention, points'

permanent_events = [
    'Boruta',
    'Guild Territory War',
    'Irredian Shelter'
    ]

event_times = {}
event_times[permanent_events[0]] = (19, 0)
event_times[permanent_events[1]] = (20, 0)
event_times[permanent_events[2]] = (0, 0)

dummy_dates = (0, 0, 0)


async def get_dbs(kind):
    """
    :func:`get_dbs` returns a _d_ata_b_ase _s_ignature
    of the table of a given `kind`.

    Args:
        kind (str): to generate a table signature

    Returns:
        tuple: a tuple of tuples with (field name, sql type)
    """
    return tuple('{} {}'
                 .format(*t) for t in zip(columns[kind], types[kind]))


async def construct_SQL(*, args):
    """
    :func:`construct_SQL` creates a SQLite statement.

    Args:
        args (tuple): the statements to use into one statement

    Returns:
        str: a full SQLite statement
    """
    return ' '.join(args)


async def construct_filters(*, filters):
    """
    :func:`construct_filters` creates a compound SQLite filter
    in string form.

    Args:
        args (tuple): the filters

    Returns:
        str: a compound SQLite filter
    """
    return 'where {}'.format(' {} '.format('and').join(filters))


class Database:
    """:class:`Database` serves as the backend for all of the Vaivora modules."""

    def __init__(self, db_id: str):
        """
        :func:`__init__` initializes the db module.

        Args:
            db_id (str): the db id for the guild
        """
        self.db_id = db_id
        self.db_name = '{}{}{}'.format('db/', self.db_id, '.db')

    def get_id(self):
        """
        :func:`get_id` returns the database id.

        Returns:
            str: this database id
        """
        return self.db_id

    async def create_all(self, owner_id):
        """
        :func:`create_all` restores the entire db structure if it's corrupt.

        Args:
            owner_id (int): the guild owner's id
        """
        async with aiosqlite.connect(self.db_name) as _db:
            for table in tables:
                await _db.execute('drop table if exists {}'.format(table))
                await _db.execute('create table {}({})'
                                  .format(table,
                                          ','.join(await get_dbs(table))))
                await _db.commit()
        await self.update_user_sauth(owner_id)

        return

    async def create_db(self, kind):
        """
        :func:`create_db` creates a db when none (or invalid) exists,
        on the spec for `kind`.

        Args:
            kind (str): see :func:`get_dbs`
        """
        async with aiosqlite.connect(self.db_name) as _db:
            await _db.execute('drop table if exists {}'.format(kind))
            await _db.execute('create table {}({})'
                              .format(kind,
                                      ','.join(await get_dbs(kind))))
            await _db.commit()
        return

    async def check_if_valid(self, module):
        """
        :func:`check_if_valid_boss` checks if the database is valid.

        Args:
            module (str): the module name

        Returns:
            bool: True if valid; False otherwise
        """
        if module == 'boss':
            select = tables[0:1]
        elif module == 'settings':
            select = tables[1:]

        async with aiosqlite.connect(self.db_name) as _db:
            _db.row_factory = aiosqlite.Row
            for _s in select:
                try:
                    cursor = await _db.execute(
                                await construct_SQL(
                                    args=('select * from',
                                          _s)))
                except Exception as e:
                    print('check_if_vaild', e)
                    return False

                r = await cursor.fetchone()
                if not r:
                    await cursor.close()
                    return True

                if sorted(tuple(r.keys())) != sorted(columns[_s]):
                    await cursor.close()
                    print(r.keys(), sorted(columns[_s]))
                    return False

            await cursor.close()
        return True

    async def check_db_boss(self, bosses=constants.boss.ALL_BOSSES, channel=0):
        """
        :func:`check_db_boss` checks the database for the conditions in argument

        Args:
            bosses (list): (default: constants.boss.ALL_BOSSES) the bosses to check
            channel (int): (default: 0) channels to filter

        Returns:
            list: records or list of None
        """
        db_record = []
        async with aiosqlite.connect(self.db_name) as _db:
            _db.row_factory = aiosqlite.Row
            for boss in bosses:
                if channel:
                    cursor = await _db.execute(
                                await construct_SQL(
                                    args=('select * from boss',
                                          await construct_filters(filters=
                                                ('name=?',
                                                 'channel=?')))),
                                               (boss, channel,))
                else:
                    cursor = await _db.execute(
                                await construct_SQL(
                                    args=('select * from boss',
                                          await construct_filters(filters=(
                                                'name=?',)))),
                                               (boss,))

                records = await cursor.fetchall()
                for record in records:
                    db_record.append(tuple(record))

            await cursor.close()
        return await self.sort_db_boss_record(db_record)

    async def sort_db_boss_record(self, db_record):
        """
        :func:`sort_db_record` sorts the db records
        by chronological order, for bosses.

        Args:
            db_record (list): the records to sort

        Returns:
            list: the sorted records
        """
        return sorted(db_record, key=itemgetter(5,6,7,8,9), reverse=True)

    async def update_db_boss(self, boss_dict):
        """
        :func:`update_db_boss` updates the record with a new entry.

        Args:
            boss_dict (dict): the boss dictionary
                containing the new record

        Returns:
            bool: True if successful; False otherwise
        """
        contents = []

        boss_name = boss_dict['name']
        boss_channel = boss_dict['channel']

        # handle channels
        if boss_channel:
            sel_statement = await construct_SQL(
                                args=('select * from boss',
                                      await construct_filters(
                                            filters=(
                                                'name=?',
                                                'channel=?'))))
            sql_condition = (boss_name, boss_channel)
        # handle everything else
        else:
            sel_statement = await construct_SQL(
                                args=('select * from boss',
                                      await construct_filters(
                                            filters=(
                                                'name=?',))))
            sql_condition = (boss_name,)

        async with aiosqlite.connect(self.db_name) as _db:
            _db.row_factory = aiosqlite.Row

            cursor = await _db.execute(sel_statement, sql_condition)
            contents.extend(await cursor.fetchall())

            if contents and ((int(contents[0][5])
                              == boss_dict['year']) and
                             (int(contents[0][6])
                              == boss_dict['month']) and
                             (int(contents[0][7])
                              == boss_dict['day'])and
                             (int(contents[0][8])
                              > boss_dict['hour'])):
                await cursor.close()
                return False
            elif contents and ((int(contents[0][5])
                                <= boss_dict['year']) or
                               (int(contents[0][6])
                                <= boss_dict['month']) or
                               (int(contents[0][7])
                                <= boss_dict['day']) or
                               (int(contents[0][8])
                                <= boss_dict['hour'])):

                if boss_channel:
                    await self.rm_entry_db_boss(boss_list=[boss_name,],
                                                boss_ch=boss_channel)
                else:
                    await self.rm_entry_db_boss(boss_list=[boss_name,])

            try:
                # boss database structure
                await _db.execute(
                    'insert into boss values (?,?,?,?,?,?,?,?,?,?)',
                    (str(boss_name),
                     int(boss_channel),
                     str(boss_dict['map']),
                     str(boss_dict['status']),
                     str(boss_dict['text_channel']),
                     int(boss_dict['year']),
                     int(boss_dict['month']),
                     int(boss_dict['day']),
                     int(boss_dict['hour']),
                     int(boss_dict['minute'])))
                await _db.commit()
                return True
            except Exception as e:
                print('update_db_boss', e)
                return False

    async def rm_entry_db_boss(self, boss_list=constants.boss.ALL_BOSSES, boss_ch=0):
        """
        :func:`rm_entry_db_boss` removes records based on
        the conditions supplied.

        Args:
            boss_list (list): the list containing boss names (str)
                with records to erase
            boss_ch (int): (default: 0) the boss channel filter,
                if specified

        Returns:
            list: a list containing the records that were removed
        """
        records = []
        if not boss_list:
            boss_list = constants.boss.ALL_BOSSES

        async with aiosqlite.connect(self.db_name) as _db:
            _db.row_factory = aiosqlite.Row

            for boss in boss_list:
                conditions = ('boss where name = "{}"'
                               .format(boss))
                if boss_ch:
                    conditions += (' and channel = "{}"'
                                   .format(boss_ch))

                select = 'select * from ' + conditions
                delete = 'delete from ' + conditions

                cursor = await _db.execute(select)
                results = await cursor.fetchall()

                # no records to delete
                if len(results) == 0:
                    continue

                try:
                    await cursor.execute(delete)
                    await _db.commit()
                    records.append(boss) # guaranteed to be only one entry as per this loop
                except Exception as e: # in case of sqlite3 exceptions
                    print('rm_entry_db_boss', self.db_id, e)
                    continue
            await cursor.close()

        return records # return an implicit bool for how many were deleted

    async def get_users(self, kind, users=None):
        """
        :func:`get_users` gets users of a `kind`.
        Users are defined to be either Discord Members or Roles,
        hence not using "get_members" as the function name.

        Args:
            kind (str): the kind of user desired
            users: (default: None) a list of optional users to filter results

        Returns:
            list: a list of users by id
            None: if no such users were configured
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute(
                            'select mention from roles where role = "{}"'
                            .format(kind))
                results = [_row[0] for _row in await cursor.fetchall()]

                if users:
                    results = [result for result in results if result in users]

                return results
            except Exception as e:
                print(e)
                return None

    async def set_users(self, kind, users):
        """
        :func:`set_users` sets users to a `kind` of role.
        Users are defined to be either Discord Members or Roles,
        hence not using "get_members" as the function name.

        Args:
            kind (str): the kind of user desired
            users (list): the users to set

        Returns:
            list: a list of users not processed
            list(None): if successful
        """
        errs = []
        async with aiosqlite.connect(self.db_name) as _db:
            for user in users:
                try:
                    cursor = await _db.execute(
                                """insert into roles values
                                   ('{}', '{}')"""
                                .format(kind, user))
                except Exception as e:
                    await _db.execute('ROLLBACK')
                    print('set_users', e)
                    errs.append(user)
                    continue
            await _db.commit()
        return errs

    async def remove_users(self, kind, users):
        """
        :func:`remove_users` removes users from a `kind` of role.
        Users are defined to be either Discord Members or Roles,
        hence not using "remove_members" as the function name.

        Args:
            kind (str): the kind of user desired
            users (list): the users to set

        Returns:
            list: a list of users not processed
            list(None): if successful
        """
        errs = []
        async with aiosqlite.connect(self.db_name) as _db:
            for user in users:
                try:
                    cursor = await _db.execute(
                                """delete from roles where role='{}'
                                   and mention='{}'"""
                                .format(kind, user))
                except Exception as e:
                    await _db.execute('ROLLBACK')
                    print('remove_users', e)
                    errs.append(user)
                    continue
            await _db.commit()
        return errs

    async def update_user_sauth(self, user_id: int, owner=True):
        """
        :func:`update_user_sauth` updates owner to `s`uper `auth`orized
        after each boot.

        Args:
            user_id (int): the id of the owner
            owner: (default: True) optional: True if owner

        Returns:
            True if successful; False otherwise
        """
        async with aiosqlite.connect(self.db_name) as _db:
            if owner:
                try:
                    cursor = await _db.execute('select * from owner')
                    old_owner = (await cursor.fetchone())[0]
                    if user_id == old_owner:
                        return True # do not do anything if it's the same owner
                    await _db.execute('delete from owner')
                    await _db.execute("""delete from roles where
                                         role = '{}' and
                                         mention = '{}'"""
                        .format(constants.settings.ROLE_SUPER_AUTH,
                                old_owner))
                except: #Exception as e:
                    #print('Exception caught & ignored:', e)
                    pass

                try:
                    await _db.execute('create table owner(id text)')
                except: #Exception as e:
                    # table owner might already exist
                    #print('Exception caught & ignored:', e)
                    pass

            try:
                if owner:
                    await _db.execute('insert into owner values("{}")'
                                      .format(user_id))
                await _db.execute('insert into roles values("{}", "{}")'
                                  .format(constants.settings.ROLE_AUTH,
                                          user_id))
                await _db.execute('insert into roles values("{}", "{}")'
                                  .format(constants.settings.ROLE_SUPER_AUTH,
                                          user_id))
                await _db.commit()
                return True
            except Exception as e:
                await _db.execute('ROLLBACK')
                print('Exception caught:', e)
                return False

    async def clean_duplicates(self):
        """
        :func:`clean_duplicates` gets rid of duplicates from all tables.

        Returns:
            list: containing table names that could not be cleaned, or
                None if all tables could be cleaned
        """
        errs = []
        async with aiosqlite.connect(self.db_name) as _db:
            for _table in tables_to_clean:
                try:
                    await _db.execute("""delete from {0} where rowid not in
                                         (select min(rowid) from {0} group by {1})"""
                                      .format(_table, spec[_table]))
                except Exception as e:
                    errs.append(_table)
                    print('clean_duplicates', e)
                    continue
            await _db.commit()
        return errs

    async def purge(self):
        """
        :func:`purge` is a last-resort subcommand that
        resets the channels table.

        Args:
            guild_id (int): the id of the guild to purge tables

        Returns:
            True if successful; False otherwise
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                await _db.execute('drop table if exists channels')
                await _db.commit()
                await _db.execute(
                    'create table channels(type text, channel integer)')
                await _db.commit()
                return True
            except Exception as e:
                await _db.execute('ROLLBACK')
                print(e)
                return False

    async def get_channel(self, kind):
        """
        :func:`get_channel` gets channel(s) of a given `kind`.

        Args:
            kind (str): the kind of channel to filter
                e.g. 'boss', 'management'

        Returns:
            list: a list of channels of `kind`
            None: if no such channels were configured
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute(
                            """select channel from channels
                            where type = '{}'"""
                            .format(kind))
                return [_row[0] for _row in await cursor.fetchall()]
            except Exception as e:
                print(e)
                return None

    async def set_channel(self, kind, channel):
        """
        :func:`set_channel` adds a channel as a `kind`

        Args:
            kind (str): the kind of channel to filter
                e.g. 'boss', 'management'
            channel (int): the id of a channel to set

        Returns:
            True if successful; False otherwise
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                await _db.execute(
                    'insert into channels values("{}", "{}")'
                    .format(kind, channel))
                await _db.commit()
                return True
            except Exception as e:
                await _db.execute('ROLLBACK')
                print('set_channel', e)
                return False

    async def remove_channel(self, kind, channel):
        """
        :func:`remove_channel` removes a channel from `kind`.

        Args:
            kind (str): the kind of channel to filter
                e.g. 'boss', 'management'
            channel (int): the id of a channel to remove

        Returns:
            True if successful; False otherwise
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                await _db.execute(
                    'delete from channels where type="{}" and channel="{}"'
                    .format(kind, channel))
                await _db.commit()
                return True
            except Exception as e:
                await _db.execute('ROLLBACK')
                print('remove_channel', e)
                return False

    async def get_contribution(self, users=None):
        """
        :func:`get_contribution` gets contribution.

        Args:
            users: (default: None) an optional list of users to retrieve

        Returns:
            list: of tuples, containing user id and contribution points
            None: if none exist
        """
        results = []
        async with aiosqlite.connect(self.db_name) as _db:
            if not users:
                try:
                    cursor = await _db.execute(
                                """select * from contribution
                                   where mention != '0'""")
                    return await cursor.fetchall()
                except:
                    return None
            else:
                for user in users:
                    try:
                        cursor = await _db.execute(
                                    """select * from contribution
                                       where mention = '{}'"""
                                    .format(user))
                        results.append(
                            await cursor.fetchone())
                    except:
                        pass
                        print('get_contribution', 'skipped', user)
                return results

    async def set_contribution(self, user, points, append=False):
        """
        :func:`set_contribution` sets a user contribution.

        Args:
            user (int): the user to set contributions
            points (int): the points of contribution
            append (bool): (default: False) whether to add or not

        Returns:
            True if successful; False otherwise
        """
        g_level = 0
        g_points = 0

        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute(
                            """select points from contribution
                               where mention = '{}'"""
                            .format(user))
                old_points = (await cursor.fetchone())[0]

                if append:
                    points += old_points
            except:
                pass # the record may not exist; ignore if it doesn't

            try:
                cursor = await _db.execute('select * from guild')
                g_level, g_points = await cursor.fetchone()
                g_points -= old_points
                while constants.settings.G_LEVEL[g_level] > g_points:
                    g_level -= 1
                await _db.execute('delete from guild')
            except:
                pass # the guild record may not exist

            try:
                await _db.execute(
                    'delete from contribution where mention = "{}"'
                    .format(user))
            except:
                pass # the record may not exist; ignore if it doesn't

            try:
                await _db.execute(
                    'insert into contribution values("{}", "{}")'
                    .format(user, points))
                await _db.commit()

                g_points += points
                while constants.settings.G_LEVEL[g_level] < g_points:
                    g_level += 1

                await _db.execute('insert into guild values("{}", "{}")'
                                  .format(g_level, g_points))
                await _db.commit()
                return True
            except Exception as e:
                await _db.execute('ROLLBACK')
                print(e)
                return False

    async def get_guild_info(self):
        """
        :func:`get_guild_info` returns guild level and points.

        Returns:
            tuple: (guild level, guild points)
            None: if unsuccessful
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute(
                            'select * from guild')
                return await cursor.fetchone()
            except:
                return None

    async def set_guild_points(self, points):
        """
        :func:`set_guild_points` sets the guild info by rebasing points.
        This should be used last, after inputting records.

        Args:
            points (int): the points of the guild

        Returns:
            True if successful; False otherwise
        """
        level = 1
        while constants.settings.G_LEVEL[level] < points:
            level += 1

        async with aiosqlite.connect(self.db_name) as _db:
            try:
                # use sentinel value 0 for "remaining"
                cursor = await _db.execute(
                            """select points from contribution
                               where mention != '0'""")
                g_points = sum(await cursor.fetchall())
                extra_points = points - g_points
            except:
                extra_points = points

            if extra_points < 0:
                return False

            try:
                await _db.execute(
                    """delete from contribution
                       where mention = '0'""")
            except:
                pass

            try:
                await _db.execute('delete from guild')
            except:
                await _db.execute('ROLLBACK')

            try:
                await _db.execute(
                        """insert into contribution values
                           ('{}', '{}')"""
                        .format(0, extra_points))
                await _db.execute(
                        """insert into guild values
                           ('{}', '{}')"""
                        .format(level, points))
                await _db.commit()
                return True
            except:
                await _db.execute('ROLLBACK')
                return False

    async def get_tz(self):
        """
        :func:`get_tz` gets the guild's time zone.

        Returns:
            str: the time zone e.g America/New_York
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute('select * from tz')
                return (await cursor.fetchone())[0]
            except:
                await _db.execute('drop table if exists tz')
                await self.create_db('tz')
                return None

    async def set_tz(self, tz: str):
        """
        :func:`set_tz` sets the guild's time zone to use for records.

        Args:
            tz (str): the time zone to use

        Returns:
            True if successful; False otherwise
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute('select * from tz')
                existing = await cursor.fetchone()
                if existing:
                    await _db.execute('delete from tz')
            except:
                await _db.execute('drop table if exists tz')
                await self.create_db('tz')

            try:
                await _db.execute('insert into tz values("{}")'
                                  .format(tz))
                await _db.commit()
                return True
            except:
                return False

    async def get_offset(self):
        """
        :func:`get_offset` gets the guild's offset from the time zone.

        Returns:
            str: the time zone e.g America/New_York
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute('select * from offset')
                return (await cursor.fetchone())[0]
            except:
                return None

    async def set_offset(self, offset: int):
        """
        :func:`set_offset` sets the guild's offset from time zone
        to use for records.

        Args:
            offset (int): the offset to use

        Returns:
            True if successful; False otherwise
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute('select * from offset')
                existing = await cursor.fetchone()
                if existing:
                    await _db.execute('delete from offset')
            except:
                await _db.execute('drop table if exists offset')
                await self.create_db('offset')

            try:
                await _db.execute('insert into offset values("{}")'
                                  .format(offset))
                await _db.commit()
                return True
            except:
                return False

    async def add_custom_event(self, name: str, date: dict, time: dict):
        """
        :func:`add_custom_event` adds a custom event to timers.
        If an event already exists, the command fails.

        Args:
            name (str): the name of the event to add
            date (dict): with year, month, day; the ending date
            time (dict): with hour, minutes; the ending time

        Returns:
            True if successful; False otherwise
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute(
                    'select * from events where name = "{}"'
                    .format(name)
                    )
                existing = await cursor.fetchone()
                if existing:
                    return False

                cursor = await _db.execute(
                    'select count(name) from events'
                    )
                event_count = (await cursor.fetchone())[0]
                if event_count >= 15:
                    return False
            except sqlite3.OperationalError as e:
                await self.create_db('events')
                print('add_custom_event', e)
                return False
            except Exception as e:
                print('add_custom_event', 'unknown exception:', e)
                return False

    async def verify_existing_custom_event(self, name: str):
        """
        :func:`verify_existing_custom_event` is called prior to updating
        a custom event.
        If the event did not exist already, the command fails.
        Otherwise, the existing event is destroyed and the command proceeds.

        Args:
            name (str): the name of the event to check

        Returns:
            True if successful; False otherwise
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute(
                    'select * from events where name = "{}"'
                    .format(name)
                    )
                existing = await cursor.fetchone()
                if existing:
                    await _db.execute(
                        'delete from events where name = "{}"'
                        .format(name)
                        )
                    await _db.commit()
                    return True
                else:
                    return False
            except sqlite3.OperationalError:
                await self.create_db('events')
                return False
            except:
                return False

    async def del_custom_event(self, name: str):
        """
        :func:`del_custom_event` deletes a custom event from timers.
        Note that the command will successfully run even if
        nothing was deleted.

        Args:
            name (str): the name of the event to delete; MUST MATCH EXISTING

        Returns:
            True if successful; False otherwise
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                await _db.execute(
                    'delete from events where name = "{}"'
                    .format(name)
                    )
                return True
            except Exception as e:
                print('del_custom_event', e)
                return False

    async def toggle_event(self, name: str, toggle: int):
        """
        :func:`toggle_event` handles the logic for:
            :func:`enable_event`
            :func:`disable_event`

        Args:
            name (str): the name of the permanent event to use
            toggle (int): the toggle state, 1 being enabled; 0 disabled

        Returns:
            True if successful; False otherwise
        """
        toggle_name = 'enable_event' if toggle != 0 else 'disable_event'
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                await _db.execute(
                    'delete from events where name = "{}"'
                    .format(name)
                    )
                await _db.commit(
                    'insert into events({} {} {} {} {} {} {})'
                    .format(name, *dummy_dates, *event_times[name], toggle))
                await _db.commit()
                return True
            except Exception as e:
                print(toggle_name, e)
                return False

    async def enable_event(self, name: str):
        """
        :func:`enable_event` enables a permanent in-game event timer.
        Note that this function makes no attempt to check the previous state
        of the event.
        Permanent event dates will use dummy values.

        Args:
            name (str): the name of the permanent event to use

        Returns:
            True if successful; False otherwise
        """
        return await self.toggle_event(name, 1)

    async def disable_event(self, name: str):
        """
        :func:`disable_event` disables a permanent in-game event timer.
        Note that this function makes no attempt to check the previous state
        of the event.

        Args:
            name (str): the name of the permanent event to use

        Returns:
            True if successful; False otherwise
        """
        return await self.toggle_event(name, 0)

    async def list_all_events(self):
        """
        :func:`list_all_events` prints all events custom or permanent.
        Custom event timers will show time remaining.
        Permanent events may do the same, if they are enabled.
        The state of all permanent event timers will be listed as well.

        Returns:
            list: of tuples (event name, date and time, enabled/disabled)
            False if unsuccessful
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute('select * from events')
                return await cursor.fetchall()
            except Exception as e:
                print('list_all_events', e)
                return False
