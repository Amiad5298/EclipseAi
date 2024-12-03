# excel_handler.py
import pandas as pd

class ExcelHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_excel(self):
        try:
            data = pd.read_excel(self.file_path)
            self.validate_columns(data)
            return data
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {e}")

    @staticmethod
    def validate_columns(data):
        required_columns = {"name", "jobTitle", "hobby", "FavoritFood"}
        if not required_columns.issubset(data.columns):
            raise ValueError(f"Excel file must contain the following columns: {', '.join(required_columns)}")
