import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor


def create_presentation_pptx(slides_data: list, topic: str, output_path: str):
    """
    Slaydlar massivi asosida toza va chiroyli PPTX fayl yasaydi.
    """
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 format
    prs.slide_height = Inches(7.5)

    # 1. Boshlang'ich slayd (Title Slide)
    title_slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(title_slide_layout)
    title = slide.shapes.title
    subtitle = slide.placeholders[1]

    title.text = topic.upper()
    subtitle.text = "Tayyorladi: Talaba\nSun'iy intellekt va Ta'lim ekotizimi"

    # 2. Mazmun slaydlari
    bullet_slide_layout = prs.slide_layouts[1]
    for item in slides_data:
        slide = prs.slides.add_slide(bullet_slide_layout)
        shapes = slide.shapes
        
        # Sarlavha
        title_shape = shapes.title
        title_shape.text = item.get("title", "")

        # Matn va punktlar
        body_shape = shapes.placeholders[1]
        tf = body_shape.text_frame
        tf.word_wrap = True

        bullets = item.get("bullets", [])
        if bullets:
            tf.text = bullets[0]
            for bullet in bullets[1:]:
                p = tf.add_paragraph()
                p.text = bullet
                p.level = 0

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    prs.save(output_path)
    return output_path
