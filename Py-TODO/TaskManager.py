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
    def add_task(self, task: Task):
        # Add the task to the task list
        self.tasks.append(task)
        # Query that is going to insert values(?) into table tasks
        query = "INSERT INTO tasks(title, description) VALUES(?, ?)"
        # Values representing ? that are going to be inserted
        values = (task.get_task_name(), task.get_description())
        # Executes query with values replacing ? in memory
        self.db.execute(query, values)
        # Commits changes made in memory to disk
        self.con.commit()

    # Adds a task to self.archive and .db archives when the task is completed
    def archive_task(self, task: Task):
        # Remove task from ongoing task list
        self.tasks.remove(task)
        # Add the task to archive list
        self.archive.append(task)
        # Query that inserts task into archive
        query = "INSERT INTO archive(title, description) VALUES(?, ?)"
        # Values that are going to be inserted
        values = (task.get_task_name(), task.get_description)
        # Insert task into archive table
        self.db.execute(query, values)
        # Saves db into disk
        self.con.commit()

        # Query that removes a task from the task table after it was moved to archives table
        query = "DELETE FROM tasks WHERE title=? and description=?"
        # Values to be removed
        values = (task.get_task_name(), task.get_description())
        # Remove from tasks table
        self.db.execute(query, values)
        # Write changes to file
        self.con.commit()
    
    # Deletes the task from .db when the task gets removed from archive
    def delete_task(self, task: Task):
        # Remove task from the archive list
        self.archive.remove(task)
        # Query that removes archive from archives table
        query = "DELETE FROM archive WHERE title=? and description=?"
        # Values to be removed
        values = (task.get_task_name(), task.get_description())
        # Remove archive from archive table
        self.db.execute(query, values)
        # Save changes to disk
        self.con.commit()

    # Returns a list of tasks
    def get_tasks(self):
        return self.tasks
    
    # Returns a list of archived tasks that the user completed
    def get_archive(self):
        return self.archive
    
    # Returns a list of task titles
    def get_task_titles(self):
        titles = []
        for task in self.tasks:
            titles.append(task.get_task_name())
        return titles
    
    # Returns a list of archive titles
    def get_archive_titles(self):
        titles = []
        for task in self.archive:
            titles.append(task.get_task_name())
        return titles