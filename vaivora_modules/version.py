milestone   = "[m]"
unstable    = "[n]" # nightly

# to change
version_n   = 1
subver_n    = 0
hotfix_n    = ''
status_now  = milestone # or unstable

# syntax: [m|n][0-9].[0-9].[a-z]
version     = status_now + str(version_n) + "." + \
              str(subver_n) + hotfix_n
version_l   = version # uncomment below line if nightly/unstable version is in development
#version_l   =

changelog   = list()

# follow format like below - reassign "current" and append again to "changelog"
current     = \
"""
```ini
[Version:]""" + version + """\n
[Latest:] """ + version_l + """\n
[Date:]   """ + "2017/03/29" + """\n
```
```diff
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