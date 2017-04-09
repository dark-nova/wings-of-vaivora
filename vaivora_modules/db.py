import sqlite3

# import additional constants
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)

class Database:
    # constants
    TIME                    = "Time"
    modules                 = ['boss', 'reminders', 'talt', 'permissions' ]
    # BOSS        = "Module: Boss"
    # REMINDERS   = "Module: Reminders"
    # TALT        = "Module: Talt Tracker"
    # PERMISSIONS = "Module: Permissions"

    # database formats
    columns                 = dict()
    columns[TIME]           = ('year', 'month', 'day', 'hour', 'minute')
    columns[modules[0]]     = ('name', 'channel', 'map', 'status', 'text_channel') + columns[TIME]
    columns[modules[1]]     = ('user', 'comment') + columns[TIME]
    columns[modules[2]]     = ('user', 'previous', 'current', 'valid') + columns[TIME]
    columns[modules[3]]     = ('user', 'role')

    # and the database formats' types
    types                   = dict()
    types[TIME]             = ('real',)*5
    types[modules[0]]       = ('text',) + ('real',) + ('text',)*3 + types[TIME]
    types[modules[1]]       = ('text',)*2 + types[TIME]
    types[modules[2]]       = ('text',) + ('real',)*3 + types[TIME]
    types[modules[3]]       = ('text',)*2

    # zip, create, concatenate into tuple
    dbs                     = dict()
    dbs[modules[0]]         = tuple('{} {}'.format(*t) for t in 
                                    zip(columns[modules[0]], types[modules[0]]))
    dbs[modules[1]]         = tuple('{} {}'.format(*t) for t in 
                                    zip(columns[modules[1]], types[modules[1]]))
    dbs[modules[2]]         = tuple('{} {}'.format(*t) for t in 
                                    zip(columns[modules[2]], types[modules[2]]))
    dbs[modules[3]]         = tuple('{} {}'.format(*t) for t in
                                    zip(columns[modules[3]], types[modules[3]]))


    def __init__(self, db_id):
        self.db_id          = str(db_id)
        self.db_name        = self.db_id + ".db"
        self.open_db()
        self.invalid        = self.check_if_invalid()
        if self.invalid:
            self.create_db(invalid)
        self.save_db()

    def open_db(self):
        self.connect        = sqlite3.connect(self.db_name)
        self.connect.row_factory = sqlite3.Row
        self.cursor         = self.connect.cursor()


    def save_db(self):
        self.connect.commit()
        self.connect.close()


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
        for invalid_module in invalid:
            self.cursor.execute('drop table if exists {}'.format(invalid_module))
            self.cursor.execute('create table {}({})'.format((invalid_module, ','.join(dbs[invalid_module]),)))
        # else:
        #     for module in modules:
        #         self.cursor.execute('create table {}({})'.format((module, ','.join(dbs[module]),)))
        self.invalid = []
        return


    # @func:    check_if_invalid(self)
    # @arg:
    #   self
    # @return:
    #   invalid:
    #           a list containing invalid database module names (str) or None
    def check_if_invalid(self):
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
        return invalid


    # @func:    check_db_boss(self, list)
    # @arg:
    #   self
    #   bosses:
    #           list containing bosses to check (default: vaivora_constants.command.boss.bosses)
    # @return:
    #   db_record:
    #           a list containing records or None
    def check_db_boss(self, bosses=vaivora_constants.command.boss.bosses, channel=0):
        db_record = list()
        for boss in bosses:
            if channel:
                self.cursor.execute("select * from boss where name=? and channel=?", (boss, channel,))
            else:
                self.cursor.execute("select * from boss where name=?", (boss,))
            records = self.cursor.fetchall()
            for record in records:
                db_record.append(tuple(record))
        # return a list of records
        return db_record


    # @func:    update_db_boss(sqlite3.connect.cursor, dict)
    # @arg:
    #   c:              the sqlite3 connection cursor
    #   boss_dict:      message_args from on_message(*)
    # @return:
    #   True if successful, False otherwise
    def update_db_boss(self, boss_dict):
        # the following two bosses rotate per spawn
        if boss_dict['name'] == 'Mirtis' or boss_dict['name'] == 'Helgasercle':
            self.cursor.execute("select * from boss where name=?", ('Mirtis',))
            contents = self.cursor.fetchall()
            self.cursor.execute("select * from boss where name=?", ('Helgasercle',))
            contents += self.cursor.fetchall()
        elif boss_dict['name'] == 'Demon Lord Marnox' or boss_dict['name'] == 'Rexipher':
            self.cursor.execute("select * from boss where name=?", ('Demon Lord Marnox',))
            contents = self.cursor.fetchall()
            self.cursor.execute("select * from boss where name=?", ('Rexipher',))
            contents += self.cursor.fetchall()
        elif boss_dict['name'] == 'Blasphemous Deathweaver':
            self.cursor.execute("select * from boss where name=? and map=?", \
                                (boss_dict['name'], boss_dict['map'],))
            contents = self.cursor.fetchall()
        else:
            self.cursor.execute("select * from boss where name=? and channel=?", (boss_dict['name'], boss_dict['channel'],))
            contents = self.cursor.fetchall()

        # invalid case: more than one entry for this combination
        #### TODO: keep most recent time? 
        if   boss_dict['name'] != "Blasphemous Deathweaver" and len(contents) >= 1:
            self.rm_entry_db_boss(boss_name=boss_dict['name'], boss_map=boss_dict['map'])
        elif boss_dict['name'] == "Blasphemous Deathweaver" and len(contents) >= 2:
            self.rm_entry_db_boss(boss_name=boss_dict['name'])

        # if entry has newer data, discard previousit's 
        if contents and (int(contents[0][5]) < boss_dict['year'] or \
                         int(contents[0][6]) < boss_dict['month'] or \
                         int(contents[0][7]) < boss_dict['day'] or \
                         int(contents[0][8]) < boss_dict['hour'] - 3):
            self.rm_entry_db_boss(boss_name=boss_dict['name'])

        #try: # boss database structure
        self.cursor.execute("insert into boss values (?,?,?,?,?,?,?,?,?,?)", \
                            (str(boss_dict['name'   ]), \
                             int(boss_dict['channel']), \
                             str(boss_dict['map'    ]), \
                             str(boss_dict['status' ]), \
                             str(boss_dict['srvchn' ]), \
                             int(boss_dict['year'   ]), \
                             int(boss_dict['month'  ]), \
                             int(boss_dict['day'    ]), \
                             int(boss_dict['hour'   ]), \
                             int(boss_dict['mins'   ])))
        # except:
        #     return False
        return True

    # @func:    rm_entry_db_boss(, dict, int)
    # @arg:
    #   c:              the sqlite3 connection cursor
    #   boss_dict:      message_args from on_message(*)
    #   ch:             Default: None; the channel to remove
    # @return:
    #   True if successful, False otherwise
    def rm_entry_db_boss(self, boss_list=vaivora_constants.command.boss.bosses, boss_ch=0, boss_map=''):
        for boss in boss_list:
            if boss_ch:
                self.cursor.execute("delete from boss where name=? and channel=?", (boss, boss_ch,))
            elif boss_map:
                ####TODO: make more generalized case. Currently applies only to Deathweaver
                dw_idx  = vaivora_constants.command.boss.boss_locs['Blasphemous Deathweaver'].index(boss_map)
                if dw_idx == 0 or dw_idx == 1: # crystal mine
                    dw_idx = [(dw_idx + 1) % 2,]
                else:
                    dw_idx = [(dw_idx % 3 + 2, (dw_idx-1) % 3 + 2,)]
                for idx in dw_idx:
                    try:
                        self.cursor.execute("delete from boss where name=? and map=?", \
                                            (boss, vaivora_constants.command.boss.boss_locs['Blasphemous Deathweaver'][idx],))
                    except:
                        continue
            else:
                self.cursor.execute("delete from boss where name=?", (boss,))
        except:
            return False
        return True