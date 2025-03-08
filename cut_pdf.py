import os
import fitz  # PyMuPDF

def split_pdf(pdf_file):
    try:
        print(f"Opening original PDF: {pdf_file}")

        # Open the original PDF
        doc = fitz.open(pdf_file)

        # Calculate the halfway point of the original PDF
        original_len = len(doc)
        half_len = original_len // 2

        print(f"Original PDF has {original_len} pages. Keeping the second half.")

        # Create a new PDF with the second half of the original PDF
        new_pdf = fitz.open()
        for page_num in range(half_len, original_len):
            new_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)

        # Save the new PDF with the second half
        new_pdf_file = f"half_{os.path.basename(pdf_file)}"
        new_pdf.save(new_pdf_file)
        new_pdf.close()

        print(f"New PDF file with second half saved as {new_pdf_file}")

        # Remove the original PDF
        print(f"Removing original PDF file {pdf_file}")
        os.remove(pdf_file)
        
        if '.' in pdf_file:
            pdf_file = pdf_file.replace(".", "- Part-2.", 1)
        else:
            pdf_file = f"{pdf_file}- Part - 2"
            
            
        # Rename the new PDF to the original filename
        print(f"Renaming {new_pdf_file} to {pdf_file}")
        os.rename(new_pdf_file, pdf_file)

        doc1 = fitz.open(pdf_file)
        le = len(doc1)
        print(f"Successfully processed: {pdf_file}, remaining pages: {le}")
        return le

    except Exception as e:
        print(f"Error occurred: {e}")
        return False
