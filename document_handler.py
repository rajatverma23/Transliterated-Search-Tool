import fitz  # PyMuPDF
from PIL import Image

class DocumentHandler:
    def __init__(self):
        self.doc = None
        self.pages = []  # Fallback for image files
        self.num_pages = 0
        self.is_pdf = False

    def load_document(self, file_path):
        if self.doc:
            self.doc.close()
            self.doc = None
        self.pages = []
        self.num_pages = 0

        if file_path.lower().endswith('.pdf'):
            self._load_pdf(file_path)
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            self._load_image(file_path)
            
        return self.num_pages

    def _load_pdf(self, file_path):
        self.doc = fitz.open(file_path)
        # Apply a 50-page maximum threshold as requested
        self.num_pages = min(len(self.doc), 50)
        self.is_pdf = True

    def _load_image(self, file_path):
        img = Image.open(file_path)
        self.pages.append(img.convert('RGB'))
        self.num_pages = 1
        self.is_pdf = False

    def get_page(self, index):
        if index < 0 or index >= self.num_pages:
            return None
            
        if self.is_pdf and self.doc:
            page = self.doc.load_page(index)
            pix = page.get_pixmap(dpi=300, alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            return img
        else:
            return self.pages[index]

