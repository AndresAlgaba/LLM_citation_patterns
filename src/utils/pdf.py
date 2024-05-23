import re

from PyPDF2 import PdfReader


def _extract_reference_numbers(text):
    """Extract the reference numbers from the text.

    We use the following regex to extract the reference numbers:
    \[\s*(.*?)\s*\]. We then split the reference numbers by comma and
    hyphen. We then add the numbers to a set. We then return the sorted
    list of numbers.
    """
    mentioned_references = re.findall(r"\[\s*(.*?)\s*\]", text)
    mentioned_ref_numbers = set()

    for ref in mentioned_references:
        for part in ref.split(","):
            part = part.strip()
            if "-" in part or "–" in part:
                delimiter = "-" if "-" in part else "–"
                try:
                    start, end = map(int, part.split(delimiter))
                    mentioned_ref_numbers.update(list(range(start, end + 1)))
                except ValueError:
                    continue
            else:
                try:
                    mentioned_ref_numbers.add(int(part))
                except ValueError:
                    continue

    return sorted(mentioned_ref_numbers)


def transform_pdf_to_txt(filename):
    """Transform a pdf file to a txt file."""
    with open(filename, "rb") as file:
        pdf = PdfReader(file)
        text = ""
        for page in range(len(pdf.pages)):
            text += pdf.pages[page].extract_text()
    return text


def clean_txt(text):
    """Clean the text by removing redundant white space etc."""
    text = text.strip()
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def split_text_and_references(text):
    """Split the text into main content and references.

    We use the keyword "References" to split the text.
    """
    references_keyword = re.compile(r"\b\d*(?:References|REFERENCES)\b")
    main_content, references = re.split(references_keyword, text, 1)

    return main_content, references


def extract_intro_references(text, references):
    """Extract the references from the introduction.

    We use the following regex to extract the reference numbers:
    \[\s*(.*?)\s*\]. We then split the reference numbers by comma and
    hyphen. We then add the numbers to a set. We then filter the
    references by checking if the reference number is in the set of
    mentioned reference numbers.
    """
    reference_items = re.findall(
        r"\[\d+\].*?(?=\[\d+\]|$)", references, re.DOTALL
    )
    mentioned_ref_numbers = _extract_reference_numbers(text)

    filtered_reference_items = [
        item
        for item in reference_items
        if int(re.search(r"\[(\d+)\]", item).group(1)) in mentioned_ref_numbers
    ]

    return filtered_reference_items
