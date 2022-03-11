import os
import mysql.connector
from mysql.connector.constants import ClientFlag

# Instance name - flash-hour-338103:asia-south1:test-sql-server

config = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': '35.200.140.194',
    'client_flags': [ClientFlag.SSL],
    'ssl_ca': os.environ.get('SSL_CA'),
    'ssl_cert': os.environ.get('SSL_CERT'),
    'ssl_key': os.environ.get('SSL_KEY'),
    'database': os.environ.get('DB_NAME'),
}

GET_WRITERS = 'SELECT TrelloId, Name, DailyWordCount, Leaves, Team ' \
              'FROM Writers ' \
              "WHERE WriterStatus = 'Current'"

INSERT_LEAVES = 'INSERT INTO LeaveRecord (' \
                'TrelloId, Date)' \
                'VALUES (%s, %s);'

DEDUCT_LEAVES = 'UPDATE Writers ' \
                'SET Leaves = %s ' \
                'WHERE TrelloId = %s;'


SELECT_LEAVE_COUNT_CURRENT_WEEK = 'SELECT TrelloId, COUNT(Date) ' \
                                  'FROM LeaveRecord ' \
                                  'WHERE Date >= %s ' \
                                  'AND Date <= %s ' \
                                  'GROUP BY TrelloId;'

SELECT_WORD_COUNT_TARGET_WEEK = 'SELECT Writer, CEIL(SUM((WordCount - Penalty) * Multiplier)) ' \
                                'FROM CardDetails ' \
                                'WHERE SubmittedDate >= %s ' \
                                'AND SubmittedDate <= %s ' \
                                'GROUP BY Writer;'

INSERT_WEEKLY_UPDATE = 'INSERT INTO WeeklyTarget (' \
                       'TrelloId, WeekStart, WeekEnd, WordCount, Target, Team) ' \
                       'VALUES (%s, %s, %s, %s, %s , %s) ' \
                       'ON DUPLICATE KEY UPDATE ' \
                       'WordCount = VALUES(WordCount),' \
                       'Target = VALUES(Target),' \
                       'Team = VALUES(Team);'

GET_PREVIOUS_WEEK = 'SELECT WeekStart, WeekEnd FROM WeeklyTarget ' \
                    'WHERE WeekStart < %s ' \
                    'ORDER BY WeekStart DESC ' \
                    'LIMIT 1;'

UPDATE_PREVIOUS_WEEK = 'UPDATE WeeklyTarget SET WordCount = %s ' \
                       'WHERE (TrelloId = %s) AND (WeekStart = %s) AND (WeekEnd = %s);'


class DatabaseConnector:
    def __init__(self):
        self.connection = mysql.connector.connect(**config)
        self.cursor = self.connection.cursor()

    def get_writers(self):
        self.cursor.execute(GET_WRITERS)
        return self.cursor.fetchall()

    def insert_leaves(self, leaves_per_writer):
        self.cursor.executemany(INSERT_LEAVES, leaves_per_writer)
        self.connection.commit()

    def deduct_leaves(self, values):
        self.cursor.execute(DEDUCT_LEAVES, values)
        self.connection.commit()

    def return_leave_count_current_week(self, target_week: list):
        self.cursor.execute(SELECT_LEAVE_COUNT_CURRENT_WEEK, (target_week[0], target_week[-1]))
        return self.cursor.fetchall()

    def return_word_count_target_week(self, target_week: list):
        self.cursor.execute(SELECT_WORD_COUNT_TARGET_WEEK, (target_week[0], target_week[-1]))
        return self.cursor.fetchall()

    def insert_weekly_update(self, values):
        self.cursor.executemany(INSERT_WEEKLY_UPDATE, values)
        self.connection.commit()

    def get_previous_week(self, this_week):
        self.cursor.execute(GET_PREVIOUS_WEEK, [this_week[0]])
        value = self.cursor.fetchone()
        return value

    def update_previous_week(self, values):
        self.cursor.executemany(UPDATE_PREVIOUS_WEEK, values)
        self.connection.commit()
