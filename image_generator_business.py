import pandas as pd
from PIL import Image
import threading
from excel_handler import ExcelHandler
from api_image_generator import ApiImageGenerator
from image_saver import ImageSaver

class BackgroundImageCreator:
    def __init__(self, api_key, excel_file_path, output_dir, task_id, progress, progress_lock):
        self.excel_handler = ExcelHandler(excel_file_path)
        self.image_generator = ApiImageGenerator(api_key)
        self.image_saver = ImageSaver(output_dir)
        self.task_id = task_id
        self.progress = progress
        self.progress_lock = progress_lock

    def process(self):
        data = self.excel_handler.read_excel()
        total_rows = len(data)
        saved_images = []

        for idx, row in data.iterrows():
            # Check if the task has been canceled
            if self.is_canceled():
                print(f"Task {self.task_id} has been canceled.")
                with self.progress_lock:
                    self.progress[self.task_id] = {
                        "percentage": 0,
                        "generated": len(saved_images),
                        "total": total_rows,
                        "status": "canceled"
                    }
                return saved_images

            prompt = self.image_generator.generate_prompt(row['name'], row['jobTitle'], row['hobby'], row['FavoritFood'])

            # Another cancellation check before generating the image
            if self.is_canceled():
                print(f"Task {self.task_id} has been canceled.")
                with self.progress_lock:
                    self.progress[self.task_id] = {
                        "percentage": 0,
                        "generated": len(saved_images),
                        "total": total_rows,
                        "status": "canceled"
                    }
                return saved_images

            image_url = self.image_generator.create_background_image(prompt)

            # Another cancellation check before saving the image
            if self.is_canceled():
                print(f"Task {self.task_id} has been canceled.")
                with self.progress_lock:
                    self.progress[self.task_id] = {
                        "percentage": 0,
                        "generated": len(saved_images),
                        "total": total_rows,
                        "status": "canceled"
                    }
                return saved_images

            saved_image_path = self.image_saver.save_image(image_url, row['name'], row['LastName'])
            saved_images.append(saved_image_path)

            # Update progress
            with self.progress_lock:
                self.progress[self.task_id] = {
                    "percentage": int(((idx + 1) / total_rows) * 100),
                    "generated": idx + 1,
                    "total": total_rows,
                    "status": "in-progress"
                }
                print(f"Task {self.task_id} progress: {self.progress[self.task_id]['percentage']}% - {self.progress[self.task_id]['generated']}/{self.progress[self.task_id]['total']} images generated")

        # Final update to ensure the self.progress is complete
        with self.progress_lock:
            self.progress[self.task_id] = {
                "percentage": 100,
                "generated": total_rows,
                "total": total_rows,
                "status": "done"
            }
            print(f"Task {self.task_id} completed with progress: {self.progress[self.task_id]['percentage']}% - {self.progress[self.task_id]['generated']}/{self.progress[self.task_id]['total']} images generated")
        return saved_images

    def is_canceled(self):
        with self.progress_lock:
            return self.progress.get(self.task_id, {}).get("status") == "canceled"