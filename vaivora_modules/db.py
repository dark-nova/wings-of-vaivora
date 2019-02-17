import asyncio
import aiosqlite
from operator import itemgetter

from constants.settings import en_us as lang_settings
from constants.boss import en_us as lang_boss
from constants.db import en_us as lang_db


columns = {}
columns[lang_db.SQL_FROM_BOSS] = (
    lang_db.COL_BOSS_NAME,
    lang_db.COL_BOSS_CHANNEL,
    lang_db.COL_BOSS_MAP,
    lang_db.COL_BOSS_STATUS,
    lang_db.COL_BOSS_TXT_CHANNEL,
    lang_db.COL_TIME_YEAR,
    lang_db.COL_TIME_MONTH,
    lang_db.COL_TIME_DAY,
    lang_db.COL_TIME_HOUR,
    lang_db.COL_TIME_MINUTE
    )

columns[lang_db.SQL_FROM_ROLES] = (
    lang_db.COL_SETS_ROLES
    )

columns[lang_db.SQL_FROM_CHANS] = (
    lang_db.COL_SETS_CHANS
    )

columns[lang_db.SQL_FROM_GUILD] = (
    lang_db.COL_SETS_GUILD
    )

columns[lang_db.SQL_FROM_CONTR] = (
    lang_db.COL_SETS_CONTR
    )

columns[lang_db.SQL_FROM_OFFSET] = (
    lang_db.COL_SETS_OFFSET
    )

types = {}
types[lang_db.SQL_FROM_BOSS] = ((lang_db.SQL_TYPE_TEXT,
                                 lang_db.SQL_TYPE_INT,)
                                + (lang_db.SQL_TYPE_TEXT,)*3
                                + (lang_db.SQL_TYPE_INT,)*5)

types[lang_db.SQL_FROM_ROLES] = (lang_db.SQL_TYPE_TEXT,)*2

types[lang_db.SQL_FROM_GUILD] = (lang_db.SQL_TYPE_INT,)*2

types[lang_db.SQL_FROM_CONTR] = (lang_db.SQL_TYPE_TEXT,
                                 lang_db.SQL_TYPE_INT)

types[lang_db.SQL_FROM_CHANS] = types[lang_db.SQL_FROM_CONTR]

types[lang_db.SQL_FROM_OFFSET] = (lang_db.SQL_TYPE_INT,)


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
    return '{} {}'.format(lang_db.SQL_WHERE,
                          ' {} '.format(lang_db.SQL_AND).join(args))


class Database:
    """:class:`Database` serves as the backend for all of the Vaivora modules."""

    def __init__(self, db_id: str):
        """
        :func:`__init__` initializes the db module.

        Args:
            db_id (str): the db id for the guild
        """
        self.db_id = db_id
        self.db_name = '{}{}{}'.format(lang_db.DIR, self.db_id, lang_db.EXT)

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
        if kind == lang_db.SQL_FROM_BOSS:
            module = lang_db.MOD_BOSS
        else:
            module = lang_db.MOD_SETS
        async with aiosqlite.connect(self.db_name) as _db:
            await _db.execute('drop table if exists {}'.format(module))
            await _db.execute('create table {}({})'
                              .format(lang_db.MOD,
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
        if module == lang_db.MOD_BOSS:
            select = [lang_db.SQL_FROM_BOSS]
        elif module == lang_db.MOD_SETS:
            select = lang_db.SQL_FROM_SETS

        async with aiosqlite.connect(self.db_name) as _db:
            _db.row_factory = aiosqlite.Row
            for _s in select:
                try:
                    cursor = await _db.execute(
                                    await construct_SQL(lang_db.SQL_SELECT,
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

    async def check_db_boss(self, bosses=lang_boss.ALL_BOSSES, channel=0):
        """
        :func:`check_db_boss` checks the database for the conditions in argument

        Args:
            bosses (list): (default: lang_boss.ALL_BOSSES) the bosses to check
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
                                await construct_SQL(lang_db.SQL_SELECT,
                                                    lang_db.SQL_FROM_BOSS,
                                                    await construct_filters(
                                                        lang_db.SQL_WHERE_NAME,
                                                        lang_db.SQL_WHERE_CHANNEL)),
                                                (boss, channel,))
                else:
                    cursor = await _db.execute(
                                await construct_SQL(lang_db.SQL_SELECT,
                                                    lang_db.SQL_FROM_BOSS,
                                                    await construct_filters(
                                                        lang_db.SQL_WHERE_NAME)),
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

        boss_name = boss_dict[lang_db.COL_BOSS_NAME]
        boss_channel = boss_dict[lang_db.COL_BOSS_CHANNEL]

        # handle channels
        if boss_channel:
            sel_statement = await construct_SQL(lang_db.SQL_SELECT,
                                                lang_db.SQL_FROM_BOSS,
                                                await construct_filters(
                                                    lang_db.SQL_WHERE_NAME,
                                                    lang_db.SQL_WHERE_CHANNEL))
            sql_condition = (boss_name, boss_channel)
        # handle everything else
        else:
            sel_statement = await construct_SQL(lang_db.SQL_SELECT,
                                                lang_db.SQL_FROM_BOSS,
                                                await construct_filters(
                                                    lang_db.SQL_WHERE_NAME))
            sql_condition = (boss_name,)

        async with aiosqlite.connect(self.db_name) as _db:
            _db.row_factory = aiosqlite.Row

            cursor = await _db.execute(sel_statement, sql_condition)
            contents.extend(await cursor.fetchall())

            if contents and ((int(contents[0][5])
                              == boss_dict[lang_db.COL_TIME_YEAR]) and
                             (int(contents[0][6])
                              == boss_dict[lang_db.COL_TIME_MONTH]) and
                             (int(contents[0][7])
                              == boss_dict[lang_db.COL_TIME_DAY])and
                             (int(contents[0][8])
                              > boss_dict[lang_db.COL_TIME_HOUR])):
                await cursor.close()
                return False
            elif contents and ((int(contents[0][5])
                                <= boss_dict[lang_db.COL_TIME_YEAR]) or
                               (int(contents[0][6])
                                <= boss_dict[lang_db.COL_TIME_MONTH]) or
                               (int(contents[0][7])
                                <= boss_dict[lang_db.COL_TIME_DAY]) or
                               (int(contents[0][8])
                                <= boss_dict[lang_db.COL_TIME_HOUR])):

                if boss_channel:
                    await self.rm_entry_db_boss(boss_list=[boss_name,],
                                                boss_ch=boss_channel)
                else:
                    await self.rm_entry_db_boss(boss_list=[boss_name,])

            try:
                # boss database structure
                await _db.execute(
                    lang_db.SQL_UPDATE,
                    (str(boss_name),
                     int(boss_channel),
                     str(boss_dict[lang_db.COL_BOSS_MAP]),
                     str(boss_dict[lang_db.COL_BOSS_STATUS]),
                     str(boss_dict[lang_db.COL_BOSS_TXT_CHANNEL]),
                     int(boss_dict[lang_db.COL_TIME_YEAR]),
                     int(boss_dict[lang_db.COL_TIME_MONTH]),
                     int(boss_dict[lang_db.COL_TIME_DAY]),
                     int(boss_dict[lang_db.COL_TIME_HOUR]),
                     int(boss_dict[lang_db.COL_TIME_MINUTE])))
                await _db.commit()
                return True
            except:
                return False

    async def rm_entry_db_boss(self, boss_list=lang_boss.ALL_BOSSES, boss_ch=0):
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
            boss_list = lang_boss.ALL_BOSSES

        async with aiosqlite.connect(self.db_name) as _db:
            _db.row_factory = aiosqlite.Row

            for boss in boss_list:
                # channel is provided
                if boss_ch:
                    sql_filters = await construct_filters(
                                            lang_db.SQL_WHERE_NAME,
                                            lang_db.SQL_WHERE_CHANNEL)
                    sql_condition = (boss, boss_ch)
                # only name                
                else:
                    sql_filters = await construct_filters(
                                            lang_db.SQL_WHERE_NAME)
                    sql_condition = (boss,)

                # process counting
                sel_statement = await construct_SQL(lang_db.SQL_SELECT,
                                                    lang_db.SQL_FROM_BOSS,
                                                    sql_filters)
                del_statement = await construct_SQL(lang_db.SQL_DELETE,
                                                    lang_db.SQL_FROM_BOSS,
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
                                await construct_SQL(lang_db.COL_SQL_FROM_ROLES
                                                    .format(ch_type)))
                return [_row[0] for _row in await cursor.fetchall()]
            except Exception as e:
                print(e)
                return None

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
                cursor = await _db.execute(lang_db.SQL_GET_OLD_OWNER)
                old_owner = (await cursor.fetchone())[0]
                if owner_id == old_owner:
                    return True # do not do anything if it's the same owner
                await _db.execute(lang_db.SQL_DROP_OWNER)
                await _db.execute(lang_db.SQL_DEL_OLD_OWNER
                                  .format(old_owner))
            except: #Exception as e:
                #print('Exception caught & ignored:', e)
                pass

            try:
                await _db.execute(lang_db.SQL_MAKE_OWNER)
            except: #Exception as e:
                # table owner might already exist
                #print('Exception caught & ignored:', e)
                pass

            try:
                await _db.execute(lang_db.SQL_UPDATE_OWNER
                                  .format(owner_id))
                await _db.execute(lang_db.SQL_SAUTH_OWNER
                                  .format(lang_settings.ROLE_SUPER_AUTH,
                                          owner_id))
                await _db.commit()
                return True
            except Exception as e:
                print('Exception caught:', e)
                return False


    async def get_channels(self, ch_type):
        """
        :func:`get_channels` gets channels of a given `ch_type`.

        Args:
            ch_type (str): the channel type to filter
                e.g. 'boss', 'management'

        Returns:
            list: a list of channels of `ch_type`
            None: if no such channels were configured
        """
        async with aiosqlite.connect(self.db_name) as _db:
            #_db.row_factory = aiosqlite.Row
            try:
                cursor = await _db.execute(
                                await construct_SQL(lang_db.COL_SQL_FROM_CHANS
                                                    .format(ch_type)))
                return [_row[0] for _row in await cursor.fetchall()]
            except Exception as e:
                print(e)
                return None

    async def set_channels(self, ch_id, ch_type):
        """
        :func:`set_channels` adds a channel as a `ch_type`

        Args:
            ch_id (str): the 
        """
        pass
