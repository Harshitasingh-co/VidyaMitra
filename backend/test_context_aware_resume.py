"""
Test script for Context-Aware Resume Analysis feature
Run this after starting the server to verify all endpoints work correctly
"""

import requests
import json

BASE_URL = "http://localhost:8001/api/ai"

def test_career_intent():
    """Test Step 1: Submit career intent"""
    print("\n" + "="*60)
    print("TEST 1: Submit Career Intent")
    print("="*60)
    
    intent_data = {
        "desired_role": "Data Analyst",
        "experience_level": "0-2 years",
        "target_companies": ["Product-based companies", "Startups"],
        "preferred_industries": ["Tech", "E-commerce"],
        "location_preference": "Remote"
    }
    
    response = requests.post(f"{BASE_URL}/career-intent", json=intent_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success: {data.get('message', 'Intent captured')}")
        intent_id = data.get('intent_id')
        print(f"Intent ID: {intent_id}")
        return intent_id
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_get_intent(intent_id):
    """Test Step 2: Retrieve career intent"""
    print("\n" + "="*60)
    print("TEST 2: Retrieve Career Intent")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/career-intent/{intent_id}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        # Handle both wrapped and unwrapped responses
        data = result.get('data', result)
        print(f"✅ Retrieved intent for role: {data.get('desired_role', 'N/A')}")
        print(f"Experience Level: {data.get('experience_level', 'N/A')}")
        print(f"Target Companies: {', '.join(data.get('target_companies', []))}")
    else:
        print(f"❌ Failed: {response.text}")

def test_context_aware_analysis(intent_id):
    """Test Step 3: Context-aware resume analysis"""
    print("\n" + "="*60)
    print("TEST 3: Context-Aware Resume Analysis")
    print("="*60)
    
    # Sample resume text
    resume_text = """
    John Doe
    Email: john.doe@email.com | Phone: (555) 123-4567
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology, 2023
    
    EXPERIENCE
    Data Intern | Tech Startup Inc. | Jan 2023 - Present
    - Analyzed customer data using SQL queries
    - Created Excel reports for management
    - Assisted in data cleaning and preparation
    
    SKILLS
    - SQL (MySQL, PostgreSQL)
    - Microsoft Excel (Pivot Tables, VLOOKUP)
    - Basic Python
    - Communication and Teamwork
    
    PROJECTS
    - Sales Analysis Dashboard: Created Excel dashboard analyzing 1000+ sales records
    - Customer Segmentation: Used SQL to segment customers by purchase behavior
    """
    
    analysis_request = {
        "resume_text": resume_text,
        "intent_id": intent_id
    }
    
    response = requests.post(f"{BASE_URL}/context-aware-analyze", json=analysis_request)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        # Handle both wrapped and unwrapped responses
        analysis = result.get('data', result)
        
        print(f"\n✅ Analysis Complete!")
        print(f"\n📊 ROLE FIT SCORE: {analysis.get('role_fit_score', 'N/A')}%")
        
        print(f"\n✅ EXISTING SKILLS ({len(analysis.get('existing_skills', []))}):")
        for skill in analysis.get('existing_skills', [])[:5]:
            print(f"  - {skill}")
        
        print(f"\n❌ MISSING SKILLS ({len(analysis.get('missing_skills', []))}):")
        for skill in analysis.get('missing_skills', [])[:5]:
            print(f"  - {skill}")
        
        print(f"\n🎯 TECHNICAL SKILLS REQUIRED ({len(analysis.get('technical_skills_required', []))}):")
        for skill_obj in analysis.get('technical_skills_required', [])[:3]:
            print(f"  - {skill_obj.get('skill')}: {skill_obj.get('importance')} importance")
            print(f"    Why: {skill_obj.get('why')}")
        
        print(f"\n🎓 CERTIFICATIONS ({len(analysis.get('certifications', []))}):")
        for cert in analysis.get('certifications', [])[:3]:
            print(f"  - {cert.get('name')}")
            print(f"    Provider: {cert.get('provider')}")
            print(f"    Link: {cert.get('link')}")
            print(f"    Priority: {cert.get('priority')}")
        
        print(f"\n💡 PROJECT IDEAS ({len(analysis.get('projects', []))}):")
        for project in analysis.get('projects', [])[:2]:
            print(f"  - {project.get('title')}")
            print(f"    Skills: {', '.join(project.get('skills_covered', []))}")
            print(f"    Time: {project.get('estimated_time')}")
            if project.get('resume_bullets'):
                print(f"    Resume Bullet: {project['resume_bullets'][0]}")
        
        print(f"\n📈 ATS OPTIMIZATION:")
        ats = analysis.get('ats_optimization', {})
        print(f"  Score: {ats.get('score', 'N/A')}%")
        print(f"  Missing Keywords: {', '.join(ats.get('missing_keywords', [])[:5])}")
        
        print(f"\n🏢 COMPANY-SPECIFIC ADVICE:")
        for advice in analysis.get('company_specific_advice', [])[:2]:
            print(f"  {advice.get('company_type')}:")
            print(f"    - {advice.get('how_to_stand_out')}")
        
        # Save full response to file
        with open('context_aware_analysis_result.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\n💾 Full analysis saved to: context_aware_analysis_result.json")
        
    else:
        print(f"❌ Failed: {response.text}")

def test_skill_gap_details():
    """Test Step 4: Detailed skill gap analysis"""
    print("\n" + "="*60)
    print("TEST 4: Detailed Skill Gap Analysis")
    print("="*60)
    
    gap_request = {
        "existing_skills": ["SQL", "Excel", "Basic Python"],
        "required_skills": ["Python", "Power BI", "Statistics", "Tableau"],
        "desired_role": "Data Analyst"
    }
    
    response = requests.post(f"{BASE_URL}/skill-gap-details", json=gap_request)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        # Handle both wrapped and unwrapped responses
        gap_analysis = result.get('data', result)
        
        print(f"\n✅ Gap Analysis Complete!")
        print(f"\nSummary: {gap_analysis.get('gap_summary', 'N/A')}")
        
        print(f"\n🚨 CRITICAL GAPS:")
        for gap in gap_analysis.get('critical_gaps', [])[:3]:
            print(f"  - {gap.get('skill')}")
            print(f"    Why: {gap.get('why_critical')}")
            print(f"    Time: {gap.get('estimated_time')}")
        
        print(f"\n📚 LEARNING ROADMAP:")
        for week in gap_analysis.get('learning_roadmap', [])[:4]:
            print(f"  Week {week.get('week')}: {week.get('focus')}")
    else:
        print(f"❌ Failed: {response.text}")

def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "="*60)
    print("CONTEXT-AWARE RESUME ANALYSIS - TEST SUITE")
    print("="*60)
    print("Testing endpoints at:", BASE_URL)
    
    try:
        # Test 1: Submit career intent
        intent_id = test_career_intent()
        
        if not intent_id:
            print("\n❌ Cannot proceed without intent_id")
            return
        
        # Test 2: Retrieve intent
        test_get_intent(intent_id)
        
        # Test 3: Context-aware analysis
        test_context_aware_analysis(intent_id)
        
        # Test 4: Skill gap details
        test_skill_gap_details()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print("Make sure the backend server is running on http://localhost:8001")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
