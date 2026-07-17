from pdfminer.high_level import extract_text
import arabic_reshaper
from bidi.algorithm import get_display


def fix_persian_text(text):

    reshaped = arabic_reshaper.reshape(text)

    bidi_text = get_display(
        reshaped
    )

    return bidi_text



def read_pdf(file):

    file.seek(0)

    text = extract_text(file)

    text = fix_persian_text(text)

    return text