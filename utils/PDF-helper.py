import sys
from pathlib import Path

import pymupdf
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.logger import setup_logger

logger = setup_logger("PDF-helper")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
IMAGES_DIR = PROJECT_ROOT / "images"


def page_count(pdf_path):
    logger.info(f"Counting pages for {pdf_path.name}")
    doc = pymupdf.open(pdf_path)
    count = len(doc)
    doc.close()
    return count

def pdf_to_images(pdf_path):
    logger.info(f"Converting {pdf_path.name} to images")
    doc = pymupdf.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap()
        images.append(pix)
    doc.close()
    return images

def sotre_images(images, output_path):
    logger.info(f"Storing images in {output_path}")
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    for i, image in enumerate(images):
        image.save(str(output_path / f"page_{i}.png"))
    return True

def list_pdfs(data_dir=DATA_DIR):
    logger.info(f"Listing PDFs in {data_dir}")
    return sorted(Path(data_dir).glob("*.pdf"))

def process_pdf(pdf_path, images_root=IMAGES_DIR):
    logger.info(f"Processing {pdf_path.name}")
    pdf_path = Path(pdf_path)
    count = page_count(pdf_path)
    logger.info(f"Processing {pdf_path.name} ({count} pages)")
    images = pdf_to_images(pdf_path)
    output_dir = Path(images_root) / pdf_path.stem
    sotre_images(images, output_dir)
    logger.info(f"Stored {len(images)} images in {output_dir}")
    return True

if __name__ == "__main__":
    pdfs = list_pdfs()
    if not pdfs:
        logger.info(f"No PDFs found in {DATA_DIR}")
    else:
        logger.info(f"Found {len(pdfs)} PDF(s) in {DATA_DIR}")
        for pdf in pdfs:
            process_pdf(pdf)
        logger.info("All PDFs processed successfully")
