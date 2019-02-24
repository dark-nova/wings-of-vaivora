import constants.settings
#from constants.settings import en_us as lang_settings

### DO NOT CHANGE/TRANSLATE THIS FILE ###

SQL_SELECT = 'select *'
#SQL_SELECT_COUNT = 'select count(*)'
SQL_DELETE = 'delete'
SQL_AND = 'and'
SQL_WHERE = 'where'
SQL_FROM_BOSS = 'from boss'
SQL_WHERE_NAME = 'name=?'
SQL_WHERE_MAP = 'map=?'
SQL_WHERE_CHANNEL = 'channel=?'
SQL_FROM_BOSS_DEFAULT = 'from boss where name=?'
SQL_ORDER = 'order by year desc, month desc, day desc, hour desc, minute desc'
SQL_UPDATE = 'insert into boss values (?,?,?,?,?,?,?,?,?,?)'

SQL_FROM_ROLES = 'from roles'
# role {} can be "member", "authorized", "s-authorized"
COL_SQL_FROM_ROLES = 'select mention from roles where role = "{}"'
SQL_FROM_CHANS = 'from channels'
# type {} can be "boss" or "settings"
COL_SQL_FROM_CHANS = 'select channel from channels where type = "{}"'
SQL_FROM_GUILD = 'from guild'
COL_SQL_FROM_GUILD = 'select {} from guild' # {} can be level or points
SQL_FROM_CONTR = 'from contribution'
SQL_FROM_CONTR_USER = 'select points from contribution where userid = "{}"'
SQL_FROM_OFFSET = 'from offset'
SQL_FROM_SETS = [
    SQL_FROM_ROLES,
    SQL_FROM_CHANS,
    SQL_FROM_GUILD,
    SQL_FROM_CONTR,
    SQL_FROM_OFFSET
    ]

SQL_CLEAN_TABLES = [
    'roles',
    'channels',
    'contribution'
    ]

SQL_CLEAN = {}
SQL_CLEAN['roles'] = 'role, mention' # COL_SETS_ROLES
SQL_CLEAN['channels'] = 'type, channel' # COL_SETS_CHANS
SQL_CLEAN['contribution'] = 'userid, points' # COL_SETS_CONTR

SQL_DROP_OWNER = 'drop table if exists owner'
SQL_DROP_CHANS = 'drop table if exists channels'
SQL_MAKE_OWNER = 'create table owner(id text)'
SQL_MAKE_CHANS = 'create table channels(type text, channel integer)'
SQL_UPDATE_OWNER = 'insert into owner values("{}")'
SQL_SAUTH_OWNER = 'insert into roles values("{}", "{}")'
SQL_GET_OLD_OWNER = 'select * from owner'
SQL_DEL_OLD_OWNER = ("""delete from roles where role = '"""
    + constants.settings.ROLE_SUPER_AUTH
    + """' and mention = '{}'""")

SQL_SET_CHANNEL = 'insert into channels values("{}", "{}")'

SQL_CLEAN_DUPES = """delete from {0} where rowid not in
(select min(rowid) from {0} group by {1})"""

MOD_BOSS = 'boss'
MOD_SETS = 'settings'
DIR = 'db/'
EXT = '.db'

TIME = 'Time'

COL_TIME_YEAR = 'year'
COL_TIME_MONTH = 'month'
COL_TIME_DAY = 'day'
COL_TIME_HOUR = 'hour'
COL_TIME_MINUTE = 'minute'

COL_BOSS_NAME = 'name'
COL_BOSS_CHANNEL = 'channel'
COL_BOSS_MAP = 'map'
COL_BOSS_STATUS = 'status'
COL_BOSS_TXT_CHANNEL = 'text_channel'

COL_SETS_ROLES = ('role', 'mention')
COL_SETS_CHANS = ('type', 'channel')
COL_SETS_GUILD = ('level', 'points')
COL_SETS_CONTR = ('userid', 'points')
COL_SETS_OFFSET = ('hours',)

SQL_TYPE_INT = 'integer'
SQL_TYPE_TEXT = 'text'

### DO NOT CHANGE/TRANSLATE THIS FILE ###
