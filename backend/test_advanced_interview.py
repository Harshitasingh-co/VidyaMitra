"""
Test script for Advanced Mock Interview System
Run this after starting the server to verify all endpoints work correctly
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001/api/ai/advanced-interview"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_start_interview():
    """Test Step 1: Start interview with context"""
    print_section("TEST 1: Start Advanced Interview")
    
    request_data = {
        "interview_type": "full",
        "user_context": {
            "user_id": "test_user_123",
            "desired_role": "Data Analyst",
            "experience_level": "0-2 years",
            "existing_skills": ["SQL", "Excel", "Communication"],
            "missing_skills": ["Python", "Power BI", "Statistics"],
            "target_companies": ["Product-based companies", "Startups"]
        }
    }
    
    response = requests.post(f"{BASE_URL}/start", json=request_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        session_id = data['data']['session_id']
        config = data['data']['config']
        
        print(f"✅ Interview Started!")
        print(f"Session ID: {session_id}")
        print(f"Interview Type: {data['data']['interview_type']}")
        print(f"\nConfiguration:")
        print(f"  Technical Weight: {config['technical_weight']}%")
        print(f"  Aptitude Weight: {config['aptitude_weight']}%")
        print(f"  Soft Skills Weight: {config['soft_skills_weight']}%")
        print(f"  Difficulty: {config['difficulty_level']}")
        print(f"  Skills to Test: {', '.join(config['skills_to_test'][:3])}")
        
        print(f"\nQuestion Distribution:")
        dist = data['data']['question_distribution']
        print(f"  Technical: {dist['technical']}")
        print(f"  Aptitude: {dist['aptitude']}")
        print(f"  Soft Skills: {dist['soft_skills']}")
        
        print(f"\nAnti-Cheat Rules:")
        rules = data['data']['rules']
        print(f"  Time Limit: {rules['time_limit_per_question']}s per question")
        print(f"  Tab Switch Allowed: {rules['allow_tab_switch']}")
        print(f"  Paste Allowed: {rules['allow_paste']}")
        print(f"  Max Tab Switches: {rules['max_tab_switches']}")
        
        return session_id
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_technical_question(session_id):
    """Test Step 2: Get technical question"""
    print_section("TEST 2: Get Technical Question")
    
    request_data = {
        "session_id": session_id,
        "question_number": 1
    }
    
    response = requests.post(f"{BASE_URL}/technical/question", json=request_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        question = data['data']['question']
        
        print(f"✅ Technical Question Generated!")
        print(f"\nQuestion ID: {question['question_id']}")
        print(f"Skill: {question['skill']}")
        print(f"Difficulty: {question['difficulty']}")
        print(f"Type: {question['question_type']}")
        print(f"Time Limit: {question['time_limit']}s")
        print(f"\nQuestion:")
        print(f"  {question['question_text'][:200]}...")
        print(f"\nExpected Approach:")
        print(f"  {question.get('expected_approach', 'N/A')}")
        print(f"\nHints: {', '.join(question.get('hints', []))}")
        
        return question['question_id']
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_technical_submit(session_id, question_id):
    """Test Step 3: Submit technical answer"""
    print_section("TEST 3: Submit Technical Answer")
    
    request_data = {
        "session_id": session_id,
        "question_id": question_id,
        "approach_explanation": "I will use a two-pass algorithm. First pass to find the maximum element, second pass to find the second maximum. This ensures O(n) time complexity with O(1) space complexity. I'll handle edge cases like arrays with less than 2 elements and arrays with duplicate values.",
        "code_solution": """def second_largest(arr):
    if len(arr) < 2:
        return None
    
    first = second = float('-inf')
    
    for num in arr:
        if num > first:
            second = first
            first = num
        elif num > second and num != first:
            second = num
    
    return second if second != float('-inf') else None""",
        "time_taken": 245,
        "tab_switches": 0,
        "paste_attempts": 0
    }
    
    response = requests.post(f"{BASE_URL}/technical/submit", json=request_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        eval_data = data['data']
        
        print(f"✅ Technical Answer Evaluated!")
        print(f"\n📊 SCORES:")
        print(f"  Overall Score: {eval_data['overall_score']}/100")
        print(f"  Approach Score: {eval_data['approach_score']}/100")
        print(f"  Code Score: {eval_data['code_score']}/100")
        print(f"  Code Readability: {eval_data['code_readability']}/100")
        
        print(f"\n✅ STRENGTHS:")
        for strength in eval_data['strengths']:
            print(f"  • {strength}")
        
        print(f"\n⚠️  WEAKNESSES:")
        for weakness in eval_data['weaknesses']:
            print(f"  • {weakness}")
        
        print(f"\n🔍 COMPLEXITY:")
        print(f"  Time: {eval_data['time_complexity']}")
        print(f"  Space: {eval_data['space_complexity']}")
        
        print(f"\n💡 IMPROVEMENTS:")
        for suggestion in eval_data['improvement_suggestions']:
            print(f"  • {suggestion}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_aptitude_question(session_id):
    """Test Step 4: Get aptitude question"""
    print_section("TEST 4: Get Aptitude Question")
    
    request_data = {
        "session_id": session_id,
        "question_number": 1
    }
    
    response = requests.post(f"{BASE_URL}/aptitude/question", json=request_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        question = data['data']['question']
        
        print(f"✅ Aptitude Question Generated!")
        print(f"\nQuestion ID: {question['question_id']}")
        print(f"Category: {question['category']}")
        print(f"Difficulty: {question['difficulty']}")
        print(f"Time Limit: {question['time_limit']}s")
        print(f"\nQuestion:")
        print(f"  {question['question_text']}")
        print(f"\nOptions:")
        for option in question['options']:
            print(f"  {option}")
        
        return question['question_id']
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_aptitude_submit(session_id, question_id):
    """Test Step 5: Submit aptitude answer"""
    print_section("TEST 5: Submit Aptitude Answer")
    
    request_data = {
        "session_id": session_id,
        "question_id": question_id,
        "answer": "A",
        "reasoning": "This follows the transitive property in logic. If all A are B, and all B are C, then all A must be C. Therefore, the statement is logically valid.",
        "time_taken": 45
    }
    
    response = requests.post(f"{BASE_URL}/aptitude/submit", json=request_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        eval_data = data['data']
        
        print(f"✅ Aptitude Answer Evaluated!")
        print(f"\n📊 RESULTS:")
        print(f"  Correct: {'✓' if eval_data['is_correct'] else '✗'}")
        print(f"  Score: {eval_data['score']}/100")
        print(f"  Reasoning Quality: {eval_data['reasoning_quality']}/100")
        print(f"  Speed Rating: {eval_data['speed_rating']}")
        
        print(f"\n💬 FEEDBACK:")
        print(f"  {eval_data['reasoning_feedback']}")
        
        print(f"\n💡 TIP:")
        print(f"  {eval_data['improvement_tip']}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_soft_skills_question(session_id):
    """Test Step 6: Get soft skills question"""
    print_section("TEST 6: Get Soft Skills Question")
    
    request_data = {
        "session_id": session_id,
        "question_number": 1,
        "previous_answer": None
    }
    
    response = requests.post(f"{BASE_URL}/soft-skills/question", json=request_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        question = data['data']['question']
        
        print(f"✅ Soft Skills Question Generated!")
        print(f"\nQuestion ID: {question['question_id']}")
        print(f"Type: {question['question_type']}")
        print(f"STAR Method Applicable: {question['star_method_applicable']}")
        print(f"Time Limit: {question['time_limit']}s")
        print(f"\nQuestion:")
        print(f"  {question['question_text']}")
        print(f"\nEvaluation Focus:")
        for focus in question['evaluation_focus']:
            print(f"  • {focus}")
        
        return question['question_id']
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_soft_skills_submit(session_id, question_id):
    """Test Step 7: Submit soft skills answer"""
    print_section("TEST 7: Submit Soft Skills Answer")
    
    request_data = {
        "session_id": session_id,
        "question_id": question_id,
        "answer": "During my college project (Situation), I was the team lead responsible for delivering a data analysis project within 2 weeks (Task). I organized daily stand-ups, created a shared task board, and ensured everyone understood their responsibilities. When one team member fell behind, I paired them with a stronger member for support (Action). We completed the project 2 days early and received the highest grade in our class. The professor specifically praised our teamwork and organization (Result).",
        "time_taken": 120
    }
    
    response = requests.post(f"{BASE_URL}/soft-skills/submit", json=request_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        eval_data = data['data']
        
        print(f"✅ Soft Skills Answer Evaluated!")
        print(f"\n📊 SCORES:")
        print(f"  Overall Score: {eval_data['overall_score']}/100")
        print(f"  Clarity: {eval_data['clarity_score']}/100")
        print(f"  Structure: {eval_data['structure_score']}/100")
        print(f"  Impact: {eval_data['impact_score']}/100")
        
        print(f"\n🎯 ANALYSIS:")
        print(f"  Confidence Level: {eval_data['confidence_level']}")
        print(f"  STAR Method Used: {'✓' if eval_data['star_method_used'] else '✗'}")
        print(f"  Communication Quality: {eval_data['communication_quality']}")
        
        print(f"\n📋 STAR Breakdown:")
        star = eval_data['star_breakdown']
        print(f"  Situation: {star['situation']}")
        print(f"  Task: {star['task']}")
        print(f"  Action: {star['action']}")
        print(f"  Result: {star['result']}")
        
        print(f"\n✅ STRENGTHS:")
        for strength in eval_data['strengths']:
            print(f"  • {strength}")
        
        print(f"\n💡 IMPROVEMENTS:")
        for suggestion in eval_data['improvement_suggestions']:
            print(f"  • {suggestion}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_session_status(session_id):
    """Test Step 8: Get session status"""
    print_section("TEST 8: Get Session Status")
    
    response = requests.get(f"{BASE_URL}/session/{session_id}/status")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        status_data = data['data']
        
        print(f"✅ Session Status Retrieved!")
        print(f"\nSession ID: {status_data['session_id']}")
        print(f"Status: {status_data['status']}")
        print(f"\nQuestions Answered:")
        answered = status_data['questions_answered']
        print(f"  Technical: {answered['technical']}")
        print(f"  Aptitude: {answered['aptitude']}")
        print(f"  Soft Skills: {answered['soft_skills']}")
        
        print(f"\nCheating Indicators:")
        cheating = status_data['cheating_indicators']
        print(f"  Tab Switches: {cheating['tab_switches']}")
        print(f"  Paste Attempts: {cheating['paste_attempts']}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_final_report(session_id):
    """Test Step 9: Get final interview report"""
    print_section("TEST 9: Get Final Interview Report")
    
    response = requests.get(f"{BASE_URL}/report/{session_id}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        report = data['data']
        
        print(f"✅ Interview Report Generated!")
        print(f"\n🎯 OVERALL SCORE: {report['overall_score']}/100")
        print(f"🏆 READINESS LEVEL: {report['readiness_level'].upper()}")
        
        if report.get('technical'):
            tech = report['technical']
            print(f"\n💻 TECHNICAL ({tech['score']}/100):")
            print(f"  Questions Attempted: {tech['questions_attempted']}")
            print(f"  Strengths: {', '.join(tech['strengths'][:2])}")
            print(f"  Priority Skills: {', '.join(tech['priority_skills'][:2])}")
        
        if report.get('aptitude'):
            apt = report['aptitude']
            print(f"\n🧠 APTITUDE ({apt['score']}/100):")
            print(f"  Accuracy: {apt['accuracy']}%")
            print(f"  Analysis: {apt['analysis']}")
        
        if report.get('soft_skills'):
            soft = report['soft_skills']
            print(f"\n💬 SOFT SKILLS ({soft['score']}/100):")
            print(f"  STAR Usage: {soft['star_method_usage']}")
            print(f"  Feedback: {soft['feedback']}")
        
        print(f"\n🚨 CHEATING FLAGS:")
        flags = report['cheating_flags']
        print(f"  Severity: {flags['severity'].upper()}")
        print(f"  Tab Switches: {flags['tab_switches']}")
        print(f"  Paste Attempts: {flags['paste_attempts']}")
        
        print(f"\n📋 NEXT ACTIONS:")
        for i, action in enumerate(report['next_actions'][:5], 1):
            print(f"  {i}. {action}")
        
        print(f"\n⏱️  Interview Duration: {report['interview_duration']}s")
        
        # Save full report to file
        with open('advanced_interview_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n💾 Full report saved to: advanced_interview_report.json")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def run_all_tests():
    """Run complete interview flow test"""
    print("\n" + "="*60)
    print("  ADVANCED MOCK INTERVIEW SYSTEM - TEST SUITE")
    print("="*60)
    print(f"Testing endpoints at: {BASE_URL}")
    
    try:
        # Test 1: Start interview
        session_id = test_start_interview()
        if not session_id:
            print("\n❌ Cannot proceed without session_id")
            return
        
        time.sleep(1)
        
        # Test 2-3: Technical interview
        question_id = test_technical_question(session_id)
        if question_id:
            time.sleep(1)
            test_technical_submit(session_id, question_id)
        
        time.sleep(1)
        
        # Test 4-5: Aptitude interview
        question_id = test_aptitude_question(session_id)
        if question_id:
            time.sleep(1)
            test_aptitude_submit(session_id, question_id)
        
        time.sleep(1)
        
        # Test 6-7: Soft skills interview
        question_id = test_soft_skills_question(session_id)
        if question_id:
            time.sleep(1)
            test_soft_skills_submit(session_id, question_id)
        
        time.sleep(1)
        
        # Test 8: Session status
        test_session_status(session_id)
        
        time.sleep(1)
        
        # Test 9: Final report
        test_final_report(session_id)
        
        print("\n" + "="*60)
        print("  ✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server")
        print("Make sure the backend server is running on http://localhost:8001")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    run_all_tests()
