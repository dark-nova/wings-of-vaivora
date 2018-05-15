from operator import itemgetter
import sqlite3
from importlib import import_module as im
import vaivora_modules
for mod in vaivora_modules.modules:
    im(mod)
from constants.boss import en_us as lang


class Database:
    # constants
    TIME                    =   "Time"
    modules                 =   [ 'boss' ]
    # BOSS        = "Module: Boss"
    # REMINDERS   = "Module: Reminders"
    # TALT        = "Module: Talt Tracker"
    # PERMISSIONS = "Module: Permissions"

    # database formats
    columns                 =   dict()
    columns[TIME]           =   ('year', 'month', 'day', 'hour', 'minute')
    columns[modules[0]]     =   ('name', 'channel', 'map', 'status', 'text_channel') + columns[TIME]
    # columns[modules[1]]     =   ('user', 'comment') + columns[TIME]
    # columns[modules[2]]     =   ('user', 'previous', 'current', 'valid') + columns[TIME]
    # columns[modules[3]]     =   ('user', 'role')

    # and the database formats' types
    types                   =   dict()
    types[TIME]             =   ('real',)*5
    types[modules[0]]       =   ('text',) + ('real',) + ('text',)*3 + types[TIME]
    # types[modules[1]]       =   ('text',)*2 + types[TIME]
    # types[modules[2]]       =   ('text',) + ('real',)*3 + types[TIME]
    # types[modules[3]]       =   ('text',)*2

    # zip, create, concatenate into tuple
    dbs                     =   dict()
    dbs[modules[0]]         =   tuple('{} {}'.format(*t) for t in 
                                      zip(columns[modules[0]], types[modules[0]]))
    # dbs[modules[1]]         =   tuple('{} {}'.format(*t) for t in 
    #                                   zip(columns[modules[1]], types[modules[1]]))
    # dbs[modules[2]]         =   tuple('{} {}'.format(*t) for t in 
    #                                   zip(columns[modules[2]], types[modules[2]]))
    # dbs[modules[3]]         =   tuple('{} {}'.format(*t) for t in
    #                                   zip(columns[modules[3]], types[modules[3]]))

    sql_select = "select * "
    sql_count = "select count(*) "
    sql_from_boss = "from boss "
    sql_and = "and "
    sql_boss_name = "name=? "
    sql_boss_map = "map=? "
    sql_boss_channel = "channel=?"
    sql_boss_default = "from boss where name=?"
    sql_order = "order by year desc, month desc, day desc, hour desc, minute desc "

    def __init__(self, db_id):
        self.db_id          = str(db_id)
        self.db_name        = "db/" + self.db_id + ".db"
        self.open_db()
        self.invalid        = self.check_if_invalid()
        if self.invalid:
            self.create_db(self.invalid)


    def open_db(self):
        self.connect        = sqlite3.connect(self.db_name)
        self.connect.row_factory = sqlite3.Row
        self.cursor         = self.connect.cursor()


    def save_db(self):
        self.connect.commit()
        #self.connect.close()


    def get_id(self):
        return self.db_id

    # @func:    create_db(self, list)
    # @post:    no invalid databases
    # @arg:
    #   conn:
    #           the sqlite3 connection
    #   invalid:
    #           invalid databases to redo (default: modules)
    # @return:
    #   None
    def create_db(self, invalid=modules):
        #self.open_db()
        for invalid_module in invalid:
            self.cursor.execute('drop table if exists {}'.format(invalid_module))
            self.cursor.execute('create table {}({})'.format(invalid_module, ','.join(self.dbs[invalid_module])))
        # else:
        #     for module in modules:
        #         self.cursor.execute('create table {}({})'.format((module, ','.join(dbs[module]),)))
        self.invalid = []
        self.save_db()
        return


    # @func:    check_if_invalid(self)
    # @arg:
    #   self
    # @return:
    #   invalid:
    #           a list containing invalid database module names (str) or None
    def check_if_invalid(self):
        #self.open_db()
        invalid = []
        for module in self.modules:
            try:
                self.cursor.execute('select * from ' + module)
            except:
                invalid.append(module)
                continue
            r = self.cursor.fetchone()
            if not r:
                continue # it's empty. probably works.
            if sorted(tuple(r.keys())) != sorted(self.columns[module]):
                invalid.append(module)
                continue
        self.save_db()
        return invalid


    # @func:    check_db_boss(self, list)
    # @arg:
    #   self
    #   bosses:
    #           list containing bosses to check (default: vaivora_modules.boss.bosses)
    # @return:
    #   db_record:
    #           a list containing records or None
    def check_db_boss(self, bosses=vaivora_modules.boss.bosses, channel=0):
        #self.open_db()
        db_record = list()
        for boss in bosses:
            if channel:
                self.cursor.execute((self.sql_select+self.sql_boss_world), (boss, channel,))
            else:
                self.cursor.execute((self.sql_select+self.sql_boss_default), (boss,))
            records = self.cursor.fetchall()
            for record in records:
                db_record.append(tuple(record))
        self.save_db()
        db_record   =   self.sort_db(db_record)
        # return a list of records
        return db_record


    def sort_db(self, rec_db):
        return sorted(rec_db, key=itemgetter(5,6,7,8,9), reverse=True)



    # @func:    update_db_boss(sqlite3.connect.cursor, dict)
    # @arg:
    #   c:              the sqlite3 connection cursor
    #   boss_dict:      message_args from on_message(*)
    # @return:
    #   True if successful, False otherwise
    def update_db_boss(self, boss_dict):
        contents = []
        #self.open_db()

        # handle world bosses
        if boss_dict['channel']:
            sel_statement   =   self.sql_select+self.sql_boss_world
            sql_condition   =   (boss_dict['boss'], boss_dict['channel'])
        
        # handle everything else
        else:
            sel_statement   =   self.sql_select+self.sql_boss_default
            sql_condition   =   (boss_dict['boss'],)

        self.cursor.execute(sel_statement, sql_condition)
        contents.extend(self.cursor.fetchall())

        if contents and (int(contents[0][5]) == boss_dict['year'] and \
                         int(contents[0][6]) == boss_dict['month'] and \
                         int(contents[0][7]) == boss_dict['day'] and \
                         int(contents[0][8]) >  boss_dict['hour']):
            return False
        elif contents and (int(contents[0][5]) <= boss_dict['year'] or \
                           int(contents[0][6]) <= boss_dict['month'] or \
                           int(contents[0][7]) <= boss_dict['day'] or \
                           int(contents[0][8]) <= boss_dict['hour']):

            if boss_dict['boss'] in vaivora_modules.boss.bosses_world:
                self.rm_entry_db_boss(boss_list=[boss_dict['boss'],], boss_ch=boss_dict['channel'])
            else:
                self.rm_entry_db_boss(boss_list=[boss_dict['boss'],])


        #try: # boss database structure
        self.cursor.execute("insert into boss values (?,?,?,?,?,?,?,?,?,?)", \
                            (str(boss_dict['boss'           ]), \
                             int(boss_dict['channel'        ]), \
                             str(boss_dict['map'            ]), \
                             str(boss_dict['status'         ]), \
                             str(boss_dict['text_channel'   ]), \
                             int(boss_dict['year'           ]), \
                             int(boss_dict['month'          ]), \
                             int(boss_dict['day'            ]), \
                             int(boss_dict['hour'           ]), \
                             int(boss_dict['mins'           ])))
        self.save_db()
        return True


    def rm_entry_db_boss(self, boss_list=vaivora_modules.boss.bosses, boss_ch=0, boss_map=None):
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
        rec_count = 0
        if not boss_list:
            boss_list = lang.ALL_BOSSES
        for boss in boss_list:
            if boss_ch:
                sql_statement = self.sql_boss_world
                sql_condition = (boss, boss_ch)
            elif boss_map and boss_map is not None:
                sql_statement = self.sql_boss_field
                sql_condition = (boss, boss_map)
            # handle all others, generally field bosses
            else:
                sql_statement = self.sql_boss_default
                sql_condition = (boss,)

            # process counting
            ct_statement    = "select count(*) " + sql_statement
            del_statement   = "delete " + sql_statement                
            self.cursor.execute(ct_statement, sql_condition)
            result  = self.cursor.fetchone()
            # no records to delete
            if result[0] == 0:
                continue
            # records to delete
            else:
                try:
                    self.cursor.execute(del_statement, sql_condition)
                    self.save_db()
                    rec_count   +=  int(result[0])
                except: # in case of sqlite3 exceptions
                    continue
        self.save_db()
        return rec_count # return an implicit bool for how many were deleted