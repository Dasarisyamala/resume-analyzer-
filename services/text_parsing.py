import re
from typing import Dict, Optional

SECTION_PATTERN = r"{label}[:\s]+([\w\W]+?)(?:\n\s*\n|$)"


def extract_with_regex(pattern: str, text: str) -> Optional[str]:
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def parse_contact_details(text: str) -> Dict[str, Optional[str]]:
    name = extract_with_regex(r"(?:name|candidate)[:\s]*([A-Za-z ,.]+)", text)
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone_match = re.search(r"(\+?\d[\d\s-]{8,}\d)", text)

    if not name:
        first_line = text.strip().splitlines()[0]
        name = first_line.strip() if len(first_line.split()) <= 5 else None

    return {
        "name": name,
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
    }


def extract_section(label: str, text: str) -> Optional[str]:
    pattern = SECTION_PATTERN.format(label=re.escape(label))
    return extract_with_regex(pattern, text)


def estimate_years_experience(text: str) -> Optional[float]:
    matches = re.findall(r"(\d+)(?:\+)?\s+years", text, re.IGNORECASE)
    if not matches:
        return None
    numbers = [int(m) for m in matches]
    return max(numbers)


def parse_resume_details(text: str) -> Dict[str, Optional[str]]:
    details = parse_contact_details(text)
    details["education"] = extract_section("Education", text)
    details["experience"] = extract_section("Experience", text)
    details["summary"] = extract_section("Summary", text)
    details["years_experience"] = estimate_years_experience(
        details.get("experience") or text
    )
    return details
