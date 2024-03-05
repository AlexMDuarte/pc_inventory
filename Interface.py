import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import csv
import shutil
import subprocess

class ComputerDatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Computer Database Management")
        self.initialize_gui_components()
        self.create_gui()
        self.root.bind("<<NotebookTabChanged>>", self.update_tabs)

    def get_last_entries(self):
        with sqlite3.connect("computers.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT computer_id, component, serial_number, date_added
                FROM computers
                ORDER BY date_added DESC
                LIMIT 100
            ''')
            return cursor.fetchall()

    def search(self, computer_id=None):
        with sqlite3.connect("computers.db") as conn:
            cursor = conn.cursor()
            if computer_id:
                cursor.execute('''
                    SELECT computer_id, component, serial_number
                    FROM computers
                    WHERE computer_id LIKE ?
                    ORDER BY computer_id, component
                ''', (f"%{computer_id}%",))
            else:
                cursor.execute('''
                    SELECT computer_id, component, serial_number
                    FROM computers
                    ORDER BY computer_id, component
                ''')
            return cursor.fetchall()

    def update_serial_number(self, computer_id, component, new_serial_number):
        with sqlite3.connect("computers.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE computers
                SET serial_number = ?
                WHERE computer_id = ? AND component = ? AND serial_number <> ?
            ''', (new_serial_number, computer_id, component, new_serial_number))
            conn.commit()

    def update_treeview(self, data, treeview):
        treeview.delete(*treeview.get_children())
        for row in data:
            treeview.insert('', 'end', values=row)
        treeview.bind("<Double-1>", self.copy_to_clipboard)
        treeview.bind("<<TreeviewSelect>>", self.fill_entry_fields)

    def delete_all_entries(self):
        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete all entries?")
        if confirmation:
            with sqlite3.connect("computers.db") as conn:
                conn.execute('DELETE FROM computers')
            messagebox.showinfo("Delete All Entries", "All entries deleted successfully.")

    def export_all_entries(self):
        with sqlite3.connect("computers.db") as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM computers')
            result = cursor.fetchall()
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(["Computer ID", "Component", "Serial Number ( ID )", "Date Added"])
                csv_writer.writerows(result)
            messagebox.showinfo("Export All Entries", "All entries exported successfully.")

    def backup_database(self):
        shutil.copy("computers.db", "backup/computers_backup.db")
        messagebox.showinfo("Backup Database", "Database backup created successfully.")

    def restore_database(self):
        file_path = filedialog.askopenfilename(defaultextension=".db", filetypes=[("Database files", "*.db")])
        if file_path:
            shutil.copy(file_path, "computers.db")
            messagebox.showinfo("Restore Database", "Database restored successfully.")

    def perform_search(self):
        search_text = self.search_entry.get()
        result = self.search(computer_id=search_text)
        self.update_treeview(result, self.search_treeview)

    def copy_to_clipboard(self, event):
        treeview = event.widget
        selection = treeview.selection()
        if selection:
            item = treeview.item(selection)
            values = item['values']
            if values:
                self.root.clipboard_clear()
                self.root.clipboard_append(values[0])
                messagebox.showinfo("Copied", "Copied to clipboard.")

    def fill_entry_fields(self, event):
        treeview = event.widget
        selection = treeview.selection()
        if selection:
            item = treeview.item(selection)
            values = item['values']
            if values:
                self.computer_id_entry.delete(0, tk.END)
                self.computer_id_entry.insert(0, values[0])
                self.component_entry.delete(0, tk.END)
                self.component_entry.insert(0, values[1])
                self.serial_number_entry.delete(0, tk.END)
                self.serial_number_entry.insert(0, values[2])

    def initialize_gui_components(self):
        self.notebook = ttk.Notebook(self.root)
        self.treeview = None
        self.search_entry = None
        self.search_treeview = None
        self.computer_id_entry = None
        self.component_entry = None
        self.serial_number_entry = None

    def create_gui(self):
        self.create_last_entries_tab(self.notebook)
        self.create_search_tab(self.notebook)
        self.create_options_tab(self.notebook)
        self.notebook.pack(expand=1, fill="both")

    def create_last_entries_tab(self, notebook):
        tab_last_entries = ttk.Frame(notebook)
        last_entries_label = tk.Label(tab_last_entries, text="Last Entries", font=("Helvetica", 16))
        last_entries_label.pack(pady=10)
        self.treeview = ttk.Treeview(tab_last_entries, columns=('Computer ID', 'Component', 'Serial Number ( ID )', 'Date Added'), show='headings')
        for col in ('Computer ID', 'Component', 'Serial Number ( ID )', 'Date Added'):
            self.treeview.heading(col, text=col)
            self.treeview.column(col, anchor="w")
        self.treeview.pack(expand=1, fill='both')
        self.update_treeview(self.get_last_entries(), self.treeview)
        notebook.add(tab_last_entries, text="Last Entries")

    def create_search_tab(self, notebook):
        tab_search = ttk.Frame(notebook)
        search_label = tk.Label(tab_search, text="Search", font=("Helvetica", 16))
        search_label.pack(pady=10)
        search_entry_label = tk.Label(tab_search, text="Enter Computer ID:")
        search_entry_label.pack()
        self.search_entry = tk.Entry(tab_search)
        self.search_entry.pack(pady=5)
        search_button = tk.Button(tab_search, text="Search", command=self.perform_search)
        search_button.pack(pady=10)
        self.search_treeview = ttk.Treeview(tab_search, columns=('Computer ID', 'Component', 'Serial Number ( ID )'), show='headings')
        for col in ('Computer ID', 'Component', 'Serial Number ( ID )'):
            self.search_treeview.heading(col, text=col)
            self.search_treeview.column(col, anchor="w")
        self.search_treeview.pack(expand=1, fill='both')
        notebook.add(tab_search, text="Search")

    def create_options_tab(self, notebook):
        tab_options = ttk.Frame(notebook)
        options_label = tk.Label(tab_options, text="Options", font=("Helvetica", 16))
        options_label.pack(pady=10)
        delete_button = tk.Button(tab_options, text="Delete All Entries", command=self.delete_all_entries)
        delete_button.pack(pady=5)
        export_button = tk.Button(tab_options, text="Export All Entries", command=self.export_all_entries)
        export_button.pack(pady=5)
        backup_button = tk.Button(tab_options, text="Backup Database", command=self.backup_database)
        backup_button.pack(pady=5)
        restore_button = tk.Button(tab_options, text="Restore Database", command=self.restore_database)
        restore_button.pack(pady=5)
    #    edit_button = tk.Button(tab_options, text="Edit Database", command=self.edit_database)
     #   edit_button.pack(pady=5)
        run_etl_button = tk.Button(tab_options, text="Run ETL Task", command=self.run_etl_task)
        run_etl_button.pack(pady=5)
        run_etl_button = tk.Button(tab_options, text="GenerateQRCode", command=self.run_qrcode)
        run_etl_button.pack(pady=5)
        notebook.add(tab_options, text="Options")

    def edit_database(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Database")

        # Fetch and display database entries in the treeview
        entries = self.get_last_entries()
        treeview = ttk.Treeview(edit_window, columns=('Computer ID', 'Component', 'Serial Number ( ID )', 'Date Added'), show='headings')
        for col in ('Computer ID', 'Component', 'Serial Number ( ID )', 'Date Added'):
            treeview.heading(col, text=col)
            treeview.column(col, anchor="w")
        for entry in entries:
            treeview.insert('', 'end', values=entry)
        treeview.pack(expand=1, fill='both')

        # Entry fields for editing
        self.computer_id_entry = tk.Entry(edit_window)
        self.computer_id_entry.pack(pady=5)

        self.component_entry = tk.Entry(edit_window)
        self.component_entry.pack(pady=5)

        self.serial_number_entry = tk.Entry(edit_window)
        self.serial_number_entry.pack(pady=5)

        # Submit button to confirm changes
        submit_button = tk.Button(edit_window, text="Submit", command=self.submit_changes)
        submit_button.pack(pady=10)

    def submit_changes(self):
        selected_item = self.treeview.selection()
        if selected_item:
            item = self.treeview.item(selected_item)
            values = item['values']
            if values:
                computer_id = self.computer_id_entry.get()
                component = self.component_entry.get()
                serial_number = self.serial_number_entry.get()
                if computer_id and component and serial_number:
                    self.update_serial_number(computer_id, component, serial_number)
                    messagebox.showinfo("Success", "Changes submitted successfully.")
                    self.update_treeview(self.get_last_entries(), self.treeview)
                    self.computer_id_entry.delete(0, tk.END)
                    self.component_entry.delete(0, tk.END)
                    self.serial_number_entry.delete(0, tk.END)
                else:
                    messagebox.showwarning("Warning", "Please fill in all fields.")
        else:
            messagebox.showwarning("Edit Database", "Please select an entry to edit.")
    
    def run_etl_task(self):
        subprocess.Popen(["python", "ETLDatabase.py"])
        messagebox.showinfo("ETL Task", "CSV To Database Extract Transform Load Task is done")

    def run_qrcode(self):
        subprocess.Popen(["python", "QRCode.py"])


    def update_tabs(self, event=None):
        selected_tab = self.notebook.select()
        if selected_tab:
            tab_index = self.notebook.index(selected_tab)
            if tab_index == 0:
                self.update_treeview(self.get_last_entries(), self.treeview)
            elif tab_index == 1:
                self.perform_search()

def main():
    root = tk.Tk()
    app = ComputerDatabaseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
