"""CVSS vector label lookups and rationale generation."""

CVSS3_LABELS = {
    "AV": {"N": "attack is network-accessible", "A": "attack requires adjacent network access", "L": "attack requires local access", "P": "attack requires physical access"},
    "AC": {"L": "low attack complexity", "H": "high attack complexity"},
    "PR": {"N": "no privileges required", "L": "low privileges required", "H": "high privileges required"},
    "UI": {"N": "no user interaction needed", "R": "requires user interaction"},
    "S": {"U": "scope is unchanged", "C": "scope is changed (can affect other components)"},
    "C": {"H": "high confidentiality impact", "L": "low confidentiality impact", "N": "no confidentiality impact"},
    "I": {"H": "high integrity impact", "L": "low integrity impact", "N": "no integrity impact"},
    "A": {"H": "high availability impact", "L": "low availability impact", "N": "no availability impact"},
}

CVSS4_LABELS = {
    "AV": {"N": "attack is network-accessible", "A": "attack requires adjacent network access", "L": "attack requires local access", "P": "attack requires physical access"},
    "AC": {"L": "low attack complexity", "H": "high attack complexity"},
    "AT": {"N": "no attack requirements", "P": "specific attack requirements needed"},
    "PR": {"N": "no privileges required", "L": "low privileges required", "H": "high privileges required"},
    "UI": {"N": "no user interaction needed", "P": "passive user interaction", "A": "active user interaction required"},
    "VC": {"H": "high confidentiality impact on vulnerable system", "L": "low confidentiality impact on vulnerable system", "N": "no confidentiality impact on vulnerable system"},
    "VI": {"H": "high integrity impact on vulnerable system", "L": "low integrity impact on vulnerable system", "N": "no integrity impact on vulnerable system"},
    "VA": {"H": "high availability impact on vulnerable system", "L": "low availability impact on vulnerable system", "N": "no availability impact on vulnerable system"},
    "SC": {"H": "high confidentiality impact on subsequent systems", "L": "low confidentiality impact on subsequent systems", "N": "no confidentiality impact on subsequent systems"},
    "SI": {"H": "high integrity impact on subsequent systems", "L": "low integrity impact on subsequent systems", "N": "no integrity impact on subsequent systems"},
    "SA": {"H": "high availability impact on subsequent systems", "L": "low availability impact on subsequent systems", "N": "no availability impact on subsequent systems"},
}


def parse_cvss3_vector(vector_string):
    """Parse 'CVSS:3.1/AV:N/AC:L/...' into {'AV': 'N', 'AC': 'L', ...}"""
    if not vector_string or '/' not in vector_string:
        return {}
    parts = vector_string.split('/')
    result = {}
    for part in parts[1:]:  # Skip "CVSS:3.x" prefix
        if ':' in part:
            key, val = part.split(':', 1)
            result[key] = val
    return result


def cvss3_rationale(score, vector_string):
    """Generate English rationale from CVSS 3.x score and vector."""
    components = parse_cvss3_vector(vector_string)
    if not components:
        return f"Score of {score}."
    phrases = []
    for metric, value in components.items():
        if metric in CVSS3_LABELS and value in CVSS3_LABELS[metric]:
            phrases.append(CVSS3_LABELS[metric][value])
    return f"Score of {score}: {'; '.join(phrases)}."


def parse_cvss4_vector(vector_string):
    """Parse 'CVSS:4.0/AV:N/AC:L/...' into {'AV': 'N', 'AC': 'L', ...}"""
    if not vector_string or '/' not in vector_string:
        return {}
    parts = vector_string.split('/')
    result = {}
    for part in parts[1:]:
        if ':' in part:
            key, val = part.split(':', 1)
            result[key] = val
    return result


def cvss4_rationale(score, vector_string):
    """Generate English rationale from CVSS 4.0 score and vector."""
    components = parse_cvss4_vector(vector_string)
    if not components:
        return f"Score of {score}."
    phrases = []
    for metric, value in components.items():
        if metric in CVSS4_LABELS and value in CVSS4_LABELS[metric]:
            phrases.append(CVSS4_LABELS[metric][value])
    return f"Score of {score}: {'; '.join(phrases)}."
