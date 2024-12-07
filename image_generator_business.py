import logging
import threading
from typing import Dict, Any, List
from excel_handler import ExcelHandler
from api_image_generator import ApiImageGenerator
from image_saver import ImageSaver

logger = logging.getLogger(__name__)

class BackgroundImageCreator:
    """
    A class responsible for processing an Excel file to generate background images
    for each row of data using the OpenAI Image API.
    """

    def __init__(
        self,
        api_key: str,
        excel_file_path: str,
        output_dir: str,
        task_id: str,
        progress: Dict[str, Dict[str, Any]],
        progress_lock: threading.Lock
    ) -> None:
        self.excel_handler = ExcelHandler(excel_file_path)
        self.image_generator = ApiImageGenerator(api_key)
        self.image_saver = ImageSaver(output_dir)
        self.task_id = task_id
        self.progress = progress
        self.progress_lock = progress_lock

    def process(self) -> List[str]:
        """
        Process the Excel file rows to generate images. Updates progress as each image is generated.
        
        Returns:
            A list of paths to the saved images.
        """
        data = self.excel_handler.read_excel()
        total_rows = len(data)
        saved_images = []

        for idx, row in data.iterrows():
            if self.is_canceled():
                self._mark_canceled(saved_images, total_rows)
                return saved_images

            prompt = self.image_generator.generate_prompt(
                row['name'],
                row['jobTitle'],
                row['hobby'],
                row['FavoritFood']
            )

            if self.is_canceled():
                self._mark_canceled(saved_images, total_rows)
                return saved_images

            try:
                image_url = self.image_generator.create_background_image(prompt)
            except Exception as e:
                logger.exception("Failed to create background image.")
                self._mark_error(len(saved_images), total_rows, str(e))
                return saved_images

            if self.is_canceled():
                self._mark_canceled(saved_images, total_rows)
                return saved_images

            try:
                saved_image_path = self.image_saver.save_image(image_url, row['name'], row['LastName'])
                saved_images.append(saved_image_path)
            except Exception as e:
                logger.exception("Failed to save the generated image.")
                self._mark_error(len(saved_images), total_rows, str(e))
                return saved_images

            self._update_progress(idx + 1, total_rows, "in-progress")

        # Mark task as done if completed successfully
        self._update_progress(total_rows, total_rows, "done")
        logger.info(f"Task {self.task_id} completed. Generated {total_rows}/{total_rows} images.")
        return saved_images

    def is_canceled(self) -> bool:
        """
        Check if the current task has been canceled.
        """
        with self.progress_lock:
            return self.progress.get(self.task_id, {}).get("status") == "canceled"

    def _mark_canceled(self, saved_images: List[str], total_rows: int) -> None:
        """
        Update the progress dictionary to indicate the task was canceled.
        """
        logger.info(f"Task {self.task_id} has been canceled.")
        self._safe_update_progress(
            percentage=0,
            generated=len(saved_images),
            total=total_rows,
            status="canceled"
        )

    def _mark_error(self, generated: int, total: int, error_message: str) -> None:
        """
        Update the progress dictionary to indicate the task encountered an error.
        """
        logger.error(f"Task {self.task_id} encountered an error: {error_message}")
        self._safe_update_progress(
            percentage=0,
            generated=generated,
            total=total,
            status="error"
        )

    def _update_progress(self, generated: int, total: int, status: str) -> None:
        """
        Update the progress dictionary with given status and generated counts.
        """
        percentage = int((generated / total) * 100) if total > 0 else 0
        logger.debug(f"Task {self.task_id} progress: {percentage}% ({generated}/{total})")
        self._safe_update_progress(percentage, generated, total, status)

    def _safe_update_progress(self, percentage: int, generated: int, total: int, status: str) -> None:
        """
        Thread-safe method to update the progress dictionary.
        """
        with self.progress_lock:
            self.progress[self.task_id] = {
                "percentage": percentage,
                "generated": generated,
                "total": total,
                "status": status
            }
