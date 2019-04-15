import asyncio
import re

import pendulum

import constants.boss


nonalnum = re.compile('[^A-Za-z0-9 -]')


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


async def validate_date(date):
    """
    :func:`validate_date` validates whether a string representing date is valid
    or not, returning a standardized one.

    Args:
        date (str): the date str to check

    Returns:
        list: of ints (year, month, day); or
        None if invalid
    """
    delims = ['.', '/', '-']
    for delim in delims:
        split_date = date.split(delim)
        if len(split_date) != 3:
            continue
        else:
            date_list = [int(_d) for _d in split_date]
            end = pendulum.datetime(*date_list)
            now = pendulum.now()
            time_diff = now - end
            # reject events that have already ended
            if time_diff.seconds <= 0:
                return None
            else:
                return date_list

    # nothing was validated
    return None


async def sanitize_nonalmum(text: str):
    """
    :func:`sanitize_nonalnum` removes all non-alphanumeric characters.
    Spaces and hyphens are valid.

    Args:
        text (str): the text to sanitize

    Returns:
        str: a sanitized string
    """
    return nonalnum.sub('', text)
