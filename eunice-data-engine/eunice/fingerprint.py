"""fingerprint technical debt items for deduplication"""
import hashlib
from typing import List, Dict


def generate_fingerprint(finding: Dict) -> str:
    """
    create stable fingerprint for debt item
    
    reuses gitlab code quality fingerprint when available
    otherwise creates from file + location + rule
    """
    
    if finding.get('code_quality_fingerprint'):
        # reuse gitlab's fingerprint
        return finding['code_quality_fingerprint']
    
    # create our own
    components = [
        finding.get('type', ''),           # e.g. "high_complexity"
        finding.get('file', ''),           # e.g. "auth.py"
        finding.get('lines', ''),          # e.g. "45-120"
        finding.get('rule_id', '')         # e.g. "cyclomatic_complexity"
    ]
    
    fingerprint_string = '|'.join(str(c) for c in components)
    return hashlib.sha256(fingerprint_string.encode()).hexdigest()[:16]


def deduplicate_findings(findings: List[Dict]) -> List[Dict]:
    """remove duplicate findings based on fingerprint"""
    seen = set()
    unique = []
    
    for finding in findings:
        fp = generate_fingerprint(finding)
        if fp not in seen:
            seen.add(fp)
            finding['fingerprint'] = fp
            unique.append(finding)
    
    return unique
