from datetime import datetime, timedelta
from pytz import timezone
import constants


def is_holiday(date, holidays_list):
    if date.isoweekday() == 7:
        return True
    for hol in holidays_list:
        holiday = datetime.strptime(hol[0], constants.DATE_FORMAT)
        if holiday.year == date.year:
            if holiday.month == date.month:
                if holiday.day == date.day:
                    return True
    return False


def get_current_week(week_start_end_values, holidays):
    now = datetime.now(timezone('Asia/Kolkata'))
    now = now.strftime(constants.DATE_FORMAT)
    now = datetime.strptime(now, constants.DATE_FORMAT)

    for value in week_start_end_values:
        week_start = datetime.strptime(value[0], constants.DATE_FORMAT)
        week_end = datetime.strptime(value[1], constants.DATE_FORMAT)
        week_end = week_end.replace(hour=19, minute=30)
        if week_start <= now <= week_end:
            date_start = week_start
            current_week = []
            while date_start <= week_end:
                if not is_holiday(date_start, holidays):
                    current_week.append(date_start)
                date_start += timedelta(days=1)
            current_week[-1] = week_end
            return current_week


def get_previous_week(week_start_end_values, current_week, holidays):
    current_week_start = current_week[0]
    for value in week_start_end_values:
        week_start = datetime.strptime(value[0], constants.DATE_FORMAT)
        week_end = datetime.strptime(value[1], constants.DATE_FORMAT)
        week_end = week_end.replace(hour=19, minute=30)
        if week_start < current_week_start <= week_end:
            date_start = week_start
            current_week = []
            while date_start <= week_end:
                if not is_holiday(date_start, holidays):
                    current_week.append(date_start)
                date_start += timedelta(days=1)
            current_week[-1] = week_end
            return current_week


def get_leaves(leave_records, holidays):
    leaves_to_be_inserted = []
    for leave_record in leave_records:
        leave_start = datetime.strptime(leave_record[2], constants.DATE_FORMAT)
        if len(leave_record) < 4:
            leave_end = leave_start
        else:
            leave_end = datetime.strptime(leave_record[3], constants.DATE_FORMAT)

        date_start = leave_start

        leaves_per_writer = []

        while date_start <= leave_end:
            if not is_holiday(date_start, holidays):
                leaves_per_writer.append((leave_record[1], date_start))
            date_start += timedelta(days=1)

        leaves_to_be_inserted.append(leaves_per_writer)

    return leaves_to_be_inserted
