import re
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')


def find_surrounding_sentences(text, number, keep=3):
    sentences = sent_tokenize(text)
    for i, sentence in enumerate(sentences):
        if re.search(r'\[\s*{}\s*\]'.format(number), sentence):
            start_index = max(0, i - keep)
            end_index = min(i + keep, len(sentences) - 1)
            sentences[i] = f"<b>{sentence}</b>"
            small_text = sentences[start_index:i] + [sentences[i]] + sentences[i + 1:end_index + 1]
            return " ".join(small_text)
    return None


def remove_brackets_except_number(text, preserve_number):
    """
    Removes all occurrences of brackets containing numbers from the text, except for brackets
    containing a specific number specified by 'preserve_number'.

    Parameters:
    - text (str): The input text from which to remove the brackets.
    - preserve_number (int): The number inside brackets to preserve in the text.

    Returns:
    - str: The text with specified brackets removed, except for the one containing 'preserve_number'.
    """
    # Regular expression to match brackets with numbers, excluding the specified preserve_number
    # The regex includes a negative lookahead to ensure the preserve_number is not matched
    pattern = re.compile(r'\[(?!\s*{}\s*\])\s*\d+([\s,-]*\d*)*\s*\]'.format(preserve_number))

    # Replace matched patterns with an empty string, effectively removing them
    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text

