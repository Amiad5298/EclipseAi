import logging
import pandas as pd

logger = logging.getLogger(__name__)

class ExcelHandler:
    """
    Handles reading and validating Excel files for required columns.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initialize the ExcelHandler with a given file path.

        Args:
            file_path (str): The path to the Excel file.
        """
        self.file_path = file_path

    def read_excel(self) -> pd.DataFrame:
        """
        Read the Excel file into a pandas DataFrame and validate its columns.

        Returns:
            pd.DataFrame: The DataFrame containing the Excel data.

        Raises:
            ValueError: If there is an error reading the file or if required columns are missing.
        """
        logger.debug(f"Attempting to read Excel file at: {self.file_path}")
        try:
            data = pd.read_excel(self.file_path)
            self.validate_columns(data)
            logger.info(f"Successfully read and validated Excel file at: {self.file_path}")
            return data
        except Exception as e:
            logger.exception(f"Error reading Excel file at {self.file_path}")
            raise ValueError(f"Error reading Excel file: {e}") from e

    @staticmethod
    def validate_columns(data: pd.DataFrame) -> None:
        """
        Validate that the DataFrame contains the required columns.

        Args:
            data (pd.DataFrame): The DataFrame to validate.

        Raises:
            ValueError: If the required columns are not present.
        """
        required_columns = {"name", "jobTitle", "hobby", "FavoritFood"}
        logger.debug(f"Validating required columns in DataFrame. Required: {required_columns}, Found: {set(data.columns)}")

        if not required_columns.issubset(data.columns):
            missing = required_columns - set(data.columns)
            logger.error(f"Missing required columns: {missing}")
            raise ValueError(
                f"Excel file must contain the following columns: {', '.join(required_columns)}"
            )
        logger.debug("All required columns are present.")