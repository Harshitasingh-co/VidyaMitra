from ai.llm import get_llm_service
from ai.prompts import (
    INTERVIEW_GENERATION_SYSTEM,
    INTERVIEW_GENERATION_PROMPT,
    INTERVIEW_EVALUATION_SYSTEM,
    INTERVIEW_EVALUATION_PROMPT
)
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class InterviewAI:
    """AI service for mock interview generation and evaluation"""
    
    def __init__(self):
        self.llm = get_llm_service()
        self.conversation_memory = {}  # Store conversation context by session_id
    
    async def generate_questions(
        self,
        role: str,
        experience_level: str,
        industry: str = "Technology",
        num_questions: int = 5
    ) -> List[Dict]:
        """
        Generate interview questions based on role and experience
        
        Args:
            role: Target job role
            experience_level: entry/mid/senior
            industry: Industry context
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries
        """
        try:
            logger.info(f"Generating {num_questions} questions for {role} ({experience_level})")
            
            user_prompt = INTERVIEW_GENERATION_PROMPT.format(
                num_questions=num_questions,
                role=role,
                experience_level=experience_level,
                industry=industry
            )
            
            result = await self.llm.generate_json_response(
                system_prompt=INTERVIEW_GENERATION_SYSTEM,
                user_prompt=user_prompt
            )
            
            questions = result.get("questions", [])
            logger.info(f"Generated {len(questions)} interview questions")
            return questions
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            raise
    
    async def evaluate_answer(
        self,
        question: str,
        category: str,
        answer: str,
        expected_topics: List[str] = None
    ) -> dict:
        """
        Evaluate candidate's interview answer
        
        Args:
            question: The interview question
            category: Question category (technical/behavioral/situational)
            answer: Candidate's answer
            expected_topics: Topics that should be covered
            
        Returns:
            Evaluation results with scores and feedback
        """
        try:
            logger.info(f"Evaluating answer for category: {category}")
            
            user_prompt = INTERVIEW_EVALUATION_PROMPT.format(
                question=question,
                category=category,
                answer=answer
            )
            
            result = await self.llm.generate_json_response(
                system_prompt=INTERVIEW_EVALUATION_SYSTEM,
                user_prompt=user_prompt
            )
            
            logger.info(f"Answer evaluated. Score: {result.get('overall_score', 'N/A')}")
            return result
            
        except Exception as e:
            logger.error(f"Answer evaluation failed: {e}")
            raise
    
    async def generate_followup_question(
        self,
        original_question: str,
        candidate_answer: str
    ) -> str:
        """
        Generate a follow-up question based on candidate's answer
        
        Args:
            original_question: The original question asked
            candidate_answer: Candidate's response
            
        Returns:
            Follow-up question
        """
        try:
            system_prompt = "You are an expert interviewer. Generate insightful follow-up questions."
            user_prompt = f"""Based on this interview exchange, generate a relevant follow-up question:

Question: {original_question}
Answer: {candidate_answer}

Generate a follow-up question that:
1. Probes deeper into their answer
2. Tests their understanding
3. Is natural and conversational

Return only the follow-up question, no additional text."""
            
            followup = await self.llm.generate_text_response(system_prompt, user_prompt)
            return followup
            
        except Exception as e:
            logger.error(f"Follow-up generation failed: {e}")
            return "Can you elaborate more on that?"
    
    async def generate_overall_feedback(
        self,
        evaluations: List[dict],
        role: str
    ) -> dict:
        """
        Generate overall interview performance feedback
        
        Args:
            evaluations: List of individual answer evaluations
            role: Target role
            
        Returns:
            Overall feedback summary
        """
        try:
            # Calculate averages
            avg_score = sum(e.get("overall_score", 0) for e in evaluations) / len(evaluations)
            avg_clarity = sum(e.get("clarity_score", 0) for e in evaluations) / len(evaluations)
            avg_technical = sum(e.get("technical_accuracy", 0) for e in evaluations) / len(evaluations)
            
            system_prompt = "You are an interview coach. Provide comprehensive interview feedback. Return valid JSON only."
            user_prompt = f"""Provide overall interview feedback for a {role} candidate:

Average Overall Score: {avg_score:.1f}/100
Average Clarity: {avg_clarity:.1f}/100
Average Technical Accuracy: {avg_technical:.1f}/100

Number of Questions: {len(evaluations)}

Return in this JSON format:
{{
    "overall_performance": "<excellent/good/average/needs_improvement>",
    "key_strengths": ["<strength 1>", "<strength 2>"],
    "key_weaknesses": ["<weakness 1>", "<weakness 2>"],
    "improvement_plan": ["<action 1>", "<action 2>"],
    "readiness_level": "<ready/needs_practice/needs_significant_improvement>",
    "final_advice": "<2-3 sentence advice>"
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            result["average_scores"] = {
                "overall": round(avg_score, 1),
                "clarity": round(avg_clarity, 1),
                "technical": round(avg_technical, 1)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Overall feedback generation failed: {e}")
            raise

def get_interview_ai() -> InterviewAI:
    """Get InterviewAI instance"""
    return InterviewAI()
