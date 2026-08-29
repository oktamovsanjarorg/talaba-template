import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


def create_referat_docx(data: dict, output_path: str, student_name: str = "Talaba", university: str = "O'zbekiston Milliy Universiteti"):
    """
    O'zbekiston akademik talablariga mos chiroyli Word referatini yasaydi.
    """
    doc = Document()

    # Chekka masofalari (Margins): Chap 3cm, O'ng 1.5cm, Yuqori/Past 2cm
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.18)
        section.right_margin = Inches(0.6)

    # 1. TITUL VARAG'I
    p_ministry = doc.add_paragraph()
    p_ministry.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_ministry.add_run("O'ZBEKISTON RESPUBLIKASI OLIY TA'LIM, FAN VA INNOVATSIYALAR VAZIRLIGI\n")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)
    run.bold = True

    p_univ = doc.add_paragraph()
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_univ.add_run(f"{university.upper()}\n\n\n")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(13)
    run.bold = True

    p_type = doc.add_paragraph()
    p_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_type.add_run("REFERAT\n\n")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(22)
    run.bold = True

    p_theme = doc.add_paragraph()
    p_theme.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_theme.add_run(f"Mavzu: \"{data.get('title', 'Mavzu')}\"\n\n\n\n")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(14)
    run.bold = True

    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p_info.add_run(f"Bajardi: {student_name}\nQabul qildi: O'qituvchi\n\n\n\n")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(13)

    p_city = doc.add_paragraph()
    p_city.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_city.add_run("Toshkent — 2026")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(12)

    doc.add_page_break()

    # 2. REJA (Mundarija)
    p_plan_title = doc.add_paragraph()
    p_plan_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_plan_title.add_run("REJA:\n")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(15)
    run.bold = True

    for item in data.get('plan', []):
        p_item = doc.add_paragraph()
        run = p_item.add_run(item)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

    doc.add_page_break()

    def add_section(title: str, content: str):
        p_h = doc.add_paragraph()
        p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p_h.add_run(title.upper())
        run.font.name = 'Times New Roman'
        run.font.size = Pt(15)
        run.bold = True

        p_c = doc.add_paragraph()
        p_c.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_c.paragraph_format.first_line_indent = Inches(0.5)
        p_c.paragraph_format.line_spacing = 1.5
        run = p_c.add_run(content)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        doc.add_paragraph()

    # 3. KIRISH
    add_section("KIRISH", data.get('introduction', ''))

    # 4. ASOSIY BOBLAR
    for chapter in data.get('chapters', []):
        add_section(chapter.get('title', ''), chapter.get('content', ''))

    # 5. XULOSA
    add_section("XULOSA", data.get('conclusion', ''))

    # 6. ADABIYOTLAR RO'YXATI
    p_ref_title = doc.add_paragraph()
    p_ref_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_ref_title.add_run("FOYDALANILGAN ADABIYOTLAR")
    run.font.name = 'Times New Roman'
    run.font.size = Pt(15)
    run.bold = True

    for ref in data.get('references', []):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.line_spacing = 1.5
        run = p_ref.add_run(ref)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    return output_path
