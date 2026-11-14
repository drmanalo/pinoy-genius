"""The word bank: categories mapped to Taglish words."""
import random

WORDS = {
    "Tao": ["tongue", "doktor", "alak-alakan", "hintuturo", "sakong", "Jose Rizal", "Tandang Sora", "Brad Pitt"],
    "Bagay": ["payong", "tsinelas", "jeepney", "cellphone", "walis", "unan", "relo", "bola"],
    "Hayop": ["aso", "pusa", "kalabaw", "buwaya", "tarsier", "ahas", "palaka", "manok"],
    "Lugar": ["Luneta", "palengke", "simbahan", "paaralan", "Boracay", "ospital", "dagat", "bundok"],
    "Pagkain": ["adobo", "halo-halo", "mangga", "sinigang", "pandesal", "lechon", "turon", "balut"],
    "Halaman": ["saging", "niyog", "sampaguita", "kawayan", "bayabas", "santol"],
}

CATEGORIES = list(WORDS)


def category_of(word):
    """Return the category a word belongs to."""
    for category, words in WORDS.items():
        if word in words:
            return category
    raise KeyError(word)


def pick_board(n=5, rng=random):
    """Pick n distinct words, each from a different category when possible."""
    categories = rng.sample(CATEGORIES, min(n, len(CATEGORIES)))
    board = [rng.choice(WORDS[category]) for category in categories]
    while len(board) < n:
        extra = rng.choice([w for ws in WORDS.values() for w in ws])
        if extra not in board:
            board.append(extra)
    rng.shuffle(board)
    return board
