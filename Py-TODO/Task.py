
class Task:
    # Task is only going to require a task name, description is going to be optional
    def __init__(self, task_name):
        self.task_name = task_name
        self.description = None

    def set_task_name(self, name):
        self.task_name = name

    def set_description(self, description):
        self.description = description

    def get_task_name(self):
        return self.task_name

    def get_description(self):
        return self.description