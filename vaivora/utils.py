import asyncio
import re

import constants.boss

async def validate_time(time):
    """
    :func:`validate_time` validates whether a string representing time is valid
    or not, returning a standardized one.

    Args:
        time (str): the time str to check

    Returns:
        str: a standardized time unit, e.g. 0:00 (midnight) or 13:00 (1 PM); or
        None if invalid
    """
    if not constants.boss.REGEX_TIME.match(time):
        return None

    offset = 0

    # e.g. 900 (or 9:00)
    if constants.boss.REGEX_TIME_DIGITS.match(time):
        minutes = constants.boss.REGEX_TIME_MINUTES.match(time).group(1)
        hours = re.sub(minutes, '', time)
        return constants.boss.TIME.format(hours, minutes)
    # e.g. 12:00 am (or 0:00)
    elif constants.boss.REGEX_TIME_AMPM.search(time):
        if constants.boss.REGEX_TIME_PM.search(time):
            if constants.boss.REGEX_TIME_NOON.match(time):
                offset -= 12
            offset += 12
        else:
            if constants.boss.REGEX_TIME_NOON.match(time):
                offset -= 12
        time = constants.boss.REGEX_TIME_AMPM.sub('', time)

    delim = constants.boss.REGEX_TIME_DELIM.search(time)
    hours, minutes = [int(t) for t in time.split(delim.group(0))]
    hours += offset

    if hours >= 24 or hours < 0:
        return None

    return constants.boss.TIME.format(str(hours).rjust(2, '0'),
                                      str(minutes).rjust(2, '0'))