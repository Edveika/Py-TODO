import gi
# Version 3.0 required
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from Task import Task
from TaskManager import TaskManager
import os

class GUIManager:
    # Creates an instance of TaskManager
    # Loads .glade file
    def __init__(self):
        # Will be used to point to directories relative to current path
        self.cur_path = os.path.dirname(os.path.abspath(__file__))
        
        # Instance of task manager is created
        self.task_manager = TaskManager()

        # Builder instance creation
        self.builder = Gtk.Builder()
        try:
            # Opens .glade file, loads GUI elements
            self.builder.add_from_file(self.cur_path + "/Form/Py-TODO.glade")
        except:
            # If file not found, shows an error and terminates the program
            self.show_message_box("Not found: " + self.cur_path + "/Form/Py-TODO.glade")
            exit()

    # Main window of the program, shows current and completed tasks
    def main_window(self):
        window = self.builder.get_object("main_window")
        window.connect("destroy", Gtk.main_quit)

        # Retrieve listboxes from builder instance
        self.task_listbox = self.builder.get_object("task_list")
        self.archive_listbox = self.builder.get_object("archive_list")

        # Loads existing elements into listboxes
        def load_listbox_data(element_list: list[Task], listbox):
            # Iterate over all of the elements
            for element in element_list:
                # Create a label with the name of the current element
                title = Gtk.Label(label=element.get_task_name())
                # Create a row that is going to be inserted into listbox
                task_row = Gtk.ListBoxRow()
                # Add the title into the row
                task_row.add(title)
                # Add the row into the listbox
                listbox.add(task_row)

        # Load tasks and archives into listboxes
        load_listbox_data(self.task_manager.get_tasks(), self.task_listbox)
        load_listbox_data(self.task_manager.get_archive(), self.archive_listbox)

        window.show_all()

        Gtk.main()

    # Shows a messagebox
    def show_message_box(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()