import unittest
import json
import os
from constants import TEST_TABLE_DATA_JSON_PATH

class Table:
    def __init__(self, parent, predefined_items, selector_values):
        self.parent = parent
        self.predefined_items = predefined_items
        self.selector_values = selector_values
        self.rows = []

    def add_row(self, values=None):
        row_number = len(self.rows) + 1
        col1 = values["gesture"] if values else None
        col2 = values["action"] if values else None
        file_entry = values["file"] if values else None
        self.rows.append((col1, col2, file_entry))

    def save_to_json(self, path=TEST_TABLE_DATA_JSON_PATH):
        data = []
        for row in self.rows:
            gesture, action, file_path = row
            data.append({
                "gesture": gesture,
                "action": action,
                "file": file_path
            })
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, "w") as outfile:
            json.dump(data, outfile)

    def load_from_json(self, path=TEST_TABLE_DATA_JSON_PATH):
        if os.path.exists(path):
            with open(path, "r") as infile:
                data = json.load(infile)
            for entry in data:
                self.add_row(entry)

class TestTable(unittest.TestCase):

    def setUp(self):
        self.predefined_items = ["Action1", "Action2", "Action3"]
        self.selector_values = ["Gesture1", "Gesture2", "Gesture3"]
        self.table = Table(None, self.predefined_items, self.selector_values)

    def test_initialization(self):
        self.assertIsNotNone(self.table.predefined_items)
        self.assertIsNotNone(self.table.selector_values)
        self.assertIsNotNone(self.table.rows)
        self.assertEqual(len(self.table.rows), 0)  

    def test_add_row(self):
        self.table.add_row()
        self.assertEqual(len(self.table.rows), 1)  

    def test_save_and_load_json(self):

        self.table.add_row({"gesture": "Gesture1", "action": "Action1", "file": "sample_path"})


        self.table.save_to_json()


        self.table.rows = [] 
        self.table.load_from_json()


        loaded_row = self.table.rows[0]
        self.assertEqual(loaded_row[0], "Gesture1")
        self.assertEqual(loaded_row[1], "Action1")
        self.assertEqual(loaded_row[2], "sample_path")

if __name__ == "__main__":
    unittest.main()