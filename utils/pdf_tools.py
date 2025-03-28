import os
import logging
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
from tqdm import tqdm

# Allow very large blueprint images
Image.MAX_IMAGE_PIXELS = None
logger = logging.getLogger(__name__)

def convert_pdf_to_image(pdf_path, output_dir="converted_images", dpi=600, image_format="PNG"):
    """
    Convert the first page of a PDF to a high-resolution image.

    Args:
        pdf_path (str): Path to the PDF file.
        output_dir (str): Directory to save converted images.
        dpi (int): Resolution for conversion.
        image_format (str): Output format ("PNG", "JPEG", "TIFF").

    Returns:
        str | None: Path to the first converted image, or None if failed.
    """
    try:
        pdf_name = Path(pdf_path).stem
        out_path = Path(output_dir) / pdf_name
        out_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Converting PDF to image: {pdf_path}")
        images = convert_from_path(pdf_path, dpi=dpi, fmt=image_format.lower())
        if not images:
            logger.warning(f"No pages found in {pdf_path}")
            return None

        image_file = out_path / f"{pdf_name}_page1.{image_format.lower()}"
        save_image(images[0], image_file, image_format)
        logger.info(f"Saved image: {image_file}")
        return str(image_file)

    except Exception as e:
        logger.error(f"Failed to convert {pdf_path}: {e}")
        return None

def convert_pdfs_to_images(input_folder, output_folder, dpi=600, image_format="PNG"):
    """
    Batch convert all PDFs in a folder to high-quality images.

    Args:
        input_folder (str): Folder containing PDF files.
        output_folder (str): Output folder for images.
        dpi (int): Resolution for conversion.
        image_format (str): Output format ("PNG", "JPEG", "TIFF")
    """
    os.makedirs(output_folder, exist_ok=True)
    pdf_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".pdf")]

    if not pdf_files:
        logger.warning("❌ No PDF files found in the folder.")
        return

    for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
        pdf_path = os.path.join(input_folder, pdf_file)
        try:
            images = convert_from_path(pdf_path, dpi=dpi, fmt=image_format.lower())
            base_name = Path(pdf_file).stem
            for i, image in enumerate(images):
                file_name = f"{base_name}_page_{i+1}.{image_format.lower()}"
                out_path = Path(output_folder) / file_name
                save_image(image, out_path, image_format)
            logger.info(f"✔ {pdf_file} converted successfully.")
        except Exception as e:
            logger.error(f"❌ Error processing {pdf_file}: {e}")

    logger.info(f"✅ Batch conversion completed in '{output_folder}'.")

def save_image(image, path, image_format):
    """Save image with format-specific options."""
    if image_format.upper() == "PNG":
        image.save(path, "PNG", compress_level=0)
    elif image_format.upper() == "JPEG":
        image.save(path, "JPEG", quality=100)
    elif image_format.upper() == "TIFF":
        image.save(path, "TIFF", compression="tiff_lzw")
