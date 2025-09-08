# Intrabot-Ai/src/rbac.py
# Simple demo RBAC: maps roles to allowed source filenames

ROLE_RULES = {
    "employee": ["hr_faq.md", "onboarding_guide.md", "employee_handbook.md"],
    "hr": ["hr_faq.md", "employee_handbook.md"],
    "it": ["onboarding_guide.md"],
    "manager": ["employee_handbook.md", "hr_faq.md", "onboarding_guide.md"],
    # add custom roles as needed
}

def filter_hits_by_role(hits, role):
    """
    hits: list of dicts with keys: source, text, distance
    role: string
    returns filtered hits that match allowed sources for the role
    """
    allowed = ROLE_RULES.get(role, ROLE_RULES["employee"])
    return [h for h in hits if h.get("source") in allowed]