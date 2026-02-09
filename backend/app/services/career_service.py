from openai import OpenAI
from app.models.career import CareerPathRequest, CareerPathRecommendation, LearningStep
import os
import json

class CareerService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_career_path(self, request: CareerPathRequest) -> CareerPathRecommendation:
        """Generate personalized career path and upskilling plan"""
        prompt = f"""
        Create a career transition plan:
        - Current Role: {request.current_role}
        - Target Role: {request.target_role}
        - Current Skills: {', '.join(request.skills)}
        - Experience: {request.experience_years} years
        
        Provide:
        1. Transferable skills from current role
        2. Skills to acquire for target role
        3. Step-by-step learning path with duration and resources
        4. Recommended certifications
        5. Estimated timeline for transition
        
        Return as JSON with keys: target_role, transferable_skills, skills_to_acquire,
        learning_path (array with title, description, duration, resources), 
        certifications, estimated_timeline
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert career counselor specializing in career transitions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        result['learning_path'] = [LearningStep(**step) for step in result.get('learning_path', [])]
        
        return CareerPathRecommendation(**result)
    
    async def get_role_skills(self, role: str) -> dict:
        """Get required skills for a specific role"""
        prompt = f"List the top 10 essential skills for a {role}. Return as JSON array."
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a career expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        return {"skills": json.loads(response.choices[0].message.content)}
