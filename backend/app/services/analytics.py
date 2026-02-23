from collections import Counter
from typing import List
import re


def extract_bigrams(text: str) -> List[str]:
    """Extract bigrams from text for clustering."""
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    stop_words = {"the", "and", "for", "are", "was", "but", "not", "you", "all", "can",
                  "has", "him", "his", "how", "its", "our", "out", "who", "did", "get",
                  "may", "yes", "use", "say", "she", "her", "had", "any", "from", "they",
                  "what", "this", "that", "with", "have", "will", "your", "just", "know",
                  "into", "more", "when", "than", "then", "some", "very", "about", "like"}
    words = [w for w in words if w not in stop_words]
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]
    return bigrams + words


def get_question_clusters(messages: List[str], top_n: int = 5) -> List[dict]:
    """Get top keyword/bigram clusters from student messages."""
    all_terms: List[str] = []
    for msg in messages:
        all_terms.extend(extract_bigrams(msg))
    counter = Counter(all_terms)
    return [{"keyword": term, "count": count} for term, count in counter.most_common(top_n)]
