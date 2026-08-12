from fpdf import FPDF
from pathlib import Path
from pypdf import PdfReader
import io

def generate_offer_letter(candidate_name: str, salary: float) -> str:
    """Generates a structured PDF contract."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    
    pdf.cell(190, 10, txt=f"Official Offer of Employment: {candidate_name}", ln=1, align="C")
    pdf.set_font("Helvetica", size=12)
    pdf.cell(190, 10, txt="Position: Agentic AI Engineer", ln=1, align="L")
    pdf.cell(190, 10, txt=f"Agreed Base Compensation: ${salary:,.2f} USD", ln=1, align="L")
    pdf.cell(190, 10, txt="Status: Cleared via AI Compliance Guardrails", ln=1, align="L")
    
    out_dir = Path("data/offers")
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"{candidate_name.replace(' ', '_')}_Contract.pdf"
    
    pdf.output(str(file_path))
    return str(file_path)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts raw text from any uploaded PDF resume."""
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"