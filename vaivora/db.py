import asyncio
import aiosqlite
from operator import itemgetter

import constants.settings
import constants.boss
import constants.db
# from constants.settings import en_us as lang_settings
# from constants.boss import en_us as lang_boss
# from constants.db import en_us as lang_db

columns = {}
columns[constants.db.SQL_FROM_BOSS] = (
    constants.db.COL_BOSS_NAME,
    constants.db.COL_BOSS_CHANNEL,
    constants.db.COL_BOSS_MAP,
    constants.db.COL_BOSS_STATUS,
    constants.db.COL_BOSS_TXT_CHANNEL,
    constants.db.COL_TIME_YEAR,
    constants.db.COL_TIME_MONTH,
    constants.db.COL_TIME_DAY,
    constants.db.COL_TIME_HOUR,
    constants.db.COL_TIME_MINUTE
    )

columns[constants.db.SQL_FROM_ROLES] = (
    constants.db.COL_SETS_ROLES
    )

columns[constants.db.SQL_FROM_CHANS] = (
    constants.db.COL_SETS_CHANS
    )

columns[constants.db.SQL_FROM_GUILD] = (
    constants.db.COL_SETS_GUILD
    )

columns[constants.db.SQL_FROM_CONTR] = (
    constants.db.COL_SETS_CONTR
    )

columns[constants.db.SQL_FROM_OFFSET] = (
    constants.db.COL_SETS_OFFSET
    )

types = {}
types[constants.db.SQL_FROM_BOSS] = ((constants.db.SQL_TYPE_TEXT,
                                 constants.db.SQL_TYPE_INT,)
                                + (constants.db.SQL_TYPE_TEXT,)*3
                                + (constants.db.SQL_TYPE_INT,)*5)

types[constants.db.SQL_FROM_ROLES] = (constants.db.SQL_TYPE_TEXT,)*2

types[constants.db.SQL_FROM_GUILD] = (constants.db.SQL_TYPE_INT,)*2

types[constants.db.SQL_FROM_CONTR] = (constants.db.SQL_TYPE_TEXT,
                                 constants.db.SQL_TYPE_INT)

types[constants.db.SQL_FROM_CHANS] = types[constants.db.SQL_FROM_CONTR]

types[constants.db.SQL_FROM_OFFSET] = (constants.db.SQL_TYPE_INT,)


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


async def construct_SQL(*args):
    """
    :func:`construct_SQL` creates a SQLite statement.

    Args:
        args (tuple): the statements to use into one statement

    Returns:
        str: a full SQLite statement
    """
    args = [str(arg) for arg in args]
    return ' '.join(args)


async def construct_filters(*args):
    """
    :func:`construct_filters` creates a compound SQLite filter
    in string form.

    Args:
        args (tuple): the filters

    Returns:
        str: a compound SQLite filter
    """
    args = [str(arg) for arg in args]
    return '{} {}'.format(constants.db.SQL_WHERE,
                          ' {} '.format(constants.db.SQL_AND).join(args))


class Database:
    """:class:`Database` serves as the backend for all of the Vaivora modules."""

    def __init__(self, db_id: str):
        """
        :func:`__init__` initializes the db module.

        Args:
            db_id (str): the db id for the guild
        """
        self.db_id = db_id
        self.db_name = '{}{}{}'.format(constants.db.DIR, self.db_id, constants.db.EXT)

    def get_id(self):
        """
        :func:`get_id` returns the database id.

        Returns:
            str: this database id
        """
        return self.db_id

    async def create_db(self, kind):
        """
        :func:`create_db` creates a db when none (or invalid) exists,
        on the spec for `kind`.

        Args:
            kind (str): see :func:`get_dbs`
        """
        if kind == constants.db.SQL_FROM_BOSS:
            module = constants.db.MOD_BOSS
        else:
            module = constants.db.MOD_SETS
        async with aiosqlite.connect(self.db_name) as _db:
            await _db.execute('drop table if exists {}'.format(module))
            await _db.execute('create table {}({})'
                              .format(constants.db.MOD,
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
        if module == constants.db.MOD_BOSS:
            select = [constants.db.SQL_FROM_BOSS]
        elif module == constants.db.MOD_SETS:
            select = constants.db.SQL_FROM_SETS

        async with aiosqlite.connect(self.db_name) as _db:
            _db.row_factory = aiosqlite.Row
            for _s in select:
                try:
                    cursor = await _db.execute(
                                await construct_SQL(constants.db.SQL_SELECT,
                                                    _s))
                except:
                    return False

                r = await cursor.fetchone()
                if not r:
                    await cursor.close()
                    return True

                if sorted(tuple(r.keys())) != sorted(columns[_s]):
                    await cursor.close()
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
                                await construct_SQL(constants.db.SQL_SELECT,
                                                    constants.db.SQL_FROM_BOSS,
                                                    await construct_filters(
                                                        constants.db.SQL_WHERE_NAME,
                                                        constants.db.SQL_WHERE_CHANNEL)),
                                                (boss, channel,))
                else:
                    cursor = await _db.execute(
                                await construct_SQL(constants.db.SQL_SELECT,
                                                    constants.db.SQL_FROM_BOSS,
                                                    await construct_filters(
                                                        constants.db.SQL_WHERE_NAME)),
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

        boss_name = boss_dict[constants.db.COL_BOSS_NAME]
        boss_channel = boss_dict[constants.db.COL_BOSS_CHANNEL]

        # handle channels
        if boss_channel:
            sel_statement = await construct_SQL(constants.db.SQL_SELECT,
                                                constants.db.SQL_FROM_BOSS,
                                                await construct_filters(
                                                    constants.db.SQL_WHERE_NAME,
                                                    constants.db.SQL_WHERE_CHANNEL))
            sql_condition = (boss_name, boss_channel)
        # handle everything else
        else:
            sel_statement = await construct_SQL(constants.db.SQL_SELECT,
                                                constants.db.SQL_FROM_BOSS,
                                                await construct_filters(
                                                    constants.db.SQL_WHERE_NAME))
            sql_condition = (boss_name,)

        async with aiosqlite.connect(self.db_name) as _db:
            _db.row_factory = aiosqlite.Row

            cursor = await _db.execute(sel_statement, sql_condition)
            contents.extend(await cursor.fetchall())

            if contents and ((int(contents[0][5])
                              == boss_dict[constants.db.COL_TIME_YEAR]) and
                             (int(contents[0][6])
                              == boss_dict[constants.db.COL_TIME_MONTH]) and
                             (int(contents[0][7])
                              == boss_dict[constants.db.COL_TIME_DAY])and
                             (int(contents[0][8])
                              > boss_dict[constants.db.COL_TIME_HOUR])):
                await cursor.close()
                return False
            elif contents and ((int(contents[0][5])
                                <= boss_dict[constants.db.COL_TIME_YEAR]) or
                               (int(contents[0][6])
                                <= boss_dict[constants.db.COL_TIME_MONTH]) or
                               (int(contents[0][7])
                                <= boss_dict[constants.db.COL_TIME_DAY]) or
                               (int(contents[0][8])
                                <= boss_dict[constants.db.COL_TIME_HOUR])):

                if boss_channel:
                    await self.rm_entry_db_boss(boss_list=[boss_name,],
                                                boss_ch=boss_channel)
                else:
                    await self.rm_entry_db_boss(boss_list=[boss_name,])

            try:
                # boss database structure
                await _db.execute(
                    constants.db.SQL_UPDATE,
                    (str(boss_name),
                     int(boss_channel),
                     str(boss_dict[constants.db.COL_BOSS_MAP]),
                     str(boss_dict[constants.db.COL_BOSS_STATUS]),
                     str(boss_dict[constants.db.COL_BOSS_TXT_CHANNEL]),
                     int(boss_dict[constants.db.COL_TIME_YEAR]),
                     int(boss_dict[constants.db.COL_TIME_MONTH]),
                     int(boss_dict[constants.db.COL_TIME_DAY]),
                     int(boss_dict[constants.db.COL_TIME_HOUR]),
                     int(boss_dict[constants.db.COL_TIME_MINUTE])))
                await _db.commit()
                return True
            except:
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
                # channel is provided
                if boss_ch:
                    sql_filters = await construct_filters(
                                            constants.db.SQL_WHERE_NAME,
                                            constants.db.SQL_WHERE_CHANNEL)
                    sql_condition = (boss, boss_ch)
                # only name                
                else:
                    sql_filters = await construct_filters(
                                            constants.db.SQL_WHERE_NAME)
                    sql_condition = (boss,)

                # process counting
                sel_statement = await construct_SQL(constants.db.SQL_SELECT,
                                                    constants.db.SQL_FROM_BOSS,
                                                    sql_filters)
                del_statement = await construct_SQL(constants.db.SQL_DELETE,
                                                    constants.db.SQL_FROM_BOSS,
                                                    sql_filters)

                cursor = await _db.execute(sel_statement, sql_condition)
                results = await cursor.fetchall()

                # no records to delete
                if len(results) == 0:
                    continue

                try:
                    await cursor.execute(del_statement, sql_condition)
                    await _db.commit()
                    records.append(boss) # guaranteed to be only one entry as per this loop
                except Exception as e: # in case of sqlite3 exceptions
                    print(self.db_id, e)
                    continue
            await cursor.close()

        return records # return an implicit bool for how many were deleted

    async def get_users(self, kind):
        """
        :func:`get_users` gets users of a `kind`.
        Users are defined to be either Discord Members or Roles,
        hence not using "get_members" as the function name.

        Args:
            kind (str): the kind of user desired

        Returns:
            list: a list of users by id
            None: if no such users were configured
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute(
                            await construct_SQL(constants.db.COL_SQL_FROM_ROLES
                                                .format(kind)))
                return [_row[0] for _row in await cursor.fetchall()]
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
                    cursor = await _db.execute(constants.db.SQL_ADD_ROLES
                                               .format(user, kind))
                except Exception as e:
                    print(e)
                    errs.append(user)
                    continue
            await _db.commit()
        return errs

    async def update_owner_sauth(self, owner_id: str):
        """
        :func:`update_owner_sauth` updates owner to `s`uper `auth`orized
        after each boot.

        Args:
            owner_id (str): the id of the owner

        Returns:
            True if successful; False otherwise
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                cursor = await _db.execute(constants.db.SQL_GET_OLD_OWNER)
                old_owner = (await cursor.fetchone())[0]
                if owner_id == old_owner:
                    return True # do not do anything if it's the same owner
                await _db.execute(constants.db.SQL_DROP_OWNER)
                await _db.execute(constants.db.SQL_DEL_OLD_OWNER
                                  .format(old_owner))
            except: #Exception as e:
                #print('Exception caught & ignored:', e)
                pass

            try:
                await _db.execute(constants.db.SQL_MAKE_OWNER)
            except: #Exception as e:
                # table owner might already exist
                #print('Exception caught & ignored:', e)
                pass

            try:
                await _db.execute(constants.db.SQL_UPDATE_OWNER
                                  .format(owner_id))
                await _db.execute(constants.db.SQL_ADD_ROLES
                                  .format(constants.settings.ROLE_AUTH,
                                          owner_id))
                await _db.execute(constants.db.SQL_ADD_ROLES
                                  .format(constants.settings.ROLE_SUPER_AUTH,
                                          owner_id))
                await _db.commit()
                return True
            except Exception as e:
                print('Exception caught:', e)
                return False

    async def clean_duplicates(self):
        """
        :func:`clean_duplicates` gets rid of duplicates from all tables.
        """
        async with aiosqlite.connect(self.db_name) as _db:
            for _table in constants.db.SQL_CLEAN_TABLES:
                try:
                    await _db.execute(constants.db.SQL_CLEAN_DUPES
                                      .format(_table,
                                              constants.db.SQL_CLEAN[_table]))
                except Exception as e:
                    print(e)
                    continue

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
                await _db.execute(constants.db.SQL_DROP_CHANS)
                await _db.commit()
                await _db.execute(constants.db.SQL_MAKE_CHANS)
                await _db.commit()
                return True
            except Exception as e:
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
                            await construct_SQL(constants.db.COL_SQL_FROM_CHANS
                                                .format(kind)))
                return [_row[0] for _row in await cursor.fetchall()]
            except Exception as e:
                print(e)
                return None

    async def set_channel(self, kind, ch_id):
        """
        :func:`set_channel` adds a channel as a `kind`

        Args:
            kind (str): the kind of channel to filter
                e.g. 'boss', 'management'
            ch_id (str): the id of a channel to set

        Returns:
            True if successful; False otherwise
        """
        async with aiosqlite.connect(self.db_name) as _db:
            try:
                await _db.execute(
                    await construct_SQL(constants.db.SQL_SET_CHANNEL
                                        .format(kind, ch_id)))
                await _db.commit()
                return True
            except Exception as e:
                print(e)
                return False
