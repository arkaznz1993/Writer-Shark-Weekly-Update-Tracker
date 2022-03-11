from google_service import calendar_sheet
from shark_calendar import get_current_week, get_leaves
from writer import Writer


def main(data, context):
    Writer.instantiate_from_db_list()

    get_holidays = calendar_sheet.get_values('Holidays!A2:A')
    get_week_start_end_values = calendar_sheet.get_values('Work Weeks!A2:B')
    leaves = calendar_sheet.get_values('Leave Record!A3:D')

    leaves_to_be_inserted = get_leaves(leaves, get_holidays)

    if len(leaves_to_be_inserted) > 0:
        for leaves_per_writer in leaves_to_be_inserted:
            Writer.database_connection.insert_leaves(leaves_per_writer)
            writer_object = Writer.deduct_leaves(leaves_per_writer)
            writer_object.update_leaves_in_account()

        calendar_sheet.clear_values('Leave Record!A3:D')

    this_week = get_current_week(get_week_start_end_values, get_holidays)

    Writer.update_leave_count(this_week)
    Writer.update_word_count(this_week)
    Writer.update_target(this_week)

    Writer.reset_word_count()

    last_week = Writer.database_connection.get_previous_week(this_week)

    if len(last_week) > 0:
        Writer.update_word_count(last_week)
        Writer.update_target_previous_week(last_week)

    Writer.database_connection.connection.close()


if __name__ == '__main__':
    main('', '')
