"""CWE category mappings and keyword lists for enrichment."""

# Map CWE ID strings to category slugs
CWE_CATEGORY_MAP = {}

_CATEGORY_CWES = {
    "injection": [77, 78, 79, 80, 89, 90, 91, 94, 95, 96, 943],
    "memory": [119, 120, 121, 122, 124, 125, 126, 127, 131, 170, 415, 416, 476, 680, 787, 788, 805, 806, 822, 823, 824, 825],
    "auth": [250, 280, 284, 285, 287, 288, 290, 294, 306, 307, 352, 384, 522, 613, 620, 639, 640, 798, 862, 863],
    "crypto": [295, 310, 320, 326, 327, 328, 330, 331, 338, 347],
    "config": [16, 269, 276, 434, 502, 611, 668, 732, 829, 918],
    "info-disclosure": [200, 201, 203, 209, 215, 312, 319, 359, 532, 538, 548],
}

for category, cwe_ids in _CATEGORY_CWES.items():
    for cwe_id in cwe_ids:
        CWE_CATEGORY_MAP[str(cwe_id)] = category


def get_category(cwe_id):
    """Get category for a CWE ID string (e.g., '79' or 'CWE-79')."""
    clean_id = str(cwe_id).replace("CWE-", "")
    return CWE_CATEGORY_MAP.get(clean_id, "other")


# Keywords associated with common CWEs for description matching
CWE_KEYWORDS = {
    "20": ["input", "validation", "invalid", "unexpected", "improper"],
    "22": ["path", "traversal", "directory", "../", "file", "access"],
    "77": ["command", "injection", "OS", "shell", "system", "exec"],
    "78": ["command", "injection", "OS", "shell", "system", "exec", "subprocess"],
    "79": ["script", "XSS", "cross-site", "reflected", "stored", "DOM", "sanitiz", "escap", "HTML", "JavaScript"],
    "89": ["SQL", "query", "injection", "database", "parameteriz"],
    "94": ["code", "injection", "eval", "execute", "interpret"],
    "119": ["buffer", "overflow", "bounds", "memory", "read", "write"],
    "120": ["buffer", "copy", "overflow", "classic", "strcpy"],
    "125": ["out-of-bounds", "read", "buffer", "memory", "heap"],
    "190": ["integer", "overflow", "wrap", "arithmetic"],
    "200": ["information", "exposure", "sensitive", "leak", "disclose"],
    "269": ["privilege", "improper", "management", "escalat"],
    "276": ["permission", "default", "incorrect", "world"],
    "284": ["access", "control", "improper", "restrict"],
    "287": ["authentication", "improper", "login", "credential", "bypass"],
    "306": ["authentication", "missing", "critical", "function"],
    "312": ["cleartext", "storage", "sensitive", "plaintext", "password"],
    "319": ["cleartext", "transmission", "sensitive", "HTTP", "unencrypted"],
    "327": ["cryptograph", "broken", "weak", "algorithm", "cipher"],
    "330": ["random", "insufficient", "PRNG", "predictab"],
    "352": ["CSRF", "cross-site", "request", "forgery", "token"],
    "362": ["race", "condition", "concurrent", "TOCTOU", "thread"],
    "400": ["resource", "consumption", "uncontrolled", "exhaust", "denial"],
    "416": ["use-after-free", "freed", "memory", "dangling", "pointer"],
    "434": ["upload", "file", "unrestricted", "dangerous", "type"],
    "476": ["NULL", "pointer", "dereference", "null", "crash"],
    "502": ["deserialization", "untrusted", "serial", "unmarshal"],
    "522": ["credential", "insufficiently", "protected", "password", "weak"],
    "611": ["XXE", "XML", "external", "entity", "DTD", "parser"],
    "668": ["exposure", "resource", "wrong", "sphere"],
    "732": ["permission", "assignment", "incorrect", "critical"],
    "787": ["out-of-bounds", "write", "buffer", "overflow", "memory", "heap", "stack"],
    "798": ["hard-coded", "credential", "hardcoded", "password", "secret", "embedded"],
    "862": ["authorization", "missing", "access", "control"],
    "863": ["authorization", "incorrect", "access", "control", "bypass"],
    "918": ["SSRF", "server-side", "request", "forgery", "URL", "fetch"],
}
