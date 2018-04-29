# Wings of Vaivora

## Boss Module

### Usage:
+ $boss <target> <status> <time> [<channel>] [<map>]
+ $boss <target> (<entry> [<channel>] | <query> | <type>)
+ $boss help

### Examples:
+ $boss cerb died 12:00pm mok
    - Means: "Violent Cerberus" died in "Mokusul Chamber" at 12:00PM server time.
    - Omit channels for field bosses.

+ $boss crab died 14:00 ch2
    - Means: "Earth Canceril" died in "Royal Mausoleum Constructors' Chapel" at 2:00PM server time.
    - You may omit channel for world bosses.

+ $boss all erase
    - Means: Erase all records unconditionally.

+ $boss nuaele list
    - Means: List records with "[Demon Lords: Nuaele, Zaura, Blut]".

+ $boss rexipher erase
    - Means: Erase records with "[Demon Lords: Mirtis, Rexipher, Helgasercle, Marnox]".

+ $boss crab erase ch2
    - Means: Erase records with "Earth Canceril" but only for CH 2.

+ $boss crab maps
    - Means: Show maps where "Earth Canceril" may spawn.

+ $boss crab alias
    - Means: Show aliases for "Earth Canceril", of which "crab" is an alias

### Options:
+ <target>
    - This can be either "all" or part of the single boss's name. e.g. "cerb" for "Violent Cerberus"
    - "all" will always target all valid bosses for the command. The name (or part of it) will only target that boss.
    - Some commands do not work with both. Make sure to check which command can accept what <target>.

+ <status>
    - This refers to specific conditions related to a boss's spawning.
    - Options:
        * "died": to refer a known kill
        * "anchored": to refer a process known as anchoring for world bosses
    - <target> cannot be "all".

+ <entry>
    - This subcommand allows you to manipulate existing records.
    - Options:
        * "list": to list <target> records
        * "erase": to erase <target> records
    - <target> can be any valid response.

+ <query>
    - This subcommand supplies info related to a boss.
    - Options:
        * "maps": to show where <target> may spawn
        * "alias": to list possible short-hand aliases, e.g. "ml" for "Noisy Mineloader", to use in <target>
    - <target> cannot be "all".

+ <type>
    - This subcommand returns a list of bosses assigned to a type.
    - Options:
        * "world": bosses that can spawn across all channels in a particular map; they each have a gimmick to spawn
        * "event": bosses/events that can be recorded; usually time gimmick-related
        * "field": bosses that spawn only in CH 1; they spawn without a separate mechanism/gimmick
        * "demon": Demon Lords, which also count as field bosses; they have longer spawn times and the server announces everywhere prior to a spawn
    - <target> must be "all".

#### File last modified: 2018-04-29 11:47 (UTC-7)
