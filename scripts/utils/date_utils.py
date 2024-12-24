import holidays
from datetime import datetime, timedelta


def get_previous_workday_with_holidays(country='CN'):
    today = datetime.today()
    cn_holidays = holidays.CountryHoliday(country)

    offset = (today.weekday() - 4) % 7 + 1 if today.weekday() == 0 else 1
    previous_workday = today - timedelta(days=offset)

    while previous_workday.weekday() >= 5 or previous_workday in cn_holidays:
        previous_workday -= timedelta(days=1)

    return previous_workday.strftime('%Y-%m-%d')