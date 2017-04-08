milestone   = "[m]"
unstable    = "[n]" # nightly

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
    count   = 0
    srv_ver = srv_ver.split('.')

    if not srv_ver[1][0:-1]:
        hotfix = ''
        subver = srv_ver
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

    return count


def get_current_version():
    return status_n[count] + version_n[count] + "." + subver_n[count] + hotfix_n[count]


def get_header():
    return """
    ```ini
    [Version:] """ + get_current_version() + """\n
    [Date:]    """ + date_n[count] + """\n
    ```
    """


def get_index(st, v, su, h):
    z   = zip(status_n, version_n, subver_n, hotfix_n)
    for n, status, version, subver, hotfix in zip(range(len(version_n)), status_n, version_n, subver_n, hotfix_n):
        if st == status and v == version and su == subver and h == hotfix:
            return n
    return count


def get_changelogs(idx=0):
    return '\n'.join(changelog[idx:])


current     = get_header() + \
"""
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



# version_n.append('')
# subver_n.append('')
# hotfix_n.append('')
# status_n.append(milestone) # or nightly
# date_n.append("2017/12/12")

# version     = status_now + str(version_n) + "." + \
#               str(subver_n) + hotfix_n
# version_l   = version # uncomment below line if nightly/unstable version is in development

# header     = \
# """
# ```ini
# [Version:]""" + status_n[count] + version_n[count] + "." + subver_n[count] + hotfix_n[count] + """\n
# [Date:]   """ + date_n[count] + """\n
# ```
# """