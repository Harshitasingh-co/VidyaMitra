from openai import OpenAI
from app.models.resume import ResumeAnalysis, SkillGap
import os
import json

class ResumeService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def extract_text(self, content: bytes, filename: str) -> str:
        """Extract text from uploaded file"""
        # Simple text extraction - can be enhanced with PyPDF2, python-docx
        return content.decode('utf-8', errors='ignore')
    
    async def analyze_resume(self, resume_content: str) -> ResumeAnalysis:
        """Analyze resume using GPT-4 and identify skill gaps"""
        prompt = f"""
        Analyze the following resume and provide:
        1. A brief summary
        2. Key strengths (list 3-5)
        3. Skill gaps with importance level and recommendations
        4. Recommended courses to improve employability
        5. Overall score (0-100)
        
        Resume:
        {resume_content}
        
        Return response as JSON with keys: summary, strengths, skill_gaps, recommended_courses, overall_score
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert career counselor and resume analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        result = json.loads(response.choices[0].message.content)
        
        return ResumeAnalysis(
            summary=result.get("summary", ""),
            strengths=result.get("strengths", []),
            skill_gaps=[SkillGap(**gap) for gap in result.get("skill_gaps", [])],
            recommended_courses=result.get("recommended_courses", []),
            overall_score=result.get("overall_score", 0.0)
        )
