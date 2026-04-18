import fitz
import re
import unicodedata
from langchain_core.documents import Document

class FinalRAGProcessor:
    def __init__(self):
        self.hyphen_pattern = re.compile(r'(\w+)-\n\s*(\w+)')
        self.multi_space = re.compile(r' + ')

    def clean_text(self, text):
        # 1. Standardizing encoding
        text = unicodedata.normalize('NFKD', text)
        
        # 2. Fixing plit words (e.g., "process-\ning" -> "processing")
        text = self.hyphen_pattern.sub(r'\1\2', text)
        
        # 3. Handle specific artifacts
        text = text.replace('❑', '- ').replace('•', '- ')
        
        # 4. Clean up whitespace
        text = text.replace('\n', ' ')
        text = self.multi_space.sub(' ', text)
        
        return text.strip()

    def process_document(self, pdf_path):
        doc = fitz.open(pdf_path)
        documents = []

        for page_num, page in enumerate(doc):
            # Define margins to ignore (Top/Bottom 50 points)
            page_rect = page.rect
            clip_box = fitz.Rect(0, 50, page_rect.width, page_rect.height - 50)
            
            # Text as blocks
            blocks = page.get_text("blocks", clip=clip_box)
            
            # Sort blocks: Top-to-bottom, then Left-to-right
            blocks.sort(key=lambda b: (b[1], b[0]))
            
            page_content = []
            for b in blocks:
                block_text = b[4].strip()
                if len(block_text) > 5:
                    page_content.append(block_text)
            
            full_page_text = " ".join(page_content)
            cleaned_page = self.clean_text(full_page_text)

            # Filtering out thin pages and wrap in LangChain Document format
            if len(cleaned_page) > 100:
                documents.append(
                    Document(
                        page_content=cleaned_page,
                        metadata={
                            "source": pdf_path,
                            "page": page_num + 1
                        }
                    )
                )
        
        doc.close()
        return documents

def load_pdf(file_path: str):
    # Instead of PyPDFLoader, we use our custom processor
    processor = FinalRAGProcessor()
    documents = processor.process_document(file_path)
    return documents