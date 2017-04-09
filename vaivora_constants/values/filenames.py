#vaivora_constants.values.filenames

wings       = "wings-"
txt         = ".txt"
log         = ".log"
tmp         = ".tmp"

logger      = wings + "logger"

valid_db    = wings + "valid_db"    + txt
valid_db_t  = wings + "valid_db"    + tmp
no_repeat_t = wings + "no_repeat"
no_repeat   = no_repeat_t           + txt
welcomed    = wings + "welcomed"    + txt
welcomed_t  = wings + "welcomed"    + tmp

log_file    = logger                + log
debug_file  = wings + "debug"       + log
