from collections import Counter
from typing import Iterable, Tuple

DOMAIN_KEYWORDS = {
    "Web Development": {
        "javascript",
        "react",
        "angular",
        "vue",
        "css",
        "html",
        "django",
        "flask",
        "node",
        "express",
    },
    "Data Science": {
        "python",
        "pandas",
        "numpy",
        "matplotlib",
        "statistics",
        "data",
        "sql",
    },
    "Machine Learning": {
        "scikit",
        "tensorflow",
        "keras",
        "pytorch",
        "model",
        "ml",
        "classification",
    },
    "Cyber Security": {
        "penetration",
        "security",
        "owasp",
        "vulnerability",
        "threat",
        "soc",
        "nmap",
    },
    "Cloud Computing": {
        "aws",
        "azure",
        "gcp",
        "cloud",
        "kubernetes",
        "docker",
        "lambda",
    },
    "Android Development": {
        "android",
        "kotlin",
        "java",
        "gradle",
        "compose",
        "studio",
    },
}


def classify_domain(skills: Iterable[str], text: str) -> Tuple[str, Counter]:
    """Return (best_domain, score_breakdown)."""

    text_tokens = set(text.lower().split())
    skill_tokens = {skill.lower() for skill in skills}

    scores = Counter()
    for domain, keywords in DOMAIN_KEYWORDS.items():
        keyword_hits = len(keywords & text_tokens)
        skill_hits = len(keywords & skill_tokens)
        scores[domain] = keyword_hits + (2 * skill_hits)

    best_domain = scores.most_common(1)
    if not best_domain or best_domain[0][1] == 0:
        return "General", scores

    return best_domain[0][0], scores
