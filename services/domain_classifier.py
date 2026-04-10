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


def _resolve_domains(preferred_domains: Iterable[str] | None) -> dict[str, set[str]]:
    if not preferred_domains:
        return DOMAIN_KEYWORDS

    selected = {}
    normalized_map = {name.lower(): name for name in DOMAIN_KEYWORDS}

    for item in preferred_domains:
        key = item.strip().lower()
        if key in normalized_map:
            domain_name = normalized_map[key]
            selected[domain_name] = DOMAIN_KEYWORDS[domain_name]

    return selected or DOMAIN_KEYWORDS


def classify_domain(
    skills: Iterable[str],
    text: str,
    preferred_domains: Iterable[str] | None = None,
) -> Tuple[str, Counter]:
    """Return (best_domain, score_breakdown)."""

    text_tokens = set(text.lower().split())
    skill_tokens = {skill.lower() for skill in skills}

    scores = Counter()
    domains_to_use = _resolve_domains(preferred_domains)
    for domain, keywords in domains_to_use.items():
        keyword_hits = len(keywords & text_tokens)
        skill_hits = len(keywords & skill_tokens)
        scores[domain] = keyword_hits + (2 * skill_hits)

    best_domain = scores.most_common(1)
    if not best_domain or best_domain[0][1] == 0:
        return "General", scores

    return best_domain[0][0], scores
