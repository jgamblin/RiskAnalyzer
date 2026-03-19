"""Curated CWE confusion pairs and taxonomy-based confusion lookup."""

CURATED_CONFUSIONS = {
    "79": [
        ("89", "SQL Injection targets database queries, not HTML output"),
        ("94", "Code Injection executes arbitrary server-side code, not client-side scripts"),
        ("80", "Basic XSS is a subset — CWE-80 is specifically about script tag injection"),
    ],
    "89": [
        ("79", "XSS targets browser-rendered HTML, not database queries"),
        ("78", "OS Command Injection targets system commands, not SQL"),
        ("94", "Code Injection is broader — SQL Injection specifically targets SQL parsers"),
    ],
    "78": [
        ("77", "CWE-77 is the parent — CWE-78 specifically targets OS commands"),
        ("89", "SQL Injection targets database queries, not OS commands"),
    ],
    "94": [
        ("79", "XSS is specifically client-side script injection in browsers"),
        ("78", "OS Command Injection targets system shells, not application interpreters"),
    ],
    "22": [
        ("23", "CWE-23 is specifically relative path traversal; CWE-22 includes absolute paths too"),
        ("73", "External control of filename is about controlling which file, not traversing directories"),
    ],
    "119": [
        ("787", "CWE-787 is specifically out-of-bounds write; CWE-119 is the broader buffer category"),
        ("125", "CWE-125 is specifically out-of-bounds read; CWE-119 covers both read and write"),
    ],
    "125": [
        ("787", "Out-of-bounds write corrupts data; out-of-bounds read leaks data"),
        ("119", "CWE-119 is the parent category covering all buffer operations"),
    ],
    "787": [
        ("125", "Out-of-bounds read leaks data; out-of-bounds write corrupts data"),
        ("119", "CWE-119 is the parent category covering all buffer operations"),
        ("120", "Classic buffer overflow is a specific type of out-of-bounds write"),
    ],
    "416": [
        ("415", "Double free is freeing memory twice; use-after-free is accessing already-freed memory"),
        ("476", "NULL pointer dereference is accessing address 0; use-after-free is accessing freed heap memory"),
    ],
    "476": [
        ("416", "Use-after-free accesses freed heap memory; NULL dereference accesses address 0"),
        ("125", "Out-of-bounds read accesses wrong addresses; NULL dereference accesses address 0"),
    ],
    "200": [
        ("209", "CWE-209 is specifically about error messages exposing information"),
        ("532", "CWE-532 is specifically about log files containing sensitive information"),
    ],
    "209": [
        ("200", "CWE-200 is the broad category; CWE-209 is specific to error messages"),
        ("532", "CWE-532 is about log files; CWE-209 is about error messages shown to users"),
    ],
    "287": [
        ("306", "CWE-306 is missing authentication entirely; CWE-287 is improper authentication"),
        ("862", "CWE-862 is missing authorization (what you can do); CWE-287 is authentication (who you are)"),
    ],
    "306": [
        ("287", "CWE-287 is improper authentication; CWE-306 is completely missing authentication"),
        ("862", "CWE-862 is missing authorization; CWE-306 is missing authentication"),
    ],
    "862": [
        ("863", "CWE-863 is incorrect authorization; CWE-862 is completely missing authorization"),
        ("287", "CWE-287 is about authentication (who you are); CWE-862 is authorization (what you can do)"),
    ],
    "863": [
        ("862", "CWE-862 is missing authorization entirely; CWE-863 has authorization but it's wrong"),
        ("284", "CWE-284 is the broad access control category; CWE-863 is specifically incorrect authorization"),
    ],
    "352": [
        ("79", "XSS injects scripts into pages; CSRF tricks users into making unwanted requests"),
        ("287", "Authentication verifies identity; CSRF bypasses the trust of an authenticated session"),
    ],
    "434": [
        ("94", "Code Injection is about injecting code into existing execution; unrestricted upload is about uploading malicious files"),
        ("502", "Deserialization processes data formats; file upload is about file types and content"),
    ],
    "502": [
        ("94", "Code Injection injects code into running interpreters; deserialization exploits object reconstruction"),
        ("434", "File upload is about malicious file types; deserialization is about crafted serialized data"),
    ],
    "611": [
        ("918", "SSRF makes the server send requests; XXE exploits XML parsers to read files or make requests"),
        ("776", "CWE-776 is specifically about XML entity expansion (billion laughs); CWE-611 is broader XXE"),
    ],
    "918": [
        ("611", "XXE exploits XML parsers; SSRF directly controls server-side HTTP requests"),
        ("441", "Unintended proxy is about relay; SSRF is about direct server-side request forgery"),
    ],
    "327": [
        ("326", "CWE-326 is about inadequate key length; CWE-327 is about broken/risky algorithms"),
        ("330", "CWE-330 is about weak randomness; CWE-327 is about weak cryptographic algorithms"),
    ],
    "362": [
        ("367", "TOCTOU is a specific type of race condition between check and use"),
        ("400", "Resource exhaustion is about consuming resources; race conditions are about timing"),
    ],
    "190": [
        ("681", "Incorrect conversion can cause data loss; integer overflow wraps around"),
        ("131", "Incorrect buffer size is about allocation; integer overflow is about arithmetic"),
    ],
    "269": [
        ("276", "CWE-276 is incorrect default permissions; CWE-269 is improper privilege management"),
        ("250", "CWE-250 is executing with unnecessary privileges; CWE-269 is the broader management issue"),
    ],
    "732": [
        ("276", "CWE-276 is about default permissions; CWE-732 is about assigned permissions on critical resources"),
        ("269", "CWE-269 is about privilege management; CWE-732 is about file/resource permissions"),
    ],
    "798": [
        ("522", "CWE-522 is insufficiently protected credentials; CWE-798 is hardcoded credentials in source"),
        ("321", "CWE-321 is hard-coded cryptographic keys; CWE-798 is hard-coded passwords/credentials"),
    ],
    "400": [
        ("770", "CWE-770 is allocation without limits; CWE-400 is the broader resource consumption category"),
        ("362", "Race conditions are about timing; resource exhaustion is about consuming too much"),
    ],
    "20": [
        ("79", "XSS is a consequence of improper input validation in web context"),
        ("89", "SQL Injection is a consequence of improper input validation in SQL context"),
    ],
}


def get_confusions(cwe_id, cwe_taxonomy):
    """
    Get confusion CWEs for a given CWE ID.

    Args:
        cwe_id: CWE ID string (e.g., "79")
        cwe_taxonomy: dict mapping CWE IDs to {"name": str, "related": [{"nature": str, "cwe_id": str}]}

    Returns:
        List of {"cwe": "CWE-XX", "name": str, "differentiator": str}
    """
    clean_id = str(cwe_id).replace("CWE-", "")
    confusions = []

    # First: curated confusions (highest quality)
    if clean_id in CURATED_CONFUSIONS:
        for confused_id, differentiator in CURATED_CONFUSIONS[clean_id]:
            name = cwe_taxonomy.get(confused_id, {}).get("name", f"CWE-{confused_id}")
            confusions.append({
                "cwe": f"CWE-{confused_id}",
                "name": name,
                "differentiator": differentiator,
            })

    # Then: taxonomy relationships (PeerOf, ChildOf) for CWEs not already covered
    seen_ids = {c["cwe"] for c in confusions}
    if clean_id in cwe_taxonomy:
        for rel in cwe_taxonomy[clean_id].get("related", []):
            rel_cwe = f"CWE-{rel['cwe_id']}"
            if rel_cwe not in seen_ids and rel["nature"] in ("PeerOf", "CanPrecede", "ChildOf"):
                rel_name = cwe_taxonomy.get(rel["cwe_id"], {}).get("name", rel_cwe)
                rel_desc = cwe_taxonomy.get(rel["cwe_id"], {}).get("description", "")
                differentiator = f"{rel_name}" + (f" — {rel_desc[:100]}..." if rel_desc else "")
                confusions.append({
                    "cwe": rel_cwe,
                    "name": rel_name,
                    "differentiator": differentiator,
                })
                seen_ids.add(rel_cwe)

    return confusions[:5]  # Limit to 5 confusions max
