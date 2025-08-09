import fitz  # PyMuPDF
import io
import os
from PIL import Image


class ImageExtractor:
    @staticmethod
    def extract_images_from_pdf(pdf_path, output_folder=None):
        """Extracts images from a PDF with page metadata"""
        if output_folder is None:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_folder = f"temp_images_{base_name}"

        os.makedirs(output_folder, exist_ok=True)

        image_data = []  # List with {path, page_num, width, height}

        try:
            pdf_document = fitz.open(pdf_path)

            for page_num, page in enumerate(pdf_document):
                image_list = page.get_images(full=True)

                for img_index, img_info in enumerate(image_list):
                    xref = img_info[0]
                    base_image = pdf_document.extract_image(xref)

                    if base_image:
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]

                        try:
                            img = Image.open(io.BytesIO(image_bytes))
                            width, height = img.size

                            # Filter very small images
                            if width < 150 or height < 150:
                                continue

                            # Filter images with low resolution
                            if width * height < 40000:  # ~200x200 pixels
                                continue

                            # Save only relevant images
                            image_filename = f"{output_folder}/image_p{page_num + 1}_{img_index}.{image_ext}"
                            with open(image_filename, "wb") as f:
                                f.write(image_bytes)

                            # Store image metadata for later association
                            image_data.append({
                                "path": image_filename,
                                "page_num": page_num,
                                "width": width,
                                "height": height,
                                "size": width * height  # for size sorting
                            })
                        except Exception as e:
                            print(f"Error processing image: {e}")

            # Sort images by size (largest first)
            image_data.sort(key=lambda x: x["size"], reverse=True)

            return image_data

        except Exception as e:
            print(f"Error extracting images from PDF: {e}")
            return []