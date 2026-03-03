# conversations/services/core/behavior_router.py
 
ROLE_STRATEGY_MAP = {
    # 🔵 Healthcare Support Roles
    "Patient Support Agent": "support",
    # Transaction Roles
    "Appointment Scheduler": "transaction",
    "Hotel Room Booking Agent": "transaction",
    "Restaurant Table Booking Agent": "transaction",
   
    "Returns & Refund Agent": "transaction",
 
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
    "Sales Executive": "information",
    "Lead Qualifier": "information",
    "Product Demo Agent": "information",
   
    "HR Recruiter": "qualification",
    

    #hospitality
    "Hotel Room Booking Agent": "hotel_booking",
    "Restaurant Table Booking Agent": "restaurant_booking",
    "Travel Agent & Trip Planner": "travel_planner",
    # Default → Information
}
 
 
def get_role_strategy(role_name: str):
    return ROLE_STRATEGY_MAP.get(role_name, "information")