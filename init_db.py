#!/usr/bin/env python3
"""
Database initialization script for Intrabot-AI
This script ensures the ChromaDB is properly set up with sample data.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_and_create_data():
    """Ensure sample data files exist"""
    data_dir = project_root / "offline-org-chatbot" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if data files exist, create samples if they don't
    sample_files = {
        "hr_faq.md": """# HR FAQ

## Leave Policies
- **Sick Leave**: 12 days per year
- **Vacation Leave**: 21 days per year  
- **Maternity/Paternity Leave**: As per company policy

## How to Apply for Leave
1. Log into HR portal at hr.company.com
2. Navigate to 'Leave' section
3. Click 'New Request'
4. Fill in required details (dates, type of leave, reason)
5. Submit the request
6. Wait for manager approval

## Salary Information
- Salary is paid on the 1st of each month
- Salary slips are available on the HR portal
- For salary queries, contact hr@company.com

## Benefits
- Health insurance coverage for employee and family
- Provident fund contribution
- Annual performance bonus
""",
        
        "employee_handbook.md": """# Employee Handbook

## Work Hours
- Standard work hours: 9:00 AM - 6:00 PM
- Lunch break: 1:00 PM - 2:00 PM
- Flexible working hours available with manager approval

## Dress Code
- Business casual is the standard
- Formal attire for client meetings
- Casual Fridays allowed

## Communication Guidelines
- Use company email for official communication
- Slack for internal team communication
- WhatsApp only for urgent matters

## Performance Reviews
- Conducted quarterly
- Annual appraisal in March
- 360-degree feedback process

## Code of Conduct
- Maintain professional behavior
- Respect diversity and inclusion
- No harassment policy strictly enforced
""",
        
        "onboarding_guide.md": """# New Employee Onboarding Guide

## First Day Checklist
- Collect laptop and access card from IT
- Complete HR documentation
- Set up email and system accounts
- Meet your team and manager
- Attend orientation session

## IT Setup Requirements
- Install required software from IT portal
- Set up VPN access for remote work
- Configure email on mobile device
- Complete security training

## Important Contacts
- **IT Support**: it@company.com, ext: 101
- **HR Department**: hr@company.com, ext: 102  
- **Facilities**: facilities@company.com, ext: 103
- **Reception**: reception@company.com, ext: 100

## Training Schedule
- Week 1: Company overview and culture
- Week 2: Department-specific training
- Week 3: Project assignment and mentoring
- Week 4: Performance goal setting
"""
    }
    
    for filename, content in sample_files.items():
        file_path = data_dir / filename
        if not file_path.exists():
            file_path.write_text(content, encoding='utf-8')
            print(f"Created sample data file: {filename}")
        else:
            print(f"Data file already exists: {filename}")

def run_data_ingestion():
    """Run the data ingestion script"""
    try:
        # Try the src version first (more advanced)
        from src.ingest import main as ingest_main
        print("Running advanced data ingestion (src/ingest.py)...")
        ingest_main()
    except Exception as e:
        print(f"Advanced ingestion failed: {e}")
        try:
            # Fallback to offline-org-chatbot version
            sys.path.insert(0, str(project_root / "offline-org-chatbot" / "src"))
            from ingest import main as ingest_main
            print("Running basic data ingestion (offline-org-chatbot/src/ingest.py)...")
            ingest_main()
        except Exception as e2:
            print(f"Basic ingestion also failed: {e2}")
            return False
    return True

def main():
    print("🤖 Initializing Intrabot-AI Database...")
    print(f"Project root: {project_root}")
    
    # Step 1: Ensure data files exist
    print("\n📁 Step 1: Checking data files...")
    check_and_create_data()
    
    # Step 2: Run data ingestion
    print("\n📚 Step 2: Ingesting data into ChromaDB...")
    success = run_data_ingestion()
    
    if success:
        print("\n✅ Database initialization completed successfully!")
        print("\nYou can now start the server with:")
        print("  ./start.sh")
        print("  or")
        print("  npm start")
    else:
        print("\n❌ Database initialization failed!")
        print("Please check the error messages above and try running manually:")
        print("  python src/ingest.py")

if __name__ == "__main__":
    main()
