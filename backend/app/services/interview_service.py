from openai import OpenAI
from app.models.interview import InterviewRequest, InterviewQuestion, InterviewResponse, InterviewFeedback
import os
import json
from typing import List

class InterviewService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def generate_questions(self, request: InterviewRequest) -> List[InterviewQuestion]:
        """Generate realistic interview questions based on role and experience"""
        prompt = f"""
        Generate 5 realistic interview questions for:
        - Role: {request.role}
        - Experience Level: {request.experience_level}
        - Industry: {request.industry or 'General'}
        
        Include a mix of technical, behavioral, and situational questions.
        Return as JSON array with keys: question, category
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert HR interviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        
        questions_data = json.loads(response.choices[0].message.content)
        return [InterviewQuestion(**q) for q in questions_data]
    
    async def evaluate_response(self, response: InterviewResponse) -> InterviewFeedback:
        """Evaluate interview response for tone, confidence, and accuracy"""
        prompt = f"""
        Evaluate this interview response:
        Question ID: {response.question_id}
        Answer: {response.answer}
        
        Provide:
        1. Overall score (0-100)
        2. Tone analysis (professional, casual, nervous, etc.)
        3. Confidence level (low, medium, high)
        4. Content accuracy score (0-100)
        5. Strengths (list 2-3)
        6. Areas for improvement (list 2-3)
        7. Detailed feedback paragraph
        
        Return as JSON with keys: overall_score, tone_analysis, confidence_level, 
        content_accuracy, strengths, improvements, detailed_feedback
        """
        
        result = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert interview coach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        feedback_data = json.loads(result.choices[0].message.content)
        return InterviewFeedback(**feedback_data)
