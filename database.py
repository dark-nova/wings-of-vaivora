import sqlite3

class TOS_DB:
    
    def __init__(self, db_str):
        self.db_str = db_str


    # @func:      create_discord_db(Discord.server.str, func, *)
    # @arg:
    #   discord_server: the discord server's id
    #   db_func:        a database function
    #   xargs:          extra arguments
    # @return:
    #   Relevant data if successful, False otherwise
    async def func_discord_db(discord_server, db_func, xargs=None):
        if rx['str.ext.db'].search(discord_server):
            discord_db = discord_server
        elif rx['str.fnm.db'].search(discord_server):
            discord_db = discord_server + ".db"
        else:
            return False # invalid name
        conn = sqlite3.connect(discord_db)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if not os.path.isfile(discord_db):
            await create_discord_db(c)
            return False # not initialized
        elif not callable(db_func):
            return False
        # implicit else
        if xargs and not db_func is rm_ent_boss_db:
            dbif  = await db_func(c, xargs)
        elif type(xargs) is str:
            dbif  = await db_func(c, bn=xargs)
        elif type(xargs) is tuple:
            dbif  = await db_func(c, bn=xargs[0], ch=xargs[1])
        elif type(xargs) is dict:
            dbif  = await db_func(c, bd=xargs)
        else:
            dbif  = await db_func(c)
        conn.commit()
        conn.close()
        return dbif