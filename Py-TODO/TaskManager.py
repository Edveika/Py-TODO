import sqlite3
import os

class TaskManager:
    # On init will check if db exists, if not will create and then open it.
    def __init__(self):
        self.cur_dir = os.path.dirname(os.path.abspath(__file__))

        if not os.path.exists(self.cur_dir + "/Data/Tasks.db"):
            self.create_database()
        else:
            self.open_database()

        self.tasks = []
        self.archive = []
        self.load_from_database()

    def create_database(self):
        curself = self
        def create_task_table():
            nonlocal curself

            curself.db.execute("CREATE TABLE tasks(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT)")

        def create_archive_table():
            nonlocal curself

            curself.db.execute("CREATE TABLE archive(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT)")

        os.mkdir(self.cur_dir + "/Data/")
        self.open_database()
        create_task_table()
        create_archive_table()

    def open_database(self):
        db_path = self.cur_dir + "/Data/Tasks.db"
        self.con = sqlite3.connect(db_path)
        self.db: sqlite3.Cursor = self.con.cursor()

    def load_from_database(self):
        def load_tasks():
            pass

        def load_archive():
            pass

        load_tasks()
        load_archive()

    def add_task(task):
        pass

    def archive_task(task):
        pass

    def delete_task(task):
        pass