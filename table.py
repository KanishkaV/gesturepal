import tkinter as tk
from tkinter import ttk, filedialog
import os
import json
from constants import TABLE_DATA_JSON_PATH

class Table:
    def __init__(self, parent, predefined_items, selector_values):
        self.parent = parent
        self.predefined_items = predefined_items
        self.selector_values = selector_values
        self.rows = []

     
        tk.Label(self.parent, text="Gesture").grid(row=0, column=0)
        tk.Label(self.parent, text="Action").grid(row=0, column=1)
        tk.Label(self.parent, text="File Selector").grid(row=0, column=2)

      
        self.add_row_btn = tk.Button(self.parent, text="Add Row", command=self.add_row,bg="#3A2AEE",fg="#FFFFFF")
        self.add_row_btn.grid(row=0, column=3,columnspan=2)

       
        self.load_from_json()

    def add_row(self, values=None):
        row_number = len(self.rows) + 1
        
    
        col1 = ttk.Combobox(self.parent, values=self.selector_values, postcommand=self.update_combobox_values)
        col1.bind("<<ComboboxSelected>>", self.on_value_selected)
        col1.grid(row=row_number, column=0)

      
        col2 = ttk.Combobox(self.parent, values=self.predefined_items, postcommand=self.update_combobox_values)
        col2.bind("<<ComboboxSelected>>", self.on_value_selected)
        col2.grid(row=row_number, column=1)

  
        file_entry = tk.Entry(self.parent, state=tk.DISABLED)
        file_entry.grid(row=row_number, column=2)

    
        browse_btn = tk.Button(self.parent, text="Browse", command=lambda: self.browse_file(file_entry),fg="#FFFFFF", state=tk.DISABLED)
        browse_btn.grid(row=row_number, column=3)
        test_btn = tk.Button(self.parent, text="Test", state=tk.NORMAL,bg="#3A2AEE",fg="#FFFFFF")
        test_btn.grid(row=row_number, column=4)

        self.rows.append((col1, col2, file_entry, browse_btn))
        
     
        if values:
            col1.set(values["gesture"])
            predefined_item=values["action"]
            file_path=values["file"]
            col2.set(predefined_item)
            if predefined_item == "sh File" and file_path:
                self.update_file_entry_value(file_entry,file_path)
                browse_btn.config(fg="#FFFFFF",bg="#3A2AEE",state=tk.NORMAL)
            else:
                browse_btn.config(fg="#FFFFFF",bg="#C4BEBE",state=tk.DISABLED)
        
        self.save_to_json()

    def update_combobox_values(self):
        selected_values = [row[0].get() for row in self.rows if row[0].get() != "sh File"]
        for row in self.rows:
            available_values = [val for val in self.selector_values if val not in selected_values or val == "sh File"]
            row[0]['values'] = available_values
        

    def on_value_selected(self, event):
        for row in self.rows:
            if row[1].get() == "sh File":
                row[2].config(state=tk.NORMAL)
                row[3].config(fg="#FFFFFF",bg="#3A2AEE",state=tk.NORMAL)
            else:
                row[2].config(text="",state=tk.DISABLED)
                row[3].config(fg="#FFFFFF",bg="#C4BEBE",state=tk.DISABLED)
        self.save_to_json()

    def select_file(self, row_number):
        filepath = filedialog.askopenfilename()
        if filepath:
            self.rows[row_number-1][2].config(text=os.path.basename(filepath))

    def save_to_json(self, filename=TABLE_DATA_JSON_PATH):
        data = []
        for row in self.rows:
            data.append({
                "gesture": row[0].get(),
                "action": row[1].get(),
                "file": row[2].get() if row[1].get() == "sh File" else None
            })
        
        with open(filename, "w") as outfile:
            json.dump(data, outfile)

    def load_from_json(self):
        if not os.path.exists(TABLE_DATA_JSON_PATH):
            return

        with open(TABLE_DATA_JSON_PATH, 'r') as file:
            data = json.load(file)

        for item in data:
            self.add_row(values=item)
    
    def browse_file(self, file_entry):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.update_file_entry_value(file_entry,file_path)
        self.save_to_json()
    
    def update_file_entry_value(self,file_entry,file_path):
        if  file_entry:
            file_entry.config(state=tk.NORMAL)
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)