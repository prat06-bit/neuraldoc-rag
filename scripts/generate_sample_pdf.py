"""Dev utility — generates sample.pdf for testing the RAG pipeline."""

from fpdf import FPDF


class SamplePDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "RAG System Test Document - Confidential", align="C")
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")

def build():
    pdf = SamplePDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Medical Research Summary Report", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 11)
    pdf.cell(0, 8, "Domain: Oncology | Version 1.0 | March 2025", ln=True, align="C")
    pdf.ln(6)

    # Section 1
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "1. Introduction", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, (
        "This document summarises the findings of a multi-centre clinical trial "
        "investigating the efficacy of immunotherapy in patients diagnosed with "
        "stage III non-small cell lung cancer (NSCLC). The trial enrolled 1,240 "
        "patients across 18 institutions over a period of 36 months. "
        "Randomisation was stratified by PD-L1 expression level and ECOG "
        "performance status. The primary endpoint was progression-free survival "
        "(PFS) at 12 months. Secondary endpoints included overall survival (OS), "
        "objective response rate (ORR), and quality-of-life scores measured using "
        "the EORTC QLQ-C30 instrument.\n\n"
        "Immunotherapy has emerged as a cornerstone of modern oncology practice. "
        "Checkpoint inhibitors targeting PD-1 and PD-L1 pathways have demonstrated "
        "durable responses in a subset of patients, though predictive biomarkers "
        "remain an active area of investigation. This trial sought to determine "
        "whether combination immunotherapy confers a statistically significant "
        "benefit over monotherapy in biomarker-unselected populations."
    ))
    pdf.ln(4)

    # Section 2
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "2. Methodology", ln=True)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2.1 Patient Selection Criteria", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, (
        "Eligible patients were adults aged 18 to 80 years with histologically "
        "confirmed stage III NSCLC, an ECOG performance status of 0 or 1, and "
        "adequate organ function as defined by protocol-specified laboratory "
        "thresholds. Patients with active autoimmune disease, prior checkpoint "
        "inhibitor therapy, or systemic corticosteroid use within 14 days of "
        "enrolment were excluded. Written informed consent was obtained from all "
        "participants prior to any study-related procedures."
    ))
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2.2 Treatment Arms", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, (
        "Patients were randomised 1:1 to receive either combination nivolumab plus "
        "ipilimumab (Arm A) or nivolumab monotherapy (Arm B). Arm A received "
        "nivolumab 3 mg/kg intravenously every two weeks plus ipilimumab 1 mg/kg "
        "every six weeks. Arm B received nivolumab 480 mg flat dose every four "
        "weeks. Treatment continued until disease progression, unacceptable "
        "toxicity, or withdrawal of consent, for a maximum of 24 months."
    ))
    pdf.ln(4)

    # Section 3 - Results with table
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "3. Results", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, (
        "At the pre-specified interim analysis (median follow-up 14.3 months), "
        "combination therapy demonstrated a statistically significant improvement "
        "in progression-free survival compared to monotherapy. The hazard ratio "
        "for disease progression or death was 0.71 (95% CI 0.58-0.87, p=0.0008). "
        "Median PFS was 9.2 months in Arm A versus 6.8 months in Arm B."
    ))
    pdf.ln(4)

    # Table
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Table 1: Primary and Secondary Endpoint Summary", ln=True)
    pdf.ln(1)

    headers = ["Endpoint", "Arm A (Combo)", "Arm B (Mono)", "p-value"]
    col_w = [70, 38, 38, 28]

    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Helvetica", "B", 10)
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 8, h, border=1, fill=True)
    pdf.ln()

    rows = [
        ["PFS at 12 months",      "48.3%", "37.1%", "0.0008"],
        ["Median PFS (months)",   "9.2",   "6.8",   "-"],
        ["Overall Survival (OS)", "72.4%", "64.9%", "0.034"],
        ["Obj. Response Rate",    "41.2%", "29.7%", "0.001"],
        ["Grade 3-4 AEs",         "28.6%", "14.3%", "-"],
    ]

    pdf.set_font("Helvetica", "", 10)
    fill = False
    pdf.set_fill_color(245, 245, 245)
    for row in rows:
        for i, cell in enumerate(row):
            pdf.cell(col_w[i], 7, cell, border=1, fill=fill)
        pdf.ln()
        fill = not fill

    pdf.ln(5)

    # Section 4
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "4. Discussion", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, (
        "The results of this trial confirm the superiority of combination "
        "checkpoint blockade in improving progression-free survival among patients "
        "with stage III NSCLC. The magnitude of benefit (HR 0.71) is consistent "
        "with findings from the CheckMate 9LA and KEYNOTE-789 trials, supporting "
        "the generalisability of dual checkpoint inhibition. However, the increased "
        "rate of grade 3-4 adverse events (28.6% vs 14.3%) warrants careful "
        "patient selection and proactive toxicity management.\n\n"
        "Subgroup analyses revealed that patients with a PD-L1 tumour proportion "
        "score (TPS) >= 50% derived the greatest benefit (HR 0.58), while those "
        "with TPS < 1% showed a non-significant trend (HR 0.84, 95% CI 0.63-1.12). "
        "These findings suggest that PD-L1 expression remains an imperfect but "
        "clinically relevant biomarker for treatment selection."
    ))
    pdf.ln(4)

    # Section 5
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "5. Conclusions", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, (
        "Combination nivolumab plus ipilimumab significantly improves "
        "progression-free survival compared to nivolumab monotherapy in patients "
        "with stage III NSCLC. The benefit is most pronounced in patients with "
        "high PD-L1 expression. Toxicity is manageable but requires vigilant "
        "monitoring. These results support the consideration of combination "
        "immunotherapy as a standard-of-care option for eligible patients. "
        "Further biomarker research is needed to optimise patient selection."
    ))
    pdf.ln(6)

    # References
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "References", ln=True)
    pdf.set_font("Helvetica", "", 10)
    refs = [
        "[1] Hellmann MD et al. Nivolumab plus Ipilimumab in Lung Cancer. "
        "N Engl J Med. 2019;381:2020-2031.",
        "[2] Paz-Ares L et al. KEYNOTE-789: Pembrolizumab in NSCLC. "
        "J Clin Oncol. 2023;41:1240-1250.",
        "[3] Reck M et al. CheckMate 9LA: Nivolumab plus Ipilimumab. "
        "J Thorac Oncol. 2021;16(1):49-61.",
    ]
    for ref in refs:
        pdf.multi_cell(0, 6, ref)
        pdf.ln(1)

    pdf.output("tests/fixtures/sample.pdf")
    print("tests/fixtures/sample.pdf created successfully.")


if __name__ == "__main__":
    build()
