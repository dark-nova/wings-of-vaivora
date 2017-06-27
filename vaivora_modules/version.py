milestone   = "[m]"
unstable    = "[n]" # nightly
bugfix      = "[b]" # incremental

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

def check_revisions(srv_ver):
    count   = -1
    srv_ver = srv_ver.split('.')

    if not srv_ver[1][0:-1]:
        hotfix = ''
        subver = srv_ver[1]
    else:
        hotfix = srv_ver[1][-1]
        subver = srv_ver[1][0:-1]

    while version_n[count]  >  srv_ver[0][1:]   or \
          subver_n[count]   >  subver           or \
          hotfix_n[count]   >  hotfix           or \
          (version_n[count] == srv_ver[0][1:]   and \
           subver_n[count]  == subver           and \
           hotfix_n[count]  == hotfix           and \
           status_n[count]  <= srv_ver[0][0]):
        count -= 1

    return (count+1)

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
+ Upcoming changes:
  + Code rewrite before publishing as open source. Estimated time: 1-2 weeks
```"""

changelog.append(current)
