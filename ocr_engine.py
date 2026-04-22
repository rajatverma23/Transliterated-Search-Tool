import pytesseract
import os

class OCREngine:
    def __init__(self):
        # Default options, generic model
        self.lang = 'hin+eng'
        self.tessdata_dir = None

    def set_config(self, lang, tessdata_dir=""):
        self.lang = lang
        if tessdata_dir and os.path.exists(tessdata_dir):
            self.tessdata_dir = tessdata_dir
        else:
            self.tessdata_dir = None

    def process_image(self, pil_image):
        config = ""
        if self.tessdata_dir:
            config = f'--tessdata-dir "{self.tessdata_dir}"'
            
        try:
            text = pytesseract.image_to_string(pil_image, lang=self.lang, config=config)
            return text
        except Exception as e:
            return f"OCR Error: {str(e)}"
