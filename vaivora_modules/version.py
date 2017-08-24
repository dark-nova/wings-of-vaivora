import re
from vaivora_modules.disclaimer import disclaimer

milestone   = "[m]"
unstable    = "[n]" # nightly
bugfix      = "[i]" # incremental

version_n   = []
subver_n    = []
hotfix_n    = []
status_n    = []
date_n      = []
changelog   = []

version_n.append('1')
subver_n.append('0')
hotfix_n.append('')
status_n.append(milestone)
date_n.append("2017/03/29")

rgx_brackets    =   re.compile(r'\[[imn]\]', re.IGNORECASE)
rgx_letter      =   re.compile(r'[a-z]', re.IGNORECASE)
#rgx_letter_pre  =   re.compile(r'[0-9]+pre-[0-9]+', re.IGNORECASE)

def check_revisions(srv_ver):
    if srv_ver == "[m]1.0":
        return len(version_n)-1

    if not srv_ver:
        return 0
    count             =   -1
    
    aversion, asubver =   srv_ver.split('.')
    
    letter_check      =   rgx_letter.search(asubver)
    if not letter_check:
        hotfix  =   ''
        subver  =   asubver
    else:
        hotfix = letter_check.group(0)
        subver = rgx_letter.sub('', asubver)

    version_check     =   rgx_brackets.match(aversion)
    status            =   version_check.group(0)
    version           =   rgx_brackets.sub('', aversion)

    while version_n[count]  >  version  or \
          subver_n[count]   >  subver   or \
          hotfix_n[count]   >  hotfix   or \
          (version_n[count] == version  and \
           subver_n[count]  == subver   and \
           hotfix_n[count]  == hotfix   and \
           compare_status(status_n[count], status)):
        count -= 1

    return count+1

def compare_status(status_a, status_b):
    if status_b == milestone and status_a != milestone:
        return True # stable > (incremental|nightly)
    if status_a == milestone:
        return False # status_b is not stable so always false
    if status_b == unstable and status_a == bugfix:
        return True
    if status_a == unstable:
        return False # ruled out status_a as "m"ilestone and status_b as "m"ilestone and "n"ightly
    else:
        return False # incrementals remaining; i == i but not i > i

def get_revisions():
    return len(version_n)

def get_subscription_msg():
    return "Remember, if you ever want to stop receiving these changelogs, type `$unsubscribe` in this DM.\n" + \
           "To receive changelogs again, just `$subscribe` back.\n"

def get_current_version():
    return status_n[-1] + version_n[-1] + "." + subver_n[-1] + hotfix_n[-1]


def get_header():
    return """```ini
[Version:] """ + get_current_version() + """
[Date:]    """ + date_n[-1] + """```"""


def get_index(st, v, su, h):
    z   = zip(status_n, version_n, subver_n, hotfix_n)
    for n, status, version, subver, hotfix in zip(range(len(version_n)), status_n, version_n, subver_n, hotfix_n):
        if st == status and v == version and su == subver and h == hotfix:
            return n
    return -1


def get_changelogs(idx=0):
    return changelog[idx:]


current     = get_header() + \
"""```diff
+ Added features:
  + 'Wings of Vaivora' has been rewritten using a separate module for constants. Performance should subsequently be higher.
  + The welcome message should now be clearer with a brighter display.

- Upcoming changes:
  + Previous modules will be migrated over to separate modules, like constants.
  + Talt Tracker will now be prioritized.
  + Custom settings, including the option to 'unsubscribe' from these notifications, will be implemented after.
  + Custom permissions will also be included.
```
"""

changelog.append(current)


version_n.append('1')
subver_n.append('1')
hotfix_n.append('')
status_n.append(milestone)
date_n.append("2017/04/09")

current     = get_header() + \
"""```diff
+ Added features:
  + 'Wings of Vaivora' has been rewritten fully with the constants module in place.

+ Fixes:
  + Squished some bugs related to the migration of modules.
  + Actually published this. Sorry for the delay on the downtime!

- Upcoming changes:
  + Talt Tracker to be developed next
  + Custom settings, including the option to 'unsubscribe' from these notifications, will be implemented after.
  + Custom permissions will also be included.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('1')
hotfix_n.append('a')
status_n.append(milestone)
date_n.append("2017/04/09")

current     = get_header() + \
"""```diff
+ Fixes:
  + Versioning corrected.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('1')
hotfix_n.append('b')
status_n.append(milestone)
date_n.append("2017/04/09")

current     = get_header() + \
"""```diff
+ Fixes:
  + Versioning _really_ corrected.
  + Several bugs related to file creation also fixed.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('1')
hotfix_n.append('c')
status_n.append(milestone)
date_n.append("2017/04/09")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed issues with databases not connecting.
  + Fixed issues with commands.
  + Stopped Wings of Vaivora from shouting changelogs everytime. (MAYBE.)
    * Thanks to Jiyuu for the feedback on all this.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('1')
hotfix_n.append('d')
status_n.append(milestone)
date_n.append("2017/04/10")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed issues with Deathweaver's map not recording.
    * Thanks to Term for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('2')
hotfix_n.append('')
status_n.append(milestone)
date_n.append("2017/04/10")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed issues with Deathweaver's map not recording. (For real!)
    + Corrected some other issues with the code. No more duplicate Deathweaver entries, for example.
  + Entries should be checked properly for time to prevent overlap.
    + New error message for overlapping times.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('2')
hotfix_n.append('a')
status_n.append(milestone)
date_n.append("2017/04/11")

current     = get_header() + \
"""```diff
+ Added features:
  + Changed the changelog delivery to server owners. Changelogs will come in separate messages. Apologies if you don't want notifications!

+ Fixes:
  + Fixed logic with missing/broken references -- imported all the relevant modules.
    + This may have impacted boss alerts. Sorry.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('2')
hotfix_n.append('b')
status_n.append(milestone)
date_n.append("2017/04/11")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed logic with record files (not databases) that kept deleting contents.
    + Sorry for the notifications. (Will be many like this for server owners... :( )
  + Fixed issuee with Deathweaver. You are now required to list map for Deathweaver.
    * Thanks to Term for the bug report, once again.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('2')
hotfix_n.append('c')
status_n.append(milestone)
date_n.append("2017/04/12")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed a misreferenced variable that caused issues with recording bosses.
    * Thanks to Kiito for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('2')
hotfix_n.append('d')
status_n.append(milestone)
date_n.append("2017/04/12")

current     = get_header() + \
"""```diff
+ Fixes:
  + Identified the issue linked to records not reporting within threshold of 15 mminutes.
    + Identified several other issues related to this.
      + The "no repeat" file used to archive announced records was repeatedly erased. I suppose I learned a lesson in "a" and "a+" file modes.
    * Thanks to Kiito for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('3')
hotfix_n.append('')
status_n.append(milestone)
date_n.append("2017/04/19")

current     = get_header() + \
"""```diff
+ Added features:
  + You can now query for boss aliases (less typing) and boss locations to scout for them better.
    * Thanks to Jiyuu for the feature request.

+ Fixes:
  + Migrated boss modules out of the main script, and began the process of developing custom settings.

- Upcoming changes:
  + Talt Tracker. For real!
  + Custom settings. This will be done by JSON within Python, most likely.
  + A way to send bug reports. This will take awhile, but I intend to bake this into the script.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('3')
hotfix_n.append('a')
status_n.append(milestone)
date_n.append("2017/04/19")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed issue with map and boss detection. Partial map names should now be interpreted correctly.
    * Thanks to Jiyuu for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('3')
hotfix_n.append('b')
status_n.append(milestone)
date_n.append("2017/04/20")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed potential issue with Kubas interfering with boss reporting.
  + Fixed issue with channel for world bosses not recording.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('3')
hotfix_n.append('c')
status_n.append(milestone)
date_n.append("2017/04/21")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed issue with Ellaganos not recording. Possibly some other bosses were impacted.
    * Thanks to Jiyuu and Wolfy for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('3')
hotfix_n.append('d')
status_n.append(milestone)
date_n.append("2017/04/21")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed issue with Ellaganos not recording. Possibly some other bosses were impacted.
    * Thanks to Jiyuu and Wolfy for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('4')
hotfix_n.append('')
status_n.append(milestone)
date_n.append("2017/04/21")

current     = get_header() + \
"""```diff
+ Added features:
  + Added "$subscribe" and "$unsubscribe" to DM commands.
    + You can subscribe to changelogs even if you're not a server owner.
  + Added a small status to show when things are ready.
    * Thanks to Jiyuu for the feature request.

+ Fixes:
  + Fixed issue with world bosses with no channel recorded as recorded as ch.0.

- Upcoming changes:
  + Talt T...I keep mentioning this.
  + Ways to fetch changelogs
  + Better help system, and DM commands including feedback
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('5')
hotfix_n.append('')
status_n.append(milestone)
date_n.append("2017/04/22")

current     = get_header() + \
"""```diff
+ Added features:
  + Added "$help" for commands. Give it a try in any channel or DM!

+ Fixes:
  + Added a small status to show when things are ready. Slightly better now.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('5')
hotfix_n.append('a')
status_n.append(milestone)
date_n.append("2017/04/23")

current     = get_header() + \
"""```diff
+ Fixes:
  + Corrected issue with specific deletions. Field boss records can now be deleted without issue.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('5')
hotfix_n.append('b')
status_n.append(milestone)
date_n.append("2017/04/23")

current     = get_header() + \
"""```diff
+ Fixes:
  + Corrected issue with adding to (un)subscriptions.
    * Thanks to Wolfy for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('5')
hotfix_n.append('c')
status_n.append(milestone)
date_n.append("2017/05/08")

current     = get_header() + \
"""```diff
+ Fixes:
  + Corrected issue with recording bosses on multiple channels.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('5')
hotfix_n.append('d')
status_n.append(milestone)
date_n.append("2017/05/15")

current     = get_header() + \
"""```diff
+ Fixes:
  + Corrected issue with some commands not printing.
    + Subsequently, you may reeceive more than 1 message/response when you ask for help on a command.
      * Thanks to Onesan for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('5')
hotfix_n.append('e')
status_n.append(milestone)
date_n.append("2017/05/19")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed argument count check. Preparing to condense some modules later for code clarity. Open Source SoonTM
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('5')
hotfix_n.append('f')
status_n.append(milestone)
date_n.append("2017/05/19")

current     = get_header() + \
"""```diff
+ Fixes:
  + Revert previous "fix".
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('5')
hotfix_n.append('g')
status_n.append(milestone)
date_n.append("2017/06/06")

current     = get_header() + \
"""```diff
+ Fixes:
  + Removed @here notification in preparation of custom setting. For now, you may use a role called "Boss Hunter" (caps important).
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('')
status_n.append(milestone)
date_n.append("2017/06/07")

current     = get_header() + \
"""```diff
+ Added features:
  + Check out the new Settings module! [$settings help] for more info.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('a')
status_n.append(milestone)
date_n.append("2017/06/07")

current     = get_header() + \
"""```diff
+ Fixes:
  + Corrected issues with Talt Tracker.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('b')
status_n.append(milestone)
date_n.append("2017/06/07")

current     = get_header() + \
"""```diff
+ Fixes:
  + Corrected issues with Talt Tracker: issues with individual permission comparison fixed.
    * Thanks to Sunshine for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('c')
status_n.append(milestone)
date_n.append("2017/06/07")

current     = get_header() + \
"""```diff
+ Fixes:
  + Added `$settings help`.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('d')
status_n.append(milestone)
date_n.append("2017/06/09")

current     = get_header() + \
"""```diff
+ Fixes:
  + Corrected an issue with field boss entries not recording when map is omitted.
    * Thanks to Wolfy for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('e')
status_n.append(milestone)
date_n.append("2017/06/10")

current     = get_header() + \
"""```diff
+ Added features:
  + Talt verification is now in place.
    + $settings verify|validate [@user ...]
    + $settings unverify|invalidate [@user ...]
    + Leave the mentions blank to mass (in)validate. Suitable only for "Authorized" roles only.
  + Changed an easter egg.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('f')
status_n.append(milestone)
date_n.append("2017/06/10")

current     = get_header() + \
"""```diff
+ Fixes:
  + Corrected logic issue with assigning permissions.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('g')
status_n.append(milestone)
date_n.append("2017/06/10")

current     = get_header() + \
"""```diff
+ Added features:
  + Correctly mentions people in "boss" specific features, if assigned "boss" role.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('h')
status_n.append(milestone)
date_n.append("2017/06/10")

current     = get_header() + \
"""```diff
+ Fixes:
  + Identified and fixed issue with adding Talt for others. Was impromperly recorded to command user, not the target.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('i')
status_n.append(milestone)
date_n.append("2017/06/10")

current     = get_header() + \
"""```diff
+ Added features:
  + "$settings get talt all" - to get all your guild's contribution
  + "$settings reset talt [@user ...]" - to reset a user's contribution (to fix)
  + "$settings rebase" - to rebuild Talt levels if you think something's wrong

+ Fixes:
  + Corrected issue with Guild Level corresponding to Talt.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('j')
status_n.append(bugfix)
date_n.append("2017/06/11")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed issues with member level & Talt contribution.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('k')
status_n.append(bugfix)
date_n.append("2017/06/11")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed issues with mentions on boss notice.
    * Thanks to Galoal for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('l')
status_n.append(bugfix)
date_n.append("2017/06/11")

current     = get_header() + \
"""```diff
+ Added features:
  + Change release system from [milestone, nightly] to [milestone, nightly, bugfix]
+ Fixes:
  + Adjusted logic for mentioning group or users with boss alerts.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('m')
status_n.append(bugfix)
date_n.append("2017/06/14")

current     = get_header() + \
"""```diff
+ Fixes:
  + Adjusted logic for mentioning group or users with boss alerts. For real this time.
    + Please message Nova#6732 if you've had issues with this so it can be corrected.
    * Thanks to Wolfy for the bug report and additional testing.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('n')
status_n.append(milestone)
date_n.append("2017/06/15")

current     = get_header() + \
"""```diff
+ Added features:
  + Better output for Talt commands.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('o')
status_n.append(bugfix)
date_n.append("2017/06/15")

current     = get_header() + \
"""```diff
+ Added features:
  + Changed the vocabulary of "add"ing and "set"ting Talt.
    + $settings set talt ... ; sets target's Talt directly.
    + $settings add talt ... ; the former behavior of "set talt"; adds Talt.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('p')
status_n.append(bugfix)
date_n.append("2017/06/15")

current     = get_header() + \
"""```diff
+ Fixes:
  + Corrected old boss record printing completely.
    * Thanks to Wolfy for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('q')
status_n.append(bugfix)
date_n.append("2017/06/18")

current     = get_header() + \
"""```diff
+ Fixes:
  + Corrected an issue with "anchor" keyword for "$boss".

- Upcoming changes:
  + Code rewrite before publishing as open source. Estimated time: 1-2 weeks
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('6')
hotfix_n.append('r')
status_n.append(bugfix)
date_n.append("2017/06/28")

current     = get_header() + \
"""```diff
+ Fixes:
  + Server join issue.
  + Talt Tracker issue for setting remainder Talt via "$settings set (0-20) (current points)".
    + Send a DM to Nova#6732 if you've had issues with the Talt Tracker module.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('a')
status_n.append(unstable)
date_n.append("2017/07/01")

current     = get_header() + \
"""```diff
--- Formerly known as svn 2pre-1 ---
+ Added features:
  + Migrated boss module files together, mostly.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('b')
status_n.append(bugfix)
date_n.append("2017/07/06")

current     = get_header() + \
"""```diff
--- Formerly known as svn 2pre-2 ---
+ Added features:
  + Boss module has been fully re-written.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('c')
status_n.append(milestone)
date_n.append("2017/07/07")

current     = get_header() + \
"""```diff
--- Formerly known as svn 2pre-3 ---
+ Added features:
  + Boss module has been fully re-written.
  + DB module has been re-written, partially. Probably won't need to re-write this in full.

+ Fixes:
  + Corrected issues with boss module after rewrite.

- Upcoming changes:
  + Settings module re-write.
  + Open source Vaivora later
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('d')
status_n.append(milestone)
date_n.append("2017/07/07")

current     = get_header() + \
"""```diff
+ Fixes:
  + Apologies for the multiple changes to Wings of Vaivora. You may receive fewer notifications now.

- Reminder: you can unsubscribe using "$unsubscribe" in this DM.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('e')
status_n.append(milestone)
date_n.append("2017/07/08")

current     = get_header() + \
"""```diff
+ Added features:
  + Alerts will no longer use a redundant measure of text files in raw info to prevent repeat of duplicate mentions. And... (see Fixes)
  
+ Fixes:
  + Alerts are now fixed. Sorry. This was long overdue and I've had issues and was occupied today. This was a couple issues:
    1. not converting local time (Pacific Daylight Time) to server time (Eastern Daylight Time) - solved using timedelta(hours=-3)
    2. not sending to the right channel, instead a str which discord.py made no sense of - solved using channel.id
    3. not sending messages after input - solved using message.server instead of server_id
    4. not sending messages on account of syntax/type error - solved by typing to str

- Caveat to new alert/periodic check system: if bot goes offline and you had a record still valid, you will receive at least one duplicate mention. -
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('f')
status_n.append(bugfix)
date_n.append("2017/07/08")

current     = get_header() + \
"""```diff
+ Fixes:
  + Alerts are now fixed for a couple more issues.
    1. handling 12pm - solved using hour > 24 instead of hour > 23
    2. handling empty maps - solved by assigning an unbound variable on the condition
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('g')
status_n.append(bugfix)
date_n.append("2017/07/08")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed logic errors with getting changelogs. Sorry, I know you guys must have gotten too many changelogs lately through PM, mostly repetitive.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('h')
status_n.append(bugfix)
date_n.append("2017/07/08")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed logic errors with empty maps again -resolved with changing list with "Map Unknown" to empty string
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('i')
status_n.append(bugfix)
date_n.append("2017/07/08")

current     = get_header() + \
"""```diff
+ Fixes:
  + Adjusted anchor message using boss list
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('j')
status_n.append(bugfix)
date_n.append("2017/07/20")

current     = get_header() + \
"""```diff
+ Fixes:
  + Set exception handling for emojis to prevent total bot failure
  + Adjusted 12:00am as a time
    * Thanks to Wolfy for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('k')
status_n.append(bugfix)
date_n.append("2017/07/28")

current     = get_header() + \
"""```diff
+ Fixes:
  + Set exception handling for tracking repeat messages
+ Added featurse:
  + Added Abomination anchor option. [$boss abom anchored 0:00] produces an alert 1 hour from the anchor time.
    * Thanks to Wolfy for the request.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('l')
status_n.append(milestone)
date_n.append("2017/07/31")

current     = get_header() + \
"""```diff
+ Added featurse:
  + Adjusted field bosses and added two new records corresponding to "Alluring Succubus" and "Frantic Molich". Times are still hypothetical until the update arrives.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('m')
status_n.append(bugfix)
date_n.append("2017/08/01")

current     = get_header() + \
"""```diff
+ Fixes:
  + Adjusted time to spawn for lesser field bosses.
    * Thanks to Wolfy for the contribution.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('n')
status_n.append(bugfix)
date_n.append("2017/08/01")

current     = get_header() + \
"""```diff
+ Fixes:
  + Adjusted time to spawn for Demon Lords.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('o')
status_n.append(bugfix)
date_n.append("2017/08/01")

current     = get_header() + \
"""```diff
+ Fixes:
  + Adjusted time to spawn for Demon Lords (for real now; issue was unnoticed arithmetic with regular time)
  + $boss help works now
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('p')
status_n.append(bugfix)
date_n.append("2017/08/02")

current     = get_header() + \
"""```diff
+ Fixes:
  + Changed Demon Lord grouping
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('q')
status_n.append(bugfix)
date_n.append("2017/08/02")

current     = get_header() + \
"""```diff
+ Fixes:
  + Changed Demon Lord spawns for real -- I should really just re-evaluate myself
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('r')
status_n.append(bugfix)
date_n.append("2017/08/02")

current     = get_header() + \
"""```diff
+ Fixes:
  + What is time? Seven hours, thirty minutes? Seven hours, twenty minutes? Seven hours, ten minutes? Seven hours?
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('s')
status_n.append(bugfix)
date_n.append("2017/08/03")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed 12pm errors.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('t')
status_n.append(bugfix)
date_n.append("2017/08/08")

current     = get_header() + \
"""```diff
+ Fixes:
  + Punctuation single quote

I have been really busy with life. I don't think I can maintain this project as much as I could before, and I've also had issues motivating myself with this project.

I will have the source readily available, at least one iteration of Wings of Vaivora, once I have completed rewriting Settings. Please bear with me. I know it's been a long while, and for those who may want to look into the code, I'm just one person maintaining everything.

Thank you.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('u')
status_n.append(bugfix)
date_n.append("2017/08/08")

current     = get_header() + \
"""```diff
+ Fixes:
  + Channel setting
    * Thanks to Jiyuu for the bug report.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('7')
hotfix_n.append('v')
status_n.append(bugfix)
date_n.append("2017/08/09")

current     = get_header() + \
"""```diff
+ Fixes:
  + World boss timers are back
    * Thanks to Donada for the request.
  + Demon Lord set A spawns fixed (Inner Wall District 8, etc)
    * Thanks to Jiyuu, Wolfy, and beeju for the bug reports.
```"""

changelog.append(current)



version_n.append('1')
subver_n.append('8')
hotfix_n.append('')
status_n.append(milestone)
date_n.append("2017/08/23")

current     = get_header() + \
"""```diff
--- Major Revision ---
+ Added features:
  + Settings has been fully rewritten, so that means I can push this as open source.
- Github: https://github.com/dark-nova/wings-of-vaivora
  + Some "fun" easter eggs had to be removed to follow the new Discord Bot API.
  + Similarly, please pay attention to the notice at the bottom of this.
    + I know this will bother some of you who have unsubscribed, but this will be done once.
  + Boss timers should now be sorted by time descending.
    * Thanks to Jiyuu for the feature request.

+ Fixes:
  + Corrected an unmentioned bug with wrong argument position for `$boss`

Thank you for putting up with this project. -- Nova#6732
```""" + disclaimer

changelog.append(current)



version_n.append('1')
subver_n.append('8')
hotfix_n.append('a')
status_n.append(bugfix)
date_n.append("2017/08/23")

current     = get_header() + \
"""```diff
+ Fixes:
  + Fixed issue with boss role in settings
    * Thanks to Jiyuu for the bug report.
  + Closed an open condition that led to exceptions
```""" + disclaimer

changelog.append(current)



version_n.append('1')
subver_n.append('8')
hotfix_n.append('b')
status_n.append(bugfix)
date_n.append("2017/08/23")

current     = get_header() + \
"""```diff
+ Fixes:
  + Identified an issue with discord.py ids no longer having identifying punctuation, and fixed with a workaround
```""" + disclaimer

changelog.append(current)



version_n.append('1')
subver_n.append('8')
hotfix_n.append('c')
status_n.append(bugfix)
date_n.append("2017/08/24")

current     = get_header() + \
"""```diff
+ Fixes:
  + Corrected more things (boss module specifically) with unresolved id changes
  + Began removing some files for uniform use (secrets go into secrets.py; example file on github in vaivora_modules)
```""" + disclaimer

changelog.append(current)
