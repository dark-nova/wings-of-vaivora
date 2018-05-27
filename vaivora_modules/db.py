from operator import itemgetter
import sqlite3
from importlib import import_module as im
import vaivora_modules
for mod in vaivora_modules.modules:
    im(mod)
from constants.boss import en_us as lang_boss
from constants.db import en_us as lang_db


def construct_SQL(*args):
    """
    :func:`construct_SQL` creates a SQLite statement.

    Args:
        args (tuple): the statements to use into one statement

    Returns:
        str: a full SQLite statement
    """
    args = [str(arg) for arg in args]
    return ' '.join(args)


def construct_filters(*args):
    """
    :func:`construct_filters` creates a compound SQLite filter in string form.

    Args:
        args (tuple): the filters

    Returns:
        str: a compound SQLite filter
    """
    args = [str(arg) for arg in args]
    return '{} {}'.format(lang_db.SQL_WHERE,
                          ' {} '.format(lang_db.SQL_AND).join(args))


class Database:
    columns = dict()
    columns[lang_db.TIME] = (lang_db.COL_TIME_YEAR, lang_db.COL_TIME_MONTH, lang_db.COL_TIME_DAY,
                             lang_db.COL_TIME_HOUR, lang_db.COL_TIME_MINUTE)
    columns[lang_db.MOD] = (lang_db.COL_BOSS_NAME, lang_db.COL_BOSS_CHANNEL, lang_db.COL_BOSS_MAP,
                            lang_db.COL_BOSS_STATUS, lang_db.COL_BOSS_TXT_CHANNEL) + columns[lang_db.TIME]

    types = dict()
    types[lang_db.TIME] = (lang_db.SQL_TYPE_REAL,)*5
    types[lang_db.MOD] = ((lang_db.SQL_TYPE_TEXT,) + (lang_db.SQL_TYPE_REAL,) + 
                          (lang_db.SQL_TYPE_TEXT,)*3 + types[lang_db.TIME])

    # zip, create, concatenate into tuple
    dbs = dict()
    dbs[lang_db.MOD] = tuple('{} {}'.format(*t) for t in 
                             zip(columns[lang_db.MOD], types[lang_db.MOD]))
    # lang_db.MOD being solely 'boss' is a legacy design


    def __init__(self, db_id: str):
        """
        :func:`__init__` initializes the db module.

        Args:
            db_id (str): the db id for the guild
        """
        self.db_id = db_id
        self.db_name = '{}{}{}'.format(lang_db.DIR, self.db_id, lang_db.EXT)
        self.open_db()
        if not self.check_if_valid():
            self.create_db()


    def open_db(self):
        """
        :func:`open_db` opens the database for use.
        """
        self.connect = sqlite3.connect(self.db_name)
        self.connect.row_factory = sqlite3.Row
        self.cursor = self.connect.cursor()


    def save_db(self):
        """
        :func:`save_db` saves the database.
        """
        self.connect.commit()


    def get_id(self):
        """
        :func:`get_id` returns the database id.

        Returns:
            str: this database id
        """
        return self.db_id


    def create_db(self):
        """
        :func:`create_db` creates a db when none (or invalid) exists.

        Returns:
            None
        """
        #self.open_db()
        self.cursor.execute('drop table if exists {}'.format(lang_db.MOD))
        self.cursor.execute('create table {}({})'.format(lang_db.MOD, ','.join(self.dbs[lang_db.MOD])))
        # else:
        #     for module in modules:
        #         self.cursor.execute('create table {}({})'.format((module, ','.join(dbs[module]),)))
        self.save_db()
        return


    def check_if_valid(self):
        """
        :func:`check_if_valid` checks if the database is valid. Since only one module uses db, this will be one check only.

        Returns:
            bool: True if valid; False otherwise
        """
        #self.open_db()
        try:
            self.cursor.execute(construct_SQL(lang_db.SQL_SELECT, lang_db.SQL_FROM_BOSS))
        except:
            return False

        r = self.cursor.fetchone()
        if not r:
            return True

        if sorted(tuple(r.keys())) != sorted(self.columns[lang_db.MOD]):
            return False
        else:
            return True


    def check_db_boss(self, bosses=lang_boss.ALL_BOSSES, channel=0):
        """
        :func:`check_db_boss` checks the database for the conditions in argument

        Args:
            bosses (list): (default: lang_boss.ALL_BOSSES) the bosses to check
            channel (int): (default: 0) channels to filter

        Returns:
            list: records or list of None
        """
        #self.open_db()
        db_record = []
        for boss in bosses:
            if channel:
                self.cursor.execute(construct_SQL(lang_db.SQL_SELECT, lang_db.SQL_FROM_BOSS,
                                                  construct_filters(lang_db.SQL_WHERE_NAME,
                                                                    lang_db.SQL_WHERE_CHANNEL)),
                                    (boss, channel,))
            else:
                self.cursor.execute(construct_SQL(lang_db.SQL_SELECT, lang_db.SQL_FROM_BOSS,
                                                  construct_filters(lang_db.SQL_WHERE_NAME)),
                                    (boss,))

            records = self.cursor.fetchall()
            for record in records:
                db_record.append(tuple(record))

        self.save_db()
        return self.sort_db_record(db_record)


    def sort_db_record(self, db_record):
        """
        :func:`sort_db_record` sorts the db records by chronological order.

        Args:
            db_record (list): the records to sort

        """
        return sorted(db_record, key=itemgetter(5,6,7,8,9), reverse=True)


    def update_db_boss(self, boss_dict):
        """
        :func:`update_db_boss` updates the record with a new entry.

        Args:
            boss_dict (dict): the boss dictionary containing the new record

        Returns:
            bool: True if successful; False otherwise
        """
        contents = []
        #self.open_db()

        # handle channels
        if boss_dict[lang_db.COL_BOSS_CHANNEL]:
            sel_statement = construct_SQL(lang_db.SQL_SELECT, lang_db.SQL_FROM_BOSS,
                                          construct_filters(lang_db.SQL_WHERE_NAME,
                                                            lang_db.SQL_WHERE_CHANNEL))
            sql_condition = (boss_dict[lang_db.COL_BOSS_NAME], boss_dict[lang_db.COL_BOSS_CHANNEL])
        # handle everything else
        else:
            sel_statement = construct_SQL(lang_db.SQL_SELECT, lang_db.SQL_FROM_BOSS,
                                          construct_filters(lang_db.SQL_WHERE_NAME))
            sql_condition = (boss_dict[lang_db.COL_BOSS_NAME],)

        self.cursor.execute(sel_statement, sql_condition)
        contents.extend(self.cursor.fetchall())

        if contents and (int(contents[0][5]) == boss_dict[lang_db.COL_TIME_YEAR] and
                         int(contents[0][6]) == boss_dict[lang_db.COL_TIME_MONTH] and
                         int(contents[0][7]) == boss_dict[lang_db.COL_TIME_DAY] and
                         int(contents[0][8]) >  boss_dict[lang_db.COL_TIME_HOUR]):
            return False
        elif contents and (int(contents[0][5]) <= boss_dict[lang_db.COL_TIME_YEAR] or
                           int(contents[0][6]) <= boss_dict[lang_db.COL_TIME_MONTH] or
                           int(contents[0][7]) <= boss_dict[lang_db.COL_TIME_DAY] or
                           int(contents[0][8]) <= boss_dict[lang_db.COL_TIME_HOUR]):

            if boss_dict[lang_db.COL_BOSS_CHANNEL]:
                self.rm_entry_db_boss(boss_list=[boss_dict[lang_db.COL_BOSS_NAME],],
                                      boss_ch=boss_dict[lang_db.COL_BOSS_CHANNEL])
            else:
                self.rm_entry_db_boss(boss_list=[boss_dict[lang_db.COL_BOSS_NAME],])

        try:
            # boss database structure
            self.cursor.execute(lang_db.SQL_UPDATE,
                                (str(boss_dict[lang_db.COL_BOSS_NAME]),
                                 int(boss_dict[lang_db.COL_BOSS_CHANNEL]),
                                 str(boss_dict[lang_db.COL_BOSS_MAP]),
                                 str(boss_dict[lang_db.COL_BOSS_STATUS]),
                                 str(boss_dict[lang_db.COL_BOSS_TXT_CHANNEL]),
                                 int(boss_dict[lang_db.COL_TIME_YEAR]),
                                 int(boss_dict[lang_db.COL_TIME_MONTH]),
                                 int(boss_dict[lang_db.COL_TIME_DAY]),
                                 int(boss_dict[lang_db.COL_TIME_HOUR]),
                                 int(boss_dict[lang_db.COL_TIME_MINUTE])))
            self.save_db()
            return True
        except:
            return False


    def rm_entry_db_boss(self, boss_list=lang_boss.ALL_BOSSES, boss_ch=0, boss_map=None):
        """
        :func:`rm_entry_db_boss` removes records based on the conditions supplied.

        Args:
            boss_list (list): the list containing boss names (str) with records to erase
            boss_ch (int): (default: 0) the boss channel filter, if specified
            boss_map (str): (default: None) the boss map filter, if specified

        Returns:
            list: a list containing the records that were removed
        """
        #self.open_db()
        records = []
        if not boss_list:
            boss_list = lang_boss.ALL_BOSSES

        for boss in boss_list:
            # channel is provided
            if boss_ch:
                sql_filters = construct_filters(lang_db.SQL_WHERE_NAME,
                                                lang_db.SQL_WHERE_CHANNEL)
                sql_condition = (boss, boss_ch)
            # map is provided
            elif boss_map is not None:
                sql_filters = construct_filters(lang_db.SQL_WHERE_NAME,
                                                lang_db.SQL_WHERE_MAP)
                sql_condition = (boss, boss_map)
            # only name                
            else:
                sql_filters = construct_filters(lang_db.SQL_WHERE_NAME)
                sql_condition = (boss,)

            # process counting
            sel_statement = construct_SQL(lang_db.SQL_SELECT, lang_db.SQL_FROM_BOSS, sql_filters)
            del_statement = construct_SQL(lang_db.SQL_DELETE, lang_db.SQL_FROM_BOSS, sql_filters)

            print(del_statement)

            self.cursor.execute(sel_statement, sql_condition)
            results = self.cursor.fetchall()

            self.save_db()

            # no records to delete
            if len(results) == 0:
                continue

            try:
                self.cursor.execute(del_statement, sql_condition)
                self.save_db()
                records.append(boss) # guaranteed to be only one entry as per this loop
            except Exception as e: # in case of sqlite3 exceptions
                print('what', e)
                continue

        self.save_db()
        return records # return an implicit bool for how many were deleted
