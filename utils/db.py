import psycopg2

import config


class DataBase:
    def __init__(self):
        self.con = psycopg2.connect(
          database=config.DATABASE,
          user=config.USER,
          password=config.PASSWORD,
          host=config.HOST,
          port=config.PORT
        )
        self.cur = self.con.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS user_language  
             (chat_id varchar(255) PRIMARY KEY NOT NULL,
             language varchar(50) NOT NULL);
        """)
        self.con.commit()

    def close(self):
        self.con.close()

    def insert_language(self, chat_id, language):
        self.cur.execute("""
        INSERT INTO user_language (chat_id, language)
            VALUES('{}','{}') 
            ON CONFLICT (chat_id) 
            DO UPDATE SET language = EXCLUDED.language;
        """.format(chat_id, language))
        self.con.commit()

    def select_language(self, chat_id):
        self.cur.execute("""
        SELECT language FROM user_language WHERE chat_id = '{}'
        """.format(chat_id))
        lang = self.cur.fetchone()
        return lang[0] if lang else None
