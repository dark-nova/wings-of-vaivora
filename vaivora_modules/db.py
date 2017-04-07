import sqlite3

# import additional constants
from importlib import import_module as im
from .. import vaivora_constants
for mod in vaivora_constants.modules:
    im(".." + mod)

class db:
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
        open_db(self)
        if self.invalid:
            create_db(self, invalid)
        save_db(self)        

    def open_db(self):
        self.connect        = sqlite3.connect(self.db_name)
        self.connect.row_factory = sqlite3.Row
        self.cursor         = self.connect.cursor()


    def save_db(self):
        self.cursor.commit()
        self.cursor.close()


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
        for module in modules:
            try:
                self.cursor.execute('select * from ' + module)
            except:
                invalid.append(module)
                continue
            r = self.cursor.fetchone()
            if not r:
                continue # it's empty. probably works.
            if sorted(tuple(r.keys())) != sorted(columns[module]):
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
    def check_db_boss(self, bosses=vaivora_constants.command.boss.bosses):
        db_record = list()
        for boss in bosses:
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
    async def update_db_boss(self, boss_dict):
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
            await rm_entry_db_boss(self, boss_dict)
        elif boss_dict['name'] == "Blasphemous Deathweaver" and len(contents) >= 2:
            await rm_entry_db_boss(self, boss_dict)

        # if entry has newer data, discard previousit's 
        if contents and (int(contents[0][5]) < boss_dict['year'] or \
                         int(contents[0][6]) < boss_dict['month'] or \
                         int(contents[0][7]) < boss_dict['day'] or \
                         int(contents[0][8]) < boss_dict['hour'] - 3):
            await rm_entry_db_boss(self, boss_dict)

        #try: # boss database structure
        self.cursor.execute("insert into boss values (?,?,?,?,?,?,?,?,?,?)", \
                            (str(boss_dict['name']), \
                             int(boss_dict['channel']), \
                             str(boss_dict['map']), \
                             str(boss_dict['status']), \
                             str(boss_dict['srvchn']), \
                             int(boss_dict['year']), \
                             int(boss_dict['month']), \
                             int(boss_dict['day']), \
                             int(boss_dict['hour']), \
                             int(boss_dict['mins'])))
        # except:
        #     return False
        return True



##### Utility/helper functions #####

    # @func:    formmat_message_boss(str, str, datetime, str, int)
    # @arg:
    #   boss:
    #       str
    def format_message_boss(boss, status, time, bossmap, channel):
        kubas_ch    = ''
        if vaivora_constants.regex.boss.status.warning.match(status):
            bossmap     = [(bossmap,)]
        elif boss in vaivora_constants.command.boss.bosses_world:
            bossmap     = [(vaivora_constants.command.boss.boss_loc[boss],)]
        elif bossmap == 'N/A':
            bossmap     = ['[Map Unknown]',]
        elif boss == "Blasphemous Deathweaver" and vaivora_constants.regex.boss.location.AS.search(bossmap):
            bossmap     = [m for m in vaivora_constants.command.boss.boss_loc[boss][2:-1] if m != bossmap]
        elif boss == "Blasphemous Deathweaver":
            bossmap     = [m for m in vaivora_constants.command.boss.boss_loc[boss][0:2] if m != bossmap]
        else:
            bossmap     = [m for m in vaivora_constants.command.boss.boss_loc[boss] if m != bossmap]

        if boss == "Kubas Event":
            kubas_ch    = 1 if channel == 2 else 2
            kubas_ch    = " Machine of Riddles, ch."  + str(kubas_ch) + "."

        if vaivora_constants.regex.boss.status.anchored.search(status):
            report_time = time+timedelta(hours=-3)
            status_str  = " was anchored"
        elif vaivora_constants.regex.boss.status.warning.search(status):
            report_time = time+timedelta(hours=-2)
            status_str  = " was warned to spawn"
        else:
            if   boss in boss_spawn_02h:
                report_time = time+timedelta(hours=-2)
            elif boss in boss_spawn_16h:
                report_time = time+timedelta(hours=-16)
                print(report_time)
            else:
                report_time = time+timedelta(hours=-4)
            status_str = " died"

        status_str  = status_str + " in ch." + str(int(channel)) + " at "
        # if boss not in bos16s and boss not in bos02s:
        #     time_exp    = vaivora_constants.values.time.offset.boss_spawn_04h
        # elif boss in bos16s:
        #     time_exp    = con['TIME.WAIT.16H']
        # elif boss in bos02s:
        #     time_exp    = con['TIME.WAIT.2H']
        expect_str  = (("between " + (time-timedelta(hours=1)).strftime("%Y/%m/%d %H:%M") + " and ") \
                       if vaivora_constants.regex.boss.status.anchored.match(status) else "at ") + \
                      (time).strftime("%Y/%m/%d %H:%M") + \
                      " (in " + str(int((time-datetime.now()+vaivora_constants.values.time.offset.server2pacific).seconds/60)) + " minutes)"

        if "[Map Unknown]" in bossmap:
            map_str     = '.'
        else:
            map_str     = ", in one of the the following maps:" + '\n#    ' + '\n#    '.join(bossmap[0:])
        message     = "\"" + boss + "\"" + status_str + report_time.strftime("%Y/%m/%d %H:%M") + ", and should spawn " + \
                      expect_str + map_str + kubas_ch + "\n"
        return message