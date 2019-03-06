# Wings of Vaivora

## Gems Module

### Usage
+ $gems exp `<abrasive>` `<abrasive>`...
+ $gems gem2lv `<gem-level>` `<gem-exp>` `<final-level>`
+ $gems help

### Examples
+ $gems exp 2x2 3x4
    - Means: Calculate total gem experience using 2 level 2 and 3 level 4 gem abrasives.
+ $gems gem2lv 1 0 5
    - Means: Calculate gem experience needed to level a level 1, 0 experience gem to a level 5.

### Options
+ exp
    - The function to calculate how much gem experience you can get from any number of abrasives.
    - Aliases: `experience`, `abrasives`, `abrasive`

+ `<abrasive>`
    - A format like QTY.LV, where QTY is quantity and LV is level of the abrasive.
    - You must include either '.' or 'x' to separate the two numbers.
    - `$gems exp` accepts 1 or more of this argument.

+ gem2lv
    - The function to show much gem experience you need to level a gem from its current level to a desired level.
    - Aliases: `gem2level`

+ `<gem-level>`
    - The current gem level. Ranges from 1 to 9, for the purpose of this program.

+ `<gem-exp>`
    - The current gem experience listed in the gem's UI. Ranges from 0 to 1 below its current maximum.

+ `<final-level>`
    - The final level to achieve. Must be higher than `<gem-level>` and between 2 to 9.

+ help
    - Prints this page.

#### File last modified: 2019-03-05 16:15 (UTC-8)
