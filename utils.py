import random

SYNONYMS = {
    "good": ["great", "excellent", "fantastic", "wonderful"],
    "bad": ["terrible", "awful", "horrible", "poor"],
    "service": ["experience", "assistance", "help"],
    "food": ["dishes", "cuisine", "meals"],
    "place": ["establishment", "spot", "location"],
}

def spin_text(text):
    """Spin text using synonyms to randomize review content."""
    words = text.split()
    spun_words = [
        random.choice(SYNONYMS.get(word.lower().strip(".,!?"), [word]))
        for word in words
    ]
    return " ".join(spun_words)