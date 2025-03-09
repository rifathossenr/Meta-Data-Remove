from PyPDF2 import PdfReader, PdfWriter
import os
from datetime import datetime
from app import app
import xml.etree.ElementTree as ET
from io import BytesIO

def get_xmp_metadata(filepath):
    """Extract only XMP metadata from PDF file."""
    try:
        reader = PdfReader(filepath)
        # Get XMP metadata specifically
        xmp_metadata = reader.xmp_metadata
        
        if xmp_metadata:
            # Parse the XMP XML string
            try:
                root = ET.fromstring(xmp_metadata)
                # Create a dictionary of XMP metadata
                metadata = {}
                for child in root.iter():
                    if child.text and child.text.strip():
                        # Remove namespace prefix from tag names
                        tag = child.tag.split('}')[-1]
                        metadata[tag] = child.text.strip()
                return metadata
            except ET.ParseError:
                return {"error": "Invalid XMP metadata format"}
        return {}
    except Exception as e:
        print(f"Error reading XMP metadata: {e}")
        return {}

def remove_xmp_metadata(input_path, output_path):
    """Remove only XMP metadata from PDF file while preserving other metadata."""
    try:
        # Read the PDF
        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)

        # Copy all original metadata except XMP
        metadata = reader.metadata
        if metadata:
            writer.add_metadata(metadata)

        # Clear only XMP metadata by not adding it to the writer
        # PyPDF2 will not include XMP metadata if we don't explicitly add it

        # Write the modified PDF
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)

        return True
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

def cleanup_old_files():
    """Remove files older than the cleanup interval."""
    cleanup_interval = app.config['CLEANUP_INTERVAL']
    current_time = datetime.now()
    
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        if current_time - file_modified > cleanup_interval:
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error removing file {filename}: {e}") 