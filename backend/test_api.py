"""
Test script for VidyaMitra API
Run this to verify all AI endpoints are working correctly
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.test_email = "test@vidyamitra.com"
        self.test_password = "testpassword123"
    
    def print_response(self, title: str, response: requests.Response):
        """Pretty print API response"""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        print(f"Status Code: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
    
    def test_health(self):
        """Test health endpoint"""
        response = requests.get(f"{self.base_url}/health")
        self.print_response("Health Check", response)
        return response.status_code == 200
    
    def test_register(self):
        """Test user registration"""
        data = {
            "email": self.test_email,
            "password": self.test_password,
            "full_name": "Test User"
        }
        response = requests.post(
            f"{self.base_url}/api/auth/register",
            json=data
        )
        self.print_response("User Registration", response)
        return response.status_code in [200, 400]  # 400 if user exists
    
    def test_login(self):
        """Test user login"""
        data = {
            "username": self.test_email,
            "password": self.test_password
        }
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            data=data
        )
        self.print_response("User Login", response)
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            print(f"\n✓ Token obtained: {self.token[:50]}...")
            return True
        return False
    
    def test_resume_analysis(self):
        """Test resume analysis"""
        if not self.token:
            print("❌ No token available. Login first.")
            return False
        
        sample_resume = """
        John Doe
        Software Engineer
        
        Experience:
        - 3 years as Frontend Developer at Tech Corp
        - Built React applications
        - Worked with JavaScript, HTML, CSS
        
        Skills:
        - React, JavaScript, HTML, CSS
        - Git, Agile methodologies
        
        Education:
        - BS Computer Science, 2020
        """
        
        data = {
            "resume_text": sample_resume,
            "target_role": "Full Stack Developer"
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/api/ai/resume/analyze",
            json=data,
            headers=headers
        )
        self.print_response("Resume Analysis", response)
        return response.status_code == 200
    
    def test_interview_start(self):
        """Test interview session start"""
        if not self.token:
            print("❌ No token available. Login first.")
            return False
        
        data = {
            "role": "Software Engineer",
            "experience_level": "mid",
            "industry": "Technology",
            "num_questions": 3
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/api/ai/interview/start",
            json=data,
            headers=headers
        )
        self.print_response("Interview Start", response)
        
        if response.status_code == 200:
            questions = response.json()["data"]["questions"]
            if questions:
                return questions[0]  # Return first question for evaluation test
        return None
    
    def test_interview_evaluation(self, question: dict):
        """Test answer evaluation"""
        if not self.token or not question:
            print("❌ No token or question available.")
            return False
        
        data = {
            "question": question["question"],
            "category": question["category"],
            "answer": "This is a sample answer demonstrating my understanding of the topic. I would approach this by first analyzing the requirements, then designing a solution that addresses the core problem while considering scalability and maintainability."
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/api/ai/interview/answer",
            json=data,
            headers=headers
        )
        self.print_response("Interview Answer Evaluation", response)
        return response.status_code == 200
    
    def test_career_roadmap(self):
        """Test career roadmap generation"""
        if not self.token:
            print("❌ No token available. Login first.")
            return False
        
        data = {
            "current_role": "Frontend Developer",
            "target_role": "Full Stack Developer",
            "current_skills": ["React", "JavaScript", "CSS", "HTML"],
            "experience_years": 3
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/api/ai/career/roadmap",
            json=data,
            headers=headers
        )
        self.print_response("Career Roadmap", response)
        return response.status_code == 200
    
    def test_job_matching(self):
        """Test job matching engine"""
        if not self.token:
            print("❌ No token available. Login first.")
            return False
        
        data = {
            "user_skills": ["Python", "SQL", "Excel", "Data Cleaning"],
            "experience_years": 2,
            "target_domain": "Data Science"
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/api/ai/job-match/match",
            json=data,
            headers=headers
        )
        self.print_response("Job Matching", response)
        return response.status_code == 200
    
    def test_project_generation(self):
        """Test project idea generator"""
        if not self.token:
            print("❌ No token available. Login first.")
            return False
        
        data = {
            "target_role": "Data Analyst",
            "missing_skills": ["Power BI", "Python", "Data Visualization"],
            "experience_level": "entry",
            "num_projects": 2
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/api/ai/projects/generate",
            json=data,
            headers=headers
        )
        self.print_response("Project Generation", response)
        return response.status_code == 200
    
    def run_all_tests(self):
        """Run all API tests"""
        print("\n" + "="*60)
        print("VidyaMitra API Test Suite (Extended)")
        print("="*60)
        
        results = {}
        
        # Test 1: Health Check
        print("\n[1/9] Testing Health Check...")
        results["health"] = self.test_health()
        
        # Test 2: Registration
        print("\n[2/9] Testing User Registration...")
        results["register"] = self.test_register()
        
        # Test 3: Login
        print("\n[3/9] Testing User Login...")
        results["login"] = self.test_login()
        
        if not results["login"]:
            print("\n❌ Login failed. Cannot proceed with authenticated tests.")
            return results
        
        # Test 4: Resume Analysis
        print("\n[4/9] Testing Resume Analysis...")
        results["resume"] = self.test_resume_analysis()
        
        # Test 5: Interview Start
        print("\n[5/9] Testing Interview Start...")
        question = self.test_interview_start()
        results["interview_start"] = question is not None
        
        # Test 6: Interview Evaluation
        if question:
            print("\n[6/9] Testing Interview Evaluation...")
            results["interview_eval"] = self.test_interview_evaluation(question)
        else:
            print("\n[6/9] Skipping Interview Evaluation (no question)")
            results["interview_eval"] = False
        
        # Test 7: Career Roadmap
        print("\n[7/9] Testing Career Roadmap...")
        results["career"] = self.test_career_roadmap()
        
        # Test 8: Job Matching (NEW)
        print("\n[8/9] Testing Job Matching Engine...")
        results["job_match"] = self.test_job_matching()
        
        # Test 9: Project Generation (NEW)
        print("\n[9/9] Testing Project Idea Generator...")
        results["project_gen"] = self.test_project_generation()
        
        # Summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        for test_name, passed in results.items():
            status = "✓ PASS" if passed else "❌ FAIL"
            print(f"{test_name:20s}: {status}")
        
        total = len(results)
        passed = sum(results.values())
        print(f"\nTotal: {passed}/{total} tests passed")
        
        return results

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         VidyaMitra API Test Suite                       ║
    ║                                                          ║
    ║  Make sure the backend server is running:               ║
    ║  python -m uvicorn main:app --reload                    ║
    ║                                                          ║
    ║  Required: OPENAI_API_KEY in .env file                  ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    input("Press Enter to start tests...")
    
    tester = APITester()
    results = tester.run_all_tests()
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)
