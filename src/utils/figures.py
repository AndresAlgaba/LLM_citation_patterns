import re

import numpy as np


def count_words(s):
    words = re.findall(r"\b\w+\b", s)
    return len(words)


def average_word_length(s):
    word_count = count_words(s)
    return len(s) / word_count if word_count else 0


def count_words_in_title(title, patterns, word_count):
    for word, pattern in patterns.items():
        if re.search(pattern, title.lower()):
            word_count[word] += 1


def plot_data_with_limits(
    ax,
    positive_words,
    positive_freqs,
    negative_words,
    negative_freqs,
    title,
    max_positive,
    max_negative,
):
    x_pos = np.arange(len(positive_words))
    ax.bar(
        x_pos,
        positive_freqs,
        align="edge",
        color="green",
        edgecolor="black",
    )
    for i, (word, freq) in enumerate(zip(positive_words, positive_freqs)):
        ax.text(
            i + 0.4,
            freq + 0.5,
            f"{word}\n({freq})",
            ha="center",
            va="bottom",
        )

    x_neg = np.arange(len(negative_words))
    ax.bar(
        x_neg + len(positive_words),
        -np.array(negative_freqs),
        align="edge",
        color="red",
        edgecolor="black",
    )
    for i, (word, freq) in enumerate(zip(negative_words, negative_freqs)):
        ax.text(
            i + 0.4 + len(positive_words),
            -freq - 0.5,
            f"{word}\n({freq})",
            ha="center",
            va="top",
        )

    # Remove axes and ticks
    ax.axis("off")

    # Set y-limits
    ax.set_ylim(-max_negative - 5, max_positive + 5)

    # Add title
    ax.set_title(title)
