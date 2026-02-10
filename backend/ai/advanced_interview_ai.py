from ai.llm import get_llm_service
from app.models.advanced_interview import (
    PreInterviewContext, InterviewConfig, CheatingFlags
)
from typing import Dict, List, Optional
import logging
import json

logger = logging.getLogger(__name__)

class AdvancedInterviewAI:
    """Advanced AI service for adaptive mock interviews"""
    
    def __init__(self):
        self.llm = get_llm_service()
    
    def generate_interview_config(
        self,
        context: PreInterviewContext
    ) -> InterviewConfig:
        """
        Generate dynamic interview configuration based on user context
        
        Args:
            context: User's pre-interview context
            
        Returns:
            Customized interview configuration
        """
        try:
            logger.info(f"Generating interview config for {context.desired_role} ({context.experience_level})")
            
            # Default weights based on experience level
            if context.experience_level in ["0-2 years", "entry"]:
                technical_weight = 35.0
                aptitude_weight = 35.0
                soft_skills_weight = 30.0
                difficulty = "easy"
            elif context.experience_level in ["3-5 years", "mid"]:
                technical_weight = 45.0
                aptitude_weight = 25.0
                soft_skills_weight = 30.0
                difficulty = "medium"
            else:  # senior
                technical_weight = 50.0
                aptitude_weight = 20.0
                soft_skills_weight = 30.0
                difficulty = "hard"
            
            # Determine skills to test
            skills_to_test = []
            
            # Prioritize missing skills
            if context.missing_skills:
                skills_to_test.extend(context.missing_skills[:5])
            
            # Add some existing skills for validation
            if context.existing_skills:
                skills_to_test.extend(context.existing_skills[:3])
            
            # If no skills data, use role-based defaults
            if not skills_to_test:
                skills_to_test = self._get_default_skills_for_role(context.desired_role)
            
            config = InterviewConfig(
                technical_weight=technical_weight,
                aptitude_weight=aptitude_weight,
                soft_skills_weight=soft_skills_weight,
                difficulty_level=difficulty,
                skills_to_test=skills_to_test,
                total_questions=10
            )
            
            logger.info(f"Generated config: Tech={technical_weight}%, Apt={aptitude_weight}%, Soft={soft_skills_weight}%")
            return config
            
        except Exception as e:
            logger.error(f"Config generation failed: {e}")
            # Return default config
            return InterviewConfig()
    
    def _get_default_skills_for_role(self, role: str) -> List[str]:
        """Get default skills to test based on role"""
        role_lower = role.lower()
        
        if "data" in role_lower and "analyst" in role_lower:
            return ["SQL", "Python", "Data Visualization", "Statistics", "Excel"]
        elif "software" in role_lower or "developer" in role_lower:
            return ["Programming", "Data Structures", "Algorithms", "System Design", "Debugging"]
        elif "product" in role_lower:
            return ["Product Strategy", "User Research", "Prioritization", "Metrics", "Communication"]
        else:
            return ["Problem Solving", "Communication", "Analytical Thinking", "Teamwork"]

    async def generate_technical_question(
        self,
        skill: str,
        difficulty: str,
        question_number: int,
        context: Optional[PreInterviewContext] = None
    ) -> Dict:
        """
        Generate technical/coding question
        
        Args:
            skill: Skill to test
            difficulty: easy/medium/hard
            question_number: Question sequence number
            context: User context for personalization
            
        Returns:
            Technical question with metadata
        """
        try:
            logger.info(f"Generating technical question for {skill} ({difficulty})")
            
            system_prompt = """You are an expert technical interviewer.
Generate realistic technical/coding questions that test both understanding and implementation.
Return valid JSON only."""
            
            user_prompt = f"""Generate a technical interview question:

Skill: {skill}
Difficulty: {difficulty}
Question Number: {question_number}
{"Target Role: " + context.desired_role if context else ""}

Return in this JSON format:
{{
    "question_id": "tech_{question_number}",
    "skill": "{skill}",
    "difficulty": "{difficulty}",
    "question_text": "<clear problem statement>",
    "question_type": "<coding|system_design|debugging|concept>",
    "time_limit": <seconds>,
    "hints": ["<hint 1>", "<hint 2>"],
    "expected_approach": "<brief description of expected approach>",
    "test_cases": [
        {{"input": "<input>", "output": "<output>"}},
        {{"input": "<input>", "output": "<output>"}}
    ],
    "evaluation_criteria": [
        "Approach explanation quality",
        "Code correctness",
        "Edge case handling",
        "Time complexity",
        "Code readability"
    ]
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Technical question generation failed: {e}")
            raise
    
    async def evaluate_technical_answer(
        self,
        question: Dict,
        approach_explanation: str,
        code_solution: Optional[str],
        time_taken: int,
        cheating_indicators: Dict
    ) -> Dict:
        """
        Evaluate technical answer with focus on reasoning
        
        Args:
            question: The technical question
            approach_explanation: Candidate's approach explanation
            code_solution: Code submitted (if applicable)
            time_taken: Time taken in seconds
            cheating_indicators: Tab switches, paste attempts, etc.
            
        Returns:
            Detailed evaluation
        """
        try:
            logger.info(f"Evaluating technical answer for {question.get('question_id')}")
            
            system_prompt = """You are an expert code reviewer and technical interviewer.
Evaluate both the approach explanation and code implementation.
Focus on reasoning, not just correctness.
Return valid JSON only."""
            
            user_prompt = f"""Evaluate this technical interview answer:

QUESTION:
{question.get('question_text')}

EXPECTED APPROACH:
{question.get('expected_approach')}

CANDIDATE'S APPROACH EXPLANATION:
{approach_explanation}

CODE SOLUTION:
{code_solution if code_solution else "No code provided"}

TIME TAKEN: {time_taken} seconds (Limit: {question.get('time_limit')} seconds)

CHEATING INDICATORS:
- Tab switches: {cheating_indicators.get('tab_switches', 0)}
- Paste attempts: {cheating_indicators.get('paste_attempts', 0)}

Return in this JSON format:
{{
    "overall_score": <0-100>,
    "approach_score": <0-100>,
    "code_score": <0-100>,
    "approach_feedback": "<detailed feedback on approach explanation>",
    "code_feedback": "<detailed feedback on code>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>"],
    "edge_cases_handled": <true/false>,
    "time_complexity": "<O(n), O(log n), etc>",
    "space_complexity": "<O(1), O(n), etc>",
    "code_readability": <0-100>,
    "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"],
    "passed_test_cases": <number>,
    "total_test_cases": <number>
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            
            # Add time penalty if exceeded
            if time_taken > question.get('time_limit', 300):
                result['time_penalty'] = True
                result['overall_score'] = max(0, result['overall_score'] - 10)
            
            return result
            
        except Exception as e:
            logger.error(f"Technical evaluation failed: {e}")
            raise

    async def generate_aptitude_question(
        self,
        difficulty: str,
        question_number: int
    ) -> Dict:
        """
        Generate aptitude question from predefined bank
        
        Args:
            difficulty: easy/medium/hard
            question_number: Question sequence number
            
        Returns:
            Aptitude question
        """
        try:
            logger.info(f"Generating aptitude question ({difficulty})")
            
            system_prompt = """You are an aptitude test creator.
Generate logical reasoning, quantitative, or analytical questions.
Return valid JSON only."""
            
            user_prompt = f"""Generate an aptitude question:

Difficulty: {difficulty}
Question Number: {question_number}

Return in this JSON format:
{{
    "question_id": "apt_{question_number}",
    "difficulty": "{difficulty}",
    "category": "<logical_reasoning|quantitative|analytical|verbal>",
    "question_text": "<clear question>",
    "options": ["A) <option>", "B) <option>", "C) <option>", "D) <option>"],
    "correct_answer": "<A|B|C|D>",
    "explanation": "<why this is the correct answer>",
    "time_limit": <seconds>,
    "requires_reasoning": true
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Aptitude question generation failed: {e}")
            raise
    
    async def evaluate_aptitude_answer(
        self,
        question: Dict,
        answer: str,
        reasoning: str,
        time_taken: int
    ) -> Dict:
        """
        Evaluate aptitude answer with reasoning
        
        Args:
            question: The aptitude question
            answer: Selected answer (A/B/C/D)
            reasoning: Explanation of reasoning
            time_taken: Time taken in seconds
            
        Returns:
            Evaluation with correctness and reasoning quality
        """
        try:
            logger.info(f"Evaluating aptitude answer for {question.get('question_id')}")
            
            is_correct = answer.upper() == question.get('correct_answer', '').upper()
            
            system_prompt = """You are an aptitude test evaluator.
Evaluate both correctness and reasoning quality.
Return valid JSON only."""
            
            user_prompt = f"""Evaluate this aptitude answer:

QUESTION:
{question.get('question_text')}

OPTIONS:
{chr(10).join(question.get('options', []))}

CORRECT ANSWER: {question.get('correct_answer')}
CANDIDATE'S ANSWER: {answer}
CANDIDATE'S REASONING: {reasoning}

TIME TAKEN: {time_taken} seconds (Limit: {question.get('time_limit')} seconds)

Return in this JSON format:
{{
    "is_correct": {str(is_correct).lower()},
    "score": <0-100>,
    "reasoning_quality": <0-100>,
    "reasoning_feedback": "<feedback on reasoning>",
    "speed_rating": "<fast|optimal|slow>",
    "explanation": "{question.get('explanation', '')}",
    "improvement_tip": "<specific tip>"
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            result['is_correct'] = is_correct
            
            return result
            
        except Exception as e:
            logger.error(f"Aptitude evaluation failed: {e}")
            raise

    async def generate_soft_skills_question(
        self,
        question_number: int,
        previous_answer: Optional[str] = None,
        context: Optional[PreInterviewContext] = None
    ) -> Dict:
        """
        Generate behavioral/situational soft skills question
        
        Args:
            question_number: Question sequence number
            previous_answer: Previous answer for adaptive follow-ups
            context: User context for personalization
            
        Returns:
            Soft skills question
        """
        try:
            logger.info(f"Generating soft skills question {question_number}")
            
            system_prompt = """You are a professional HR interviewer.
Generate behavioral and situational questions using STAR method principles.
Be adaptive based on previous answers.
Return valid JSON only."""
            
            adaptive_context = ""
            if previous_answer:
                adaptive_context = f"\nPrevious Answer: {previous_answer}\nGenerate a relevant follow-up question."
            
            role_context = f"Target Role: {context.desired_role}" if context else ""
            
            user_prompt = f"""Generate a soft skills interview question:

Question Number: {question_number}
{role_context}
{adaptive_context}

Return in this JSON format:
{{
    "question_id": "soft_{question_number}",
    "question_text": "<behavioral or situational question>",
    "question_type": "<behavioral|situational|leadership|teamwork|conflict>",
    "star_method_applicable": true,
    "evaluation_focus": ["<focus 1>", "<focus 2>"],
    "time_limit": <seconds>,
    "follow_up_prompts": ["<prompt 1>", "<prompt 2>"]
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Soft skills question generation failed: {e}")
            raise
    
    async def evaluate_soft_skills_answer(
        self,
        question: Dict,
        answer: str,
        time_taken: int
    ) -> Dict:
        """
        Evaluate soft skills answer using STAR method and communication quality
        
        Args:
            question: The soft skills question
            answer: Candidate's answer
            time_taken: Time taken in seconds
            
        Returns:
            Evaluation focusing on clarity, structure, and impact
        """
        try:
            logger.info(f"Evaluating soft skills answer for {question.get('question_id')}")
            
            system_prompt = """You are an expert HR interviewer and communication coach.
Evaluate soft skills answers using STAR method (Situation, Task, Action, Result).
Assess clarity, confidence, structure, and impact.
Return valid JSON only."""
            
            user_prompt = f"""Evaluate this soft skills interview answer:

QUESTION:
{question.get('question_text')}

QUESTION TYPE: {question.get('question_type')}

CANDIDATE'S ANSWER:
{answer}

TIME TAKEN: {time_taken} seconds

Return in this JSON format:
{{
    "overall_score": <0-100>,
    "clarity_score": <0-100>,
    "structure_score": <0-100>,
    "impact_score": <0-100>,
    "confidence_level": "<low|medium|high>",
    "star_method_used": <true|false>,
    "star_breakdown": {{
        "situation": "<present|missing>",
        "task": "<present|missing>",
        "action": "<present|missing>",
        "result": "<present|missing>"
    }},
    "communication_quality": "<poor|average|good|excellent>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>"],
    "improvement_suggestions": ["<suggestion 1>", "<suggestion 2>"],
    "follow_up_needed": <true|false>,
    "suggested_follow_up": "<follow-up question if needed>"
}}

Return ONLY the JSON object."""
            
            result = await self.llm.generate_json_response(system_prompt, user_prompt)
            return result
            
        except Exception as e:
            logger.error(f"Soft skills evaluation failed: {e}")
            raise
    
    def detect_cheating(
        self,
        tab_switches: int,
        paste_attempts: int,
        time_taken: int,
        expected_time: int,
        answer_similarity: Optional[float] = None
    ) -> CheatingFlags:
        """
        Detect potential cheating based on behavioral indicators
        
        Args:
            tab_switches: Number of tab switches
            paste_attempts: Number of paste attempts
            time_taken: Actual time taken
            expected_time: Expected time for question
            answer_similarity: Similarity to known answers (0-1)
            
        Returns:
            Cheating flags with severity
        """
        try:
            flags = CheatingFlags(
                tab_switches=tab_switches,
                paste_attempts=paste_attempts
            )
            
            # Check for suspicious speed (too fast)
            if time_taken < expected_time * 0.3:
                flags.suspicious_speed = True
            
            # Check for identical answers
            if answer_similarity and answer_similarity > 0.95:
                flags.identical_answers = True
            
            # Determine severity
            severity_score = 0
            
            if tab_switches > 5:
                severity_score += 2
            elif tab_switches > 2:
                severity_score += 1
            
            if paste_attempts > 0:
                severity_score += 2
            
            if flags.suspicious_speed:
                severity_score += 1
            
            if flags.identical_answers:
                severity_score += 3
            
            if severity_score >= 5:
                flags.severity = "high"
            elif severity_score >= 3:
                flags.severity = "medium"
            elif severity_score >= 1:
                flags.severity = "low"
            else:
                flags.severity = "none"
            
            logger.info(f"Cheating detection: severity={flags.severity}, score={severity_score}")
            return flags
            
        except Exception as e:
            logger.error(f"Cheating detection failed: {e}")
            return CheatingFlags()
    
    async def generate_interview_report(
        self,
        session_data: Dict,
        technical_evaluations: List[Dict],
        aptitude_evaluations: List[Dict],
        soft_skills_evaluations: List[Dict],
        cheating_flags: CheatingFlags,
        config: InterviewConfig
    ) -> Dict:
        """
        Generate comprehensive interview report
        
        Args:
            session_data: Interview session metadata
            technical_evaluations: List of technical evaluations
            aptitude_evaluations: List of aptitude evaluations
            soft_skills_evaluations: List of soft skills evaluations
            cheating_flags: Detected cheating indicators
            config: Interview configuration used
            
        Returns:
            Comprehensive structured report
        """
        try:
            logger.info(f"Generating interview report for session {session_data.get('session_id')}")
            
            # Calculate weighted scores
            tech_avg = sum(e.get('overall_score', 0) for e in technical_evaluations) / len(technical_evaluations) if technical_evaluations else 0
            apt_avg = sum(e.get('score', 0) for e in aptitude_evaluations) / len(aptitude_evaluations) if aptitude_evaluations else 0
            soft_avg = sum(e.get('overall_score', 0) for e in soft_skills_evaluations) / len(soft_skills_evaluations) if soft_skills_evaluations else 0
            
            overall_score = (
                tech_avg * (config.technical_weight / 100) +
                apt_avg * (config.aptitude_weight / 100) +
                soft_avg * (config.soft_skills_weight / 100)
            )
            
            # Apply cheating penalty
            if cheating_flags.severity == "high":
                overall_score *= 0.5
            elif cheating_flags.severity == "medium":
                overall_score *= 0.7
            elif cheating_flags.severity == "low":
                overall_score *= 0.9
            
            # Determine readiness
            if overall_score >= 75:
                readiness = "ready"
            elif overall_score >= 50:
                readiness = "needs_practice"
            else:
                readiness = "needs_significant_improvement"
            
            # Generate detailed sections
            technical_report = self._generate_technical_report(technical_evaluations) if technical_evaluations else None
            aptitude_report = self._generate_aptitude_report(aptitude_evaluations) if aptitude_evaluations else None
            soft_skills_report = self._generate_soft_skills_report(soft_skills_evaluations) if soft_skills_evaluations else None
            
            # Generate next actions
            next_actions = self._generate_next_actions(
                technical_report,
                aptitude_report,
                soft_skills_report,
                overall_score
            )
            
            report = {
                "session_id": session_data.get('session_id'),
                "overall_score": round(overall_score, 1),
                "technical": technical_report,
                "aptitude": aptitude_report,
                "soft_skills": soft_skills_report,
                "cheating_flags": cheating_flags.dict(),
                "next_actions": next_actions,
                "interview_duration": session_data.get('duration', 0),
                "readiness_level": readiness,
                "weights_used": {
                    "technical": config.technical_weight,
                    "aptitude": config.aptitude_weight,
                    "soft_skills": config.soft_skills_weight
                }
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            raise
    
    def _generate_technical_report(self, evaluations: List[Dict]) -> Dict:
        """Generate technical section of report"""
        avg_score = sum(e.get('overall_score', 0) for e in evaluations) / len(evaluations)
        
        all_strengths = []
        all_weaknesses = []
        
        for eval in evaluations:
            all_strengths.extend(eval.get('strengths', []))
            all_weaknesses.extend(eval.get('weaknesses', []))
        
        # Get unique strengths and weaknesses
        strengths = list(set(all_strengths))[:3]
        weaknesses = list(set(all_weaknesses))[:3]
        
        # Extract priority skills from weaknesses
        priority_skills = [w.split()[0] for w in weaknesses if w][:3]
        
        return {
            "score": round(avg_score, 1),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "priority_skills": priority_skills,
            "questions_attempted": len(evaluations)
        }
    
    def _generate_aptitude_report(self, evaluations: List[Dict]) -> Dict:
        """Generate aptitude section of report"""
        avg_score = sum(e.get('score', 0) for e in evaluations) / len(evaluations)
        correct_count = sum(1 for e in evaluations if e.get('is_correct', False))
        
        analysis = f"Answered {correct_count}/{len(evaluations)} correctly. "
        
        if avg_score >= 75:
            analysis += "Strong logical reasoning and analytical skills."
        elif avg_score >= 50:
            analysis += "Good foundation, practice more complex problems."
        else:
            analysis += "Needs improvement in logical reasoning and problem-solving speed."
        
        return {
            "score": round(avg_score, 1),
            "correct_answers": correct_count,
            "total_questions": len(evaluations),
            "accuracy": round((correct_count / len(evaluations)) * 100, 1),
            "analysis": analysis
        }
    
    def _generate_soft_skills_report(self, evaluations: List[Dict]) -> Dict:
        """Generate soft skills section of report"""
        avg_score = sum(e.get('overall_score', 0) for e in evaluations) / len(evaluations)
        
        star_usage = sum(1 for e in evaluations if e.get('star_method_used', False))
        
        feedback = f"Used STAR method in {star_usage}/{len(evaluations)} answers. "
        
        if avg_score >= 75:
            feedback += "Excellent communication and structured thinking."
        elif avg_score >= 50:
            feedback += "Good communication, work on structuring answers better."
        else:
            feedback += "Needs significant improvement in communication clarity and structure."
        
        return {
            "score": round(avg_score, 1),
            "star_method_usage": f"{star_usage}/{len(evaluations)}",
            "feedback": feedback,
            "questions_answered": len(evaluations)
        }
    
    def _generate_next_actions(
        self,
        technical: Optional[Dict],
        aptitude: Optional[Dict],
        soft_skills: Optional[Dict],
        overall_score: float
    ) -> List[str]:
        """Generate personalized next actions"""
        actions = []
        
        if technical and technical['score'] < 60:
            if technical.get('priority_skills'):
                actions.append(f"Practice {', '.join(technical['priority_skills'][:2])}")
            actions.append("Solve 5 coding problems daily")
        
        if aptitude and aptitude['score'] < 60:
            actions.append("Practice aptitude questions for 30 minutes daily")
        
        if soft_skills and soft_skills['score'] < 60:
            actions.append("Practice STAR method for behavioral questions")
            actions.append("Record and review your interview answers")
        
        if overall_score < 50:
            actions.append("Attempt 2-3 more mock interviews this week")
        elif overall_score < 75:
            actions.append("Attempt 1 more mock interview before real interviews")
        
        if not actions:
            actions.append("You're interview-ready! Practice maintaining consistency")
        
        return actions[:5]  # Limit to 5 actions

def get_advanced_interview_ai() -> AdvancedInterviewAI:
    """Get AdvancedInterviewAI instance"""
    return AdvancedInterviewAI()
