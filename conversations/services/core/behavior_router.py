# conversations/services/core/behavior_router.py
 
ROLE_STRATEGY_MAP = {
    # 🔵 Healthcare Support Roles
    "Patient Support Agent": "support",
    "Appointment Scheduler": "transaction",

    #Real Estate
    "Loan Eligibility Assistant": "loan_financial",
    "Site Visit Scheduler": "transaction",
    "Property Inquiry Agent": "smart_real_estate",

    #Education
    "Admission Counselor": "information",
    "Course Advisor": "education_qualification",
    "Scholarship Advisor": "education_scholarship",
    "Student Help Desk": "education_support",

    # Qualification Roles
    "Sales Executive": "sales",
    "Lead Qualifier": "lead_qualification",
    "Product Demo Agent": "product_demo",
    #Recruitment Industry

    "HR Recruiter": "recruitment_advisory",
    "Onboarding Assistant": "onboarding_support",
    "HR Helpdesk": "hr_helpdesk",
    

    #hospitality
    "Hotel Room Booking Agent": "hotel_booking",
    "Restaurant Table Booking Agent": "restaurant_booking",
    "Travel Agent & Trip Planner": "travel_planner",


    # 🔵 Customer Service Industry
    "Customer Support Executive": "customer_support",
    "Complaint Handler": "complaint_handler",
    "Returns & Refund Agent": "returns_refund",
    "Escalation Manager": "escalation_manager",

    # BFSI
    "Insurance Advisor": "insurance_transaction",
    "Mutual Funds Advisor": "mutual_fund_advisor",
    "Investment Advisor": "investment_advisor",
    # Default → Information
}
 
 
def get_role_strategy(role_name: str):
    return ROLE_STRATEGY_MAP.get(role_name, "information")