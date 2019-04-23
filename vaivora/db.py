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
    """Gets a _d_ata_b_ase _s_ignature of the table of a given `kind`.

    Args:
        kind (str): a `kind` of table, with an associated signature

    Returns:
        tuple: a tuple of str with column name and type
        separated by a space

    """
    return tuple('{} {}'
                 .format(*t) for t in zip(columns[kind], types[kind]))


async def construct_SQL(*, args):
    """Creates a SQLite statement.

    Args:
        args (tuple): the statements to use into one statement

    Returns:
        str: a full SQLite statement

    """
    return ' '.join(args)


async def construct_filters(*, filters):
    """Creates a compound SQLite filter in string form.

    Args:
        args (tuple): the filters

    Returns:
        str: a compound SQLite filter

    """
    return 'where {}'.format(' {} '.format('and').join(filters))


class Database:
    """Serves as the backend for all of the Vaivora modules."""

    def __init__(self, db_id: str):
        """Initializes the db module.

        Assigns a db file associated with the Discord guild.

        Args:
            db_id (str): the db id for the guild

        """
        self.db_id = db_id
        self.db_name = '{}{}{}'.format('db/', self.db_id, '.db')

    async def init_events(self):
        """Creates an events table if it doesn't exist.

        In addition, inserts permanent events if not present.

        Returns:
            bool: True if successful; False only if
            a fatal exception occurs

        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                await _db.execute(
                    'create table if not exists events({})'
                    .format(','.join(await get_dbs(kind))))
            except Exception as e:
                print('init_events', self.db_id, '\n', e)
                return False

            for event in permanent_events:
                try:
                    cursor = await _db.execute(
                        'select * from events where name = {}'
                        .format(event))
                    result = await cursor.fetchall()
                    if len(result) != 1:
                        raise Exception
                    else:
                        continue
                except:
                    # even if no event exists, this command will succed
                    await _db.execute(
                        'delete from events where name = "{}"'
                        .format(event))

                event_row = (event, 0, 0, 0) + event_times[event] + (0,)

                await _db.execute(
                    'insert into events values({})'
                    .format(','.join(str(col) for col in event_row)))

            await _db.commit()

        return True


    def get_id(self):
        """Gets the database id.

        Returns:
            str: this database id

        """
        return self.db_id

    async def create_all(self, owner_id):
        """Restores the entire db structure if it's corrupt.

        Will also attempt to update the 'super-authorized' role, using
        the current

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
        """Ceates a table when none (or invalid) exists.

        Args:
            kind (str): see `get_dbs`

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
                    print('check_if_vaild', self.db_id, '\n', e)
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
        """Checks the boss table using the arguments as filters.

        Args:
            bosses (list, optional): the bosses to check;
                defaults to `constants.boss.ALL_BOSSES`
            channel (int, optional): the map channel to filter;
                defaults to 0

        Returns:
            list: records
            list: None, if no records were found

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

    async def sort_db_boss_record(self, record):
        """Sorts the boss db records by descending chronological order.

        Args:
            record (list): the records to sort

        Returns:
            list: the sorted records

        """
        return sorted(record, key=itemgetter(5,6,7,8,9), reverse=True)

    async def update_db_boss(self, record):
        """Updates the boss table with a new entry.

        Args:
            record (dict): the boss record to add/update

        Returns:
            bool: True if successful; False otherwise

        """
        contents = []

        boss_name = record['name']
        boss_channel = record['channel']

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
                              == record['year']) and
                             (int(contents[0][6])
                              == record['month']) and
                             (int(contents[0][7])
                              == record['day'])and
                             (int(contents[0][8])
                              > record['hour'])):
                await cursor.close()
                return False
            elif contents and ((int(contents[0][5])
                                <= record['year']) or
                               (int(contents[0][6])
                                <= record['month']) or
                               (int(contents[0][7])
                                <= record['day']) or
                               (int(contents[0][8])
                                <= record['hour'])):
                if boss_channel:
                    await self.rm_entry_db_boss(bosses=[boss_name,],
                                                channel=boss_channel)
                else:
                    await self.rm_entry_db_boss(bosses=[boss_name,])

            try:
                # boss database structure
                await _db.execute(
                    'insert into boss values (?,?,?,?,?,?,?,?,?,?)',
                    (str(boss_name),
                     int(boss_channel),
                     str(record['map']),
                     str(record['status']),
                     str(record['text_channel']),
                     int(record['year']),
                     int(record['month']),
                     int(record['day']),
                     int(record['hour']),
                     int(record['minute'])))
                await _db.commit()
                return True
            except Exception as e:
                print('update_db_boss', self.db_id, '\n', e)
                return False

    async def rm_entry_db_boss(self, bosses=constants.boss.ALL_BOSSES, channel=0):
        """Removes records filtered by the arguments.

        Args:
            bosses (list, optional): list of boss names (str) to filter;
                defaults to `constants.boss.ALL_BOSSES`
            channel (int, optional): the map channel to filter;
                defaults to 0

        Returns:
            list: a list containing the records that were removed

        """
        records = []
        if not bosses:
            bosses = constants.boss.ALL_BOSSES

        async with aiosqlite.connect(self.db_name) as _db:
            _db.row_factory = aiosqlite.Row

            for boss in bosses:
                conditions = ('boss where name = "{}"'
                               .format(boss))
                if channel:
                    conditions += (' and channel = "{}"'
                                   .format(channel))

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
                    print('rm_entry_db_boss', self.db_id, '\n', e)
                    continue
            await cursor.close()

        return records # return an implicit bool for how many were deleted

    async def get_users(self, role, users=None):
        """Gets users by filtering from arguments.

        Users are defined to be either Discord Members or Roles,
        hence why the function isn't called "get_members".

        Args:
            role (str): the Vaivora role to filter
            users (list, optional): a list of optional users to filter results;
                defaults to None

        Returns:
            list: a list of users by id
            None: if no such users were configured

        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute(
                            'select mention from roles where role = "{}"'
                            .format(role))
                results = [_row[0] for _row in await cursor.fetchall()]

                if users:
                    results = [result for result in results if result in users]

                return results
            except Exception as e:
                print(e)
                return None

    async def set_users(self, role, users):
        """Sets users to a Vaivora role.

        Users are defined to be either Discord Members or Roles,
        hence why the function isn't called "set_members".

        Note that individual users cannot be assigned the boss role.

        Args:
            role (str): the role of user desired
            users (list): the users to set

        Returns:
            list: a list of users not processed

            If all users were successfullly processed,
            a list of None will be returned instead.

        """
        errs = []
        async with aiosqlite.connect(self.db_name) as _db:
            for user in users:
                try:
                    cursor = await _db.execute(
                                """insert into roles values
                                   ('{}', '{}')"""
                                .format(role, user))
                except Exception as e:
                    await _db.execute('ROLLBACK')
                    print('set_users', self.db_id, '\n', e)
                    errs.append(user)
                    continue
            await _db.commit()
        return errs

    async def remove_users(self, role, users):
        """Removes users from a Vaivora role.

        Users are defined to be either Discord Members or Roles,
        hence why the function isn't called "remove_members".

        Args:
            role (str): the role of user desired
            users (list): the users to set

        Returns:
            list: a list of users not processed

            If all users were successfullly processed,
            a list of None will be returned instead.

        """
        errs = []
        async with aiosqlite.connect(self.db_name) as _db:
            for user in users:
                try:
                    cursor = await _db.execute(
                                """delete from roles where role='{}'
                                   and mention='{}'"""
                                .format(role, user))
                except Exception as e:
                    await _db.execute('ROLLBACK')
                    print('remove_users', self.db_id, '\n', e)
                    errs.append(user)
                    continue
            await _db.commit()
        return errs

    async def update_user_sauth(self, user_id: int, owner=True):
        """Updates the current guild owner to `s`uper-`auth`orized.

        Also used to update bot owner to 'super-authorized'.

        Args:
            user_id (int): the id of the user
            owner (bool, optional): whether the user is the guild owner;
                defaults to True

        Returns:
            bool: True if successful; False otherwise

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
                    #print('Exception caught & ignored:', self.db_id, '\n', e)
                    pass

                try:
                    await _db.execute('create table owner(id text)')
                except: #Exception as e:
                    # table owner might already exist
                    #print('Exception caught & ignored:', self.db_id, '\n', e)
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
                print('Exception caught:', self.db_id, '\n', e)
                return False

    async def clean_duplicates(self):
        """Removes duplicates from all tables.

        Returns:
            list: containing table names that could not be cleaned

            If all tables were successfully processed,
            a list of None will be returned instead.

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
                    print('clean_duplicates', self.db_id, '\n', e)
                    continue
            await _db.commit()
        return errs

    async def purge(self):
        """Resets the channels table as a last resort.

        Used if no channels can be used for commands due to configuration
        malfunction.

        Returns:
            bool: True if successful; False otherwise

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
        """Gets channel(s) of a given `kind`, or Vaivora channel.

        Args:
            kind (str): the kind of channel to filter;
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
            bool: True if successful; False otherwise

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
                print('set_channel', self.db_id, '\n', e)
                return False

    async def remove_channel(self, kind, channel):
        """Removes a channel from `kind`.

        Args:
            kind (str): the kind of channel to filter;
                e.g. 'boss', 'management'
            channel (int): the id of a channel to remove

        Returns:
            bool: True if successful; False otherwise

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
                print('remove_channel', self.db_id, '\n', e)
                return False

    async def get_contribution(self, users=None):
        """
        :func:`get_contribution` gets contribution.

        Args:
            users (list, optional): a list of users to filter results;
                defaults to None

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
        """Sets a user contribution using points as the unit.

        Args:
            user (int): the user to set contributions
            points (int): the points of contribution
            append (bool. optional): whether to add instead of set;
                defaults to False

        Returns:
            bool: True if successful; False otherwise

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
                print('set_contribution', self.db_id, '\n', e)
                return False

    async def get_guild_info(self):
        """Retrieves guild level and points.

        Returns:
            tuple: (guild level: int, guild points: int)
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
        """Sets the guild points by rebasing points.

        This should be used last, after inputting records.

        Args:
            points (int): the points of the guild

        Returns:
            bool: True if successful; False otherwise

        """
        level = 1
        while constants.settings.G_LEVEL[level] < points:
            level += 1

        async with aiosqlite.connect(self.db_name) as _db:
            try:
                # use sentinel value 0 for "remaining",
                # unattributable points
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
            except Exception as e:
                print('set_guild_points', self.db_id, '\n', e)
                await _db.execute('ROLLBACK')
                return False

    async def get_tz(self):
        """Retrieves the guild's time zone.

        Returns:
            str: the time zone e.g America/New_York

        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute('select * from tz')
                return (await cursor.fetchone())[0]
            except Exception as e:
                print('get_tz', self.db_id, '\n', e)
                await _db.execute('drop table if exists tz')
                await self.create_db('tz')
                return None

    async def set_tz(self, tz: str):
        """Sets the guild's time zone to use for records.

        Args:
            tz (str): the time zone to use

        Returns:
            bool: True if successful; False otherwise

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
            except Exception as e:
                print('set_tz', self.db_id, '\n', e)
                return False

    async def get_offset(self):
        """Retrieves the guild's offset from the time zone.

        Returns:
            int: the offset
            None: if no offset was found

        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute('select * from offset')
                return (await cursor.fetchone())[0]
            except Exception as e:
                print('get_offset', self.db_id, '\n', e)
                return None

    async def set_offset(self, offset: int):
        """Sets the guild's offset from time zone.

        Args:
            offset (int): the offset to use

        Returns:
            bool: True if successful; False otherwise

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
            except Exception as e:
                print('set_offset', self.db_id, '\n', e)
                return False

    async def add_custom_event(self, name: str, date: dict, time: dict):
        """Adds a custom event to timers.

        If an event with the same name already exists,
        the command fails.

        Args:
            name (str): the name of the event to add
            date (dict): with year, month, day; the ending date
            time (dict): with hour, minutes; the ending time

        Returns:
            bool: True if successful; False otherwise

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
                print('add_custom_event', self.db_id, '\n', e)
                return False
            except Exception as e:
                print('add_custom_event', 'unknown exception:', self.db_id, '\n', e)
                return False

    async def verify_existing_custom_event(self, name: str):
        """Verifies whether an event already exists.

        Called prior to updating a custom event.

        If the event did not exist already, the command fails.
        Otherwise, the existing event is destroyed and the command proceeds.

        Args:
            name (str): the name of the event to check

        Returns:
            bool: True if successful; False otherwise

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
            except Exception as e:
                print('verify_existing_custom_event', self.db_id, '\n', e)
                return False

    async def del_custom_event(self, name: str):
        """Deletes a custom event from timers.

        Note that the command will successfully run even if
        nothing was deleted.

        Args:
            name (str): the name of the event to delete;
                MUST MATCH EXISTING - case/punctuation sensitive

        Returns:
            bool: True if successful; False otherwise

        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                await _db.execute(
                    'delete from events where name = "{}"'
                    .format(name)
                    )
                return True
            except Exception as e:
                print('del_custom_event', self.db_id, '\n', e)
                return False

    async def toggle_event(self, name: str, toggle: int):
        """Toggles permanent event states.

        Called by `enable_event` and `disable_event`.

        Args:
            name (str): the name of the permanent event to use
            toggle (int): the toggle state, 1 being enabled; 0 disabled

        Returns:
            bool: True if successful; False otherwise

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
                print(toggle_name, self.db_id, '\n', e)
                return False

    async def enable_event(self, name: str):
        """Enables a permanent in-game event timer.

        Note that this function makes no attempt to check
        the previous state of the event.

        Permanent event dates will use dummy values.

        Args:
            name (str): the name of the permanent event to use

        Returns:
            bool: True if successful; False otherwise

        """
        return await self.toggle_event(name, 1)

    async def disable_event(self, name: str):
        """Disables a permanent in-game event timer.

        Note that this function makes no attempt to check
        the previous state of the event.

        Args:
            name (str): the name of the permanent event to use

        Returns:
            bool: True if successful; False otherwise

        """
        return await self.toggle_event(name, 0)

    async def list_all_events(self):
        """Retrieves all events, custom or permanent.

        Custom event timers will show time remaining.
        Permanent events may do the same, if they are enabled.

        The state of all permanent event timers will be listed as well.

        Returns:
            list: of tuples (event name, date and time, enabled/disabled)
            bool: False if unsuccessful

        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute('select * from events')
                return await cursor.fetchall()
            except Exception as e:
                print('list_all_events', self.db_id, '\n', e)
                return False
