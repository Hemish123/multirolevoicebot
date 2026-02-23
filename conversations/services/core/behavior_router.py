# conversations/services/core/behavior_router.py

ROLE_STRATEGY_MAP = {
    # Transaction Roles
    "Appointment Scheduler": "transaction",
    "Hotel Room Booking Agent": "transaction",
    "Restaurant Table Booking Agent": "transaction",
    "Site Visit Scheduler": "transaction",
    "Returns & Refund Agent": "transaction",
    "Loan Eligibility Assistant": "transaction",

    # Qualification Roles
    "Sales Executive": "qualification",
    "Lead Qualifier": "qualification",
    "Product Demo Agent": "qualification",
    "Property Inquiry Agent": "qualification",
    "HR Recruiter": "qualification",

    # Default → Information
}


def get_role_strategy(role_name: str):
    return ROLE_STRATEGY_MAP.get(role_name, "information")