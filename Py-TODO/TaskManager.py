from Task import Task
import sqlite3
import os

class TaskManager:
    # On init will check if db exists, if not will create and then open it.
    def __init__(self):
        # Current file path. Will be used to get directories relative to the current file
        self.cur_dir = os.path.dirname(os.path.abspath(__file__))

        # If .db file does not exist
        if not os.path.exists(self.cur_dir + "/Data/Tasks.db"):
            # Create it and then open it
            self.create_database()
        else:
            # It it does exist, just open it
            self.open_database()

        # self.tasks will hold ongoing tasks
        self.tasks: list[Task] = []
        # self.archive holds tasks that are completed
        self.archive: list[Task] = []
        # Loads existing tasks and archived tasks from the database
        self.load_from_database()

    # Creates Data/ directory and .db file
    def create_database(self):
        curself = self

        # Creates a table of ongoing tasks
        def create_task_table():
            nonlocal curself

            curself.db.execute("CREATE TABLE tasks(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT)")

        # Creates a table of completed, archived tasks
        def create_archive_table():
            nonlocal curself

            curself.db.execute("CREATE TABLE archive(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT)")

        os.mkdir(self.cur_dir + "/Data/")
        self.open_database()
        create_task_table()
        create_archive_table()

    # Opens .db file
    def open_database(self):
        self.con: sqlite3.Connection = sqlite3.connect(self.cur_dir + "/Data/Tasks.db")
        self.db: sqlite3.Cursor = self.con.cursor()

    # Loads existing tasks/archives from .db file
    def load_from_database(self):
        curself = self

        # Loads ongoing tasks from db
        def load_tasks():
            nonlocal curself

            # Gets a task list
            task_list = curself.db.execute("SELECT title, description FROM tasks").fetchall()
            # Iterates over it
            for task in task_list:
                # Creates a temp Task type variable with the task name from db
                cur_task: Task = Task(task[0])
                # Sets a description for it
                cur_task.set_description(task[1])
                # Adds it to the list(in memory)
                self.tasks.append(cur_task)
        
        # Loads archived tasks from db
        def load_archive():
            nonlocal curself

            # Gets a list of archived tasks
            archive_list = curself.db.execute("SELECT title, description FROM archive").fetchall()
            # Iterates over it
            for archive in archive_list:
                # Creates a temp archived Task variable with the task name from db
                cur_archive: Task = Task(archive[0])
                # Sets a description for it
                cur_archive.set_description(archive[1])
                # Adds it to the list
                self.archive.append(cur_archive)

        load_tasks()
        load_archive()

    # Adds a new task to self.tasks and .db tasks
    def add_task(task):
        pass

    # Adds a task to self.archive and .db archives when the task is completed
    def archive_task(task):
        pass
    
    # Deletes the task from .db when the task gets removed from archive
    def delete_task(task):
        pass

tasker = TaskManager()