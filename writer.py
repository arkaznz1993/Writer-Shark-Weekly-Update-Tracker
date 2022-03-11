from database import DatabaseConnector


class Writer:
    database_connection = DatabaseConnector()
    all_writers = []
    writer_ids = []

    def __init__(self, trello_id: str, name: str, daily_word_count: int, leaves: int, team: str):
        self.id = trello_id
        self.name = name
        self.daily_word_count = daily_word_count
        self.leaves = leaves
        self.team = team
        self.leave_count = 0
        self.word_count = 0
        self.target = 0
        self.remarks = ''

        Writer.all_writers.append(self)
        Writer.writer_ids.append(self.id)

    def update_leaves_in_account(self):
        Writer.database_connection.deduct_leaves([self.leaves, self.id])

    @staticmethod
    def instantiate_from_db_list():
        db_rows = Writer.database_connection.get_writers()
        for row in db_rows:
            Writer(row[0], row[1], row[2], row[3], row[4])

    @staticmethod
    def find_writer(writer_id):
        for writer in Writer.all_writers:
            if writer.id == writer_id:
                return writer

    @staticmethod
    def deduct_leaves(list_of_leaves):
        writer_id = list_of_leaves[0][0]
        writer = Writer.find_writer(writer_id)
        if writer is not None:
            writer.leaves -= len(list_of_leaves)
        return writer

    @staticmethod
    def update_leave_count(target_week):
        leave_count_rows = Writer.database_connection.return_leave_count_current_week(target_week)
        for leave_count in leave_count_rows:
            writer = Writer.find_writer(leave_count[0])
            if writer is not None:
                writer.leave_count = leave_count[1]

    @staticmethod
    def reset_word_count():
        for writer in Writer.all_writers:
            writer.word_count = 0

    @staticmethod
    def update_word_count(target_week):
        word_count_rows = Writer.database_connection.return_word_count_target_week(target_week)
        print(word_count_rows)
        for trello_id, wordcount in word_count_rows:
            writer = Writer.find_writer(trello_id)
            if writer is not None:
                writer.word_count = wordcount
                print(writer.name, writer.word_count)
            else:
                print(f'HOLA: {trello_id, wordcount}')

    @staticmethod
    def update_target(current_week):
        values = []
        for writer in Writer.all_writers:
            writer.target = (len(current_week) - writer.leave_count) * writer.daily_word_count
            values.append((writer.id, current_week[0], current_week[-1], writer.word_count, writer.target, writer.team))

        Writer.database_connection.insert_weekly_update(values)

    @staticmethod
    def update_target_previous_week(previous_week):
        values = []
        for writer in Writer.all_writers:
            values.append((writer.word_count, writer.id, previous_week[0], previous_week[-1]))

        Writer.database_connection.update_previous_week(values)
