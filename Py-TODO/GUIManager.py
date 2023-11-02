import gi
# Version 3.0 required
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from Task import Task
from TaskManager import TaskManager
import os

class GUIManager:
    # Creates an instance of TaskManager
    # Loads .glade file
    # Initializes windows
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

        # Initializes new task window
        self.init_new_task_win()
        # Initializes task settings window
        self.init_task_settings_win()
        # Initializes archive settings window
        self.init_archive_settings_win()

    # Main window of the program, shows current and completed tasks
    def main_window(self):
        # Loads main window form from .glade file
        window = self.builder.get_object("main_window")
        window.connect("destroy", Gtk.main_quit)

        # Unhides the new task window
        def show_new_task_win(button):
            nonlocal self
            self.new_task_window.show_all()

        # New task button
        self.builder.get_object("btn_new_task").connect("clicked", show_new_task_win)

        # Retrieve listboxes from builder instance
        self.task_listbox = self.builder.get_object("task_list")
        self.archive_listbox = self.builder.get_object("archive_list")

        # Loads existing elements into listboxes
        def load_listbox_data(element_list: list[Task], listbox):
            # Iterate over all of the elements
            for element in element_list:
                self.text_to_listbox(listbox, element.get_task_name())

        # Load tasks and archives into listboxes
        load_listbox_data(self.task_manager.get_tasks(), self.task_listbox)
        load_listbox_data(self.task_manager.get_archive(), self.archive_listbox)

        # Handles double click events on the messagebox rows
        self.task_listbox.connect("button-press-event", self.listbox_double_click, self.task_settings_window)
        self.archive_listbox.connect("button-press-event", self.listbox_double_click, self.archive_settings_window)

        # Shows the window and starts the GTK main loop
        window.show_all()
        Gtk.main()

    # Hides the window
    # helper = additional function that can be called. Example: clear entry box text
    def hide_window(self, window, event, helper):
        window.hide()
        if helper:
            helper()
        return True

    # Adds a new task to the task list
    def add_task(self, button, reset_entry):
        # Get title and description that user chose
        title = self.builder.get_object("entry_title").get_text()
        description = self.builder.get_object("entry_desc").get_text()
        
        # Hides the window and resets the entry box fields
        def hide_window():
            nonlocal self
            reset_entry()
            self.new_task_window.hide()

        # If task already exists, prompt the user
        if title in self.task_manager.get_task_titles():
            self.show_message_box("This task already exists")
            return
        # If task is already completed, prompt the user
        if title in self.task_manager.get_archive_titles():
            self.show_message_box("You have already completed this task")
            return
        # If the user forgot to input a title, prompt him
        if title == "":
            self.show_message_box("Task title must not be empty")
            return
        
        # Create a temp Task variable with user's title of the task
        tmp_task = Task(title)
        # If user wrote a description
        if description:
            # Set the description of the task
            tmp_task.set_description(description)
        # Add the task to the task list
        self.task_manager.add_task(tmp_task)
        # Add task's title to the ongoing task listbox
        self.text_to_listbox(self.task_listbox, title)
        # Refresh the listbox so the user sees his new task
        self.task_listbox.show_all()
        # Hide the window, reset input boxes
        hide_window()

    # Loads new task window elements, initializes them
    def init_new_task_win(self):
        # Resets entry boxes of new task window
        def reset_entry():
            self.builder.get_object("entry_title").set_text("")
            self.builder.get_object("entry_desc").set_text("")
        self.new_task_window = self.builder.get_object("new_task_window")
        self.new_task_window.connect("delete-event", self.hide_window, reset_entry)
        self.builder.get_object("btn_add_task").connect("clicked", self.add_task, reset_entry)

    # Moves task into archives when complete button is pressed, refreshes listboxes
    def complete_task(self, button):
        row = self.get_cur_listbox_row()
        if row:
            # Get task from title
            title = row.get_child().get_text()
            task = self.task_manager.get_task_from_title(title)
            
            # Move row from task listbox to archive listbox, because it is completed
            self.task_listbox.remove(row)
            self.task_listbox.show_all()
            self.archive_listbox.add(row)
            self.archive_listbox.show_all()
            # Move task to archives in memory and sql db
            self.task_manager.archive_task(task)
            # Hide the window
            self.task_settings_window.hide()

    # Applies changes to the task when user clicks save
    def save_settings(self, button):
        row = self.get_cur_listbox_row()
        if row:
            # Get current values: title, desc entry, create new task
            title_entry = self.builder.get_object("settings_title_entr")
            desc_entry = self.builder.get_object("settings_desc_entr")
            title = row.get_child().get_text()
            task = self.task_manager.get_task_from_title(title)
            new_task = Task(title_entry.get_text())
            if desc_entry.get_text():
                new_task.set_description(desc_entry.get_text())

            # If the user didnt change anything, prompt him
            if task.get_task_name() == new_task.get_task_name() and task.get_description() == new_task.get_description():
                self.show_message_box("Nothing was changed")
                self.task_settings_window.hide()
                return
            # If user deleted the title, prompt him
            elif task.get_task_name() == "":
                self.show_message_box("Task title must not be empty")
                self.task_settings_window.hide()
                return
            
            # Update listbox string value
            row.get_child().set_text(title_entry.get_text())
            # Show it
            self.task_listbox.show_all()
            # Update the task values in memory and sql db
            self.task_manager.update_task(task, new_task)
            # Hide the window when we are done
            self.task_settings_window.hide()

    # Initializes settings window elements
    def init_task_settings_win(self):
        self.task_settings_window = self.builder.get_object("task_settings_window")
        self.task_settings_window.connect("delete-event", self.hide_window, None)
        self.builder.get_object("btn_settings_complete").connect("clicked", self.complete_task)
        self.builder.get_object("btn_save_stngs").connect("clicked", self.save_settings)

    # Deletes archive from archive memory list and db
    def delete_archive(self, button):
        row = self.get_cur_listbox_row()
        if row:
            # Get archive from title
            title = row.get_child().get_text()
            archive = self.task_manager.get_archive_from_title(title)
            # Delete archive from memory and db
            self.task_manager.delete_task(archive)
            # Remove it from listbox and refresh it
            self.archive_listbox.remove(row)
            self.archive_listbox.show_all()
            # Hide the window
            self.archive_settings_window.hide()

    # Initializes archive settings window elements
    def init_archive_settings_win(self):
        self.archive_settings_window = self.builder.get_object("archive_settings_window")
        self.archive_settings_window.connect("delete-event", self.hide_window, None)
        self.settings_archive_title = self.builder.get_object("archive_settings_title")
        self.settings_archive_desc = self.builder.get_object("archive_settings_desc")
        self.btn_archive_del = self.builder.get_object("btn_archive_del").connect("clicked", self.delete_archive)

    # Handles double click events, loads window data, opens settings for the tasks
    def listbox_double_click(self, listbox, event, window):
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            self.row = listbox.get_selected_row()
            # If user selected a valid row
            if self.row:
                title = self.row.get_child().get_text()
                # Depending on the window that is going to be shown, will do some initialization
                match window:
                    # If we are opening the task settings window
                    case self.task_settings_window:
                        # Get task from title
                        task = self.task_manager.get_task_from_title(title)
                        # Load task's information into listboxes so the user knows which task he opened
                        title_entry = self.builder.get_object("settings_title_entr")
                        desc_entry = self.builder.get_object("settings_desc_entr")
                        title_entry.set_text(title)
                        if task.get_description():
                            desc_entry.set_text(task.get_description())
                        # If we are opening archive settings window
                    case self.archive_settings_window:
                        # Get archive from title
                        archive = self.task_manager.get_archive_from_title(title)
                        # Load archive's information into labels
                        self.settings_archive_title.set_text(title)
                        if archive.get_description():
                            self.settings_archive_desc.set_text(archive.get_description())
                    case _:
                        return
                # Show the window
                window.show_all()

    # Returns currently selected(double clicked) listbox row
    def get_cur_listbox_row(self):
        return self.row

    # Makes a label out of text and adds it to the listbox
    def text_to_listbox(self, listbox, text):
        # Create a label with the name of the current element
        title = Gtk.Label(label=text)
        # Create a row that is going to be inserted into listbox
        task_row = Gtk.ListBoxRow()
        # Add the title into the row
        task_row.add(title)
        # Add the row into the listbox
        listbox.add(task_row)

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