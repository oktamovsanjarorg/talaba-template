import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE


def create_presentation_pptx(slides_data: list, topic: str, output_path: str, student_name: str = "Talaba"):
    """
    16:9 formatdagi zamonaviy, ranglar palitrasiga ega PowerPoint taqdimot generatori.
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 Widescreen
    prs.slide_height = Inches(7.5)

    # Ranglar palitrasi (Modern Navy & Emerald)
    COLOR_DARK_BG = RGBColor(15, 23, 42)      # Slate 900
    COLOR_PRIMARY = RGBColor(30, 58, 138)     # Blue 900
    COLOR_ACCENT = RGBColor(13, 148, 136)     # Teal 600
    COLOR_WHITE = RGBColor(255, 255, 255)
    COLOR_TEXT_DARK = RGBColor(30, 41, 59)    # Slate 800
    COLOR_CARD_BG = RGBColor(241, 245, 249)   # Slate 100

    blank_layout = prs.slide_layouts[6]

    # ================= 1. TITUL SLAYDI =================
    slide1 = prs.slides.add_slide(blank_layout)
    
    # Orqa fon (Dark Gradient / Solid)
    bg = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_DARK_BG
    bg.line.fill.background()

    # Dekorativ aksent chiziq
    accent_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(1.5), Inches(0.2), Inches(3.5))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = COLOR_ACCENT
    accent_bar.line.fill.background()

    # Sarlavha qutisi
    tx_box = slide1.shapes.add_textbox(Inches(1.6), Inches(1.5), Inches(10.5), Inches(2.5))
    tf = tx_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = topic.upper()
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.font.name = "Arial"

    # Muallif va sana
    info_box = slide1.shapes.add_textbox(Inches(1.6), Inches(4.5), Inches(10), Inches(1.5))
    tf_info = info_box.text_frame
    p_info = tf_info.paragraphs[0]
    p_info.text = f"Tayyorladi: {student_name}\nAkademik taqdimot | 2026-yil"
    p_info.font.size = Pt(20)
    p_info.font.color.rgb = RGBColor(148, 163, 184) # Slate 400
    p_info.font.name = "Arial"

    # ================= 2. MAZMUN SLAYDLARI =================
    for idx, item in enumerate(slides_data, 1):
        slide = prs.slides.add_slide(blank_layout)

        # Yuqori sarlavha paneli
        header_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(1.3))
        header_bar.fill.solid()
        header_bar.fill.fore_color.rgb = COLOR_PRIMARY
        header_bar.line.fill.background()

        # Raqam badji (01, 02...)
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.3), Inches(0.9), Inches(0.7))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_ACCENT
        badge.line.fill.background()
        tf_b = badge.text_frame
        p_b = tf_b.paragraphs[0]
        p_b.text = f"{idx:02d}"
        p_b.alignment = PP_ALIGN.CENTER
        p_b.font.size = Pt(18)
        p_b.font.bold = True
        p_b.font.color.rgb = COLOR_WHITE

        # Slayd sarlavhasi
        title_box = slide.shapes.add_textbox(Inches(1.9), Inches(0.25), Inches(10.5), Inches(0.8))
        tf_t = title_box.text_frame
        p_t = tf_t.paragraphs[0]
        p_t.text = item.get("title", f"{idx}-Mavzu")
        p_t.font.size = Pt(26)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_WHITE
        p_t.font.name = "Arial"

        # Tezislar uchun kartochkalar (Cards)
        bullets = item.get("bullets", [])
        top_pos = 1.7
        for b_idx, bullet in enumerate(bullets):
            # Kartochka foni
            card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(top_pos), Inches(11.3), Inches(1.1))
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_CARD_BG
            card.line.color.rgb = RGBColor(226, 232, 240)
            card.line.width = Pt(1)

            # Chap aksent nuqta
            dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.3), Inches(top_pos + 0.35), Inches(0.35), Inches(0.35))
            dot.fill.solid()
            dot.fill.fore_color.rgb = COLOR_ACCENT
            dot.line.fill.background()

            # Matn
            c_box = slide.shapes.add_textbox(Inches(1.8), Inches(top_pos + 0.1), Inches(10.2), Inches(0.9))
            tf_c = c_box.text_frame
            tf_c.word_wrap = True
            p_c = tf_c.paragraphs[0]
            p_c.text = bullet
            p_c.font.size = Pt(17)
            p_c.font.color.rgb = COLOR_TEXT_DARK
            p_c.font.name = "Arial"

            top_pos += 1.3

    # ================= 3. YAKUNIY SLAYD =================
    slide_end = prs.slides.add_slide(blank_layout)
    bg_end = slide_end.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg_end.fill.solid()
    bg_end.fill.fore_color.rgb = COLOR_DARK_BG
    bg_end.line.fill.background()

    end_box = slide_end.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.3), Inches(2.5))
    tf_end = end_box.text_frame
    p_end = tf_end.paragraphs[0]
    p_end.alignment = PP_ALIGN.CENTER
    p_end.text = "E'TIBORINGIZ UCHUN RAHMAT!"
    p_end.font.size = Pt(38)
    p_end.font.bold = True
    p_end.font.color.rgb = COLOR_WHITE
    p_end.font.name = "Arial"

    p_sub = tf_end.add_paragraph()
    p_sub.alignment = PP_ALIGN.CENTER
    p_sub.text = "\nSavollar va fikr-mulohazalar uchun tayyormiz"
    p_sub.font.size = Pt(22)
    p_sub.font.color.rgb = COLOR_ACCENT
    p_sub.font.name = "Arial"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    return output_path
