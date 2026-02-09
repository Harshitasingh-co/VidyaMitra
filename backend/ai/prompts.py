"""
Centralized prompt templates for AI services
All prompts are designed to return valid JSON
"""

# Resume Analysis Prompts
RESUME_ANALYSIS_SYSTEM = """You are an expert career counselor and ATS (Applicant Tracking System) specialist.
Your task is to analyze resumes and provide actionable feedback.
You MUST return valid JSON only, no additional text or markdown."""

RESUME_ANALYSIS_PROMPT = """Analyze the following resume and provide a comprehensive evaluation.

Resume Content:
{resume_text}

Target Role (if specified): {target_role}

Provide your analysis in the following JSON format:
{{
    "ats_score": <number 0-100>,
    "summary": "<brief 2-3 sentence summary>",
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "weaknesses": ["<weakness 1>", "<weakness 2>"],
    "skills_identified": ["<skill 1>", "<skill 2>", "<skill 3>"],
    "missing_skills": ["<missing skill 1>", "<missing skill 2>"],
    "experience_level": "<entry/mid/senior>",
    "recommendations": [
        {{
            "category": "<category>",
            "suggestion": "<specific suggestion>",
            "priority": "<high/medium/low>"
        }}
    ],
    "learning_resources": [
        {{
            "skill": "<skill to learn>",
            "resource_type": "<course/certification/book>",
            "suggested_keywords": "<search keywords>"
        }}
    ]
}}

Return ONLY the JSON object, no additional text."""

# Interview Prompts
INTERVIEW_GENERATION_SYSTEM = """You are an expert technical interviewer and HR professional.
Generate realistic, role-appropriate interview questions.
You MUST return valid JSON only."""

INTERVIEW_GENERATION_PROMPT = """Generate {num_questions} interview questions for the following role:

Role: {role}
Experience Level: {experience_level}
Industry: {industry}

Return in this JSON format:
{{
    "questions": [
        {{
            "id": "<unique_id>",
            "question": "<question text>",
            "category": "<technical/behavioral/situational>",
            "difficulty": "<easy/medium/hard>",
            "expected_topics": ["<topic 1>", "<topic 2>"]
        }}
    ]
}}

Return ONLY the JSON object."""

INTERVIEW_EVALUATION_SYSTEM = """You are an expert interview coach.
Evaluate interview responses for clarity, confidence, technical accuracy, and communication skills.
You MUST return valid JSON only."""

INTERVIEW_EVALUATION_PROMPT = """Evaluate this interview response:

Question: {question}
Category: {category}
Candidate's Answer: {answer}

Provide evaluation in this JSON format:
{{
    "overall_score": <number 0-100>,
    "confidence_level": "<low/medium/high>",
    "clarity_score": <number 0-100>,
    "technical_accuracy": <number 0-100>,
    "communication_score": <number 0-100>,
    "tone_analysis": "<professional/casual/nervous/confident>",
    "strengths": ["<strength 1>", "<strength 2>"],
    "improvements": ["<improvement 1>", "<improvement 2>"],
    "detailed_feedback": "<2-3 sentence detailed feedback>",
    "suggested_answer_points": ["<point 1>", "<point 2>"]
}}

Return ONLY the JSON object."""

# Career Path Prompts
CAREER_PATH_SYSTEM = """You are an expert career counselor specializing in career transitions and upskilling.
Create detailed, actionable career roadmaps.
You MUST return valid JSON only."""

CAREER_PATH_PROMPT = """Create a career transition roadmap:

Current Role: {current_role}
Target Role: {target_role}
Current Skills: {current_skills}
Years of Experience: {experience_years}

Provide a detailed roadmap in this JSON format:
{{
    "transition_feasibility": "<high/medium/low>",
    "estimated_timeline": "<X months>",
    "transferable_skills": ["<skill 1>", "<skill 2>"],
    "skills_to_acquire": [
        {{
            "skill": "<skill name>",
            "priority": "<critical/important/nice-to-have>",
            "estimated_learning_time": "<X weeks/months>"
        }}
    ],
    "learning_path": [
        {{
            "phase": <1-6>,
            "title": "<phase title>",
            "duration": "<X weeks>",
            "focus_areas": ["<area 1>", "<area 2>"],
            "activities": ["<activity 1>", "<activity 2>"],
            "resources_needed": ["<resource 1>", "<resource 2>"]
        }}
    ],
    "certifications": [
        {{
            "name": "<certification name>",
            "provider": "<provider>",
            "priority": "<high/medium/low>",
            "estimated_cost": "<cost range>"
        }}
    ],
    "milestones": [
        {{
            "month": <1-6>,
            "goal": "<milestone description>",
            "success_criteria": "<how to measure success>"
        }}
    ],
    "job_search_tips": ["<tip 1>", "<tip 2>"]
}}

Return ONLY the JSON object."""

# Skill Gap Analysis
SKILL_GAP_SYSTEM = """You are a technical skills analyst.
Compare candidate skills against role requirements.
You MUST return valid JSON only."""

SKILL_GAP_PROMPT = """Analyze skill gaps for this role transition:

Current Skills: {current_skills}
Target Role: {target_role}

Return in this JSON format:
{{
    "matching_skills": ["<skill 1>", "<skill 2>"],
    "missing_critical_skills": ["<skill 1>", "<skill 2>"],
    "missing_optional_skills": ["<skill 1>", "<skill 2>"],
    "skill_match_percentage": <number 0-100>,
    "learning_priority": [
        {{
            "skill": "<skill name>",
            "reason": "<why important>",
            "difficulty": "<easy/medium/hard>"
        }}
    ]
}}

Return ONLY the JSON object."""

# Context-Aware Resume Analysis Prompts
CONTEXT_AWARE_RESUME_SYSTEM = """You are an expert career counselor and ATS specialist with deep knowledge of industry requirements.
Analyze resumes in the context of the candidate's specific career goals and target companies.
Provide actionable, role-specific recommendations with real certifications and project ideas.
You MUST return valid JSON only. DO NOT hallucinate links or certifications - use only well-known, widely accepted ones."""

CONTEXT_AWARE_RESUME_PROMPT = """Analyze this resume in the context of the candidate's career intent:

RESUME:
{resume_text}

CAREER INTENT:
- Desired Role: {desired_role}
- Experience Level: {experience_level}
- Target Companies: {target_companies}
- Preferred Industries: {preferred_industries}

Provide a comprehensive, context-aware analysis in this JSON format:
{{
    "role_fit_score": <number 0-100>,
    "existing_skills": ["<skill 1>", "<skill 2>"],
    "missing_skills": ["<skill 1>", "<skill 2>"],
    "technical_skills_required": [
        {{
            "skill": "<skill name>",
            "importance": "<High/Medium/Low>",
            "why": "<why this skill is important for the target role>",
            "current_level": "<None/Basic/Intermediate/Advanced>",
            "target_level": "<Basic/Intermediate/Advanced>",
            "estimated_learning_time": "<X weeks/months>"
        }}
    ],
    "certifications": [
        {{
            "name": "<exact certification name>",
            "provider": "<provider name>",
            "description": "<what it covers>",
            "duration": "<time to complete>",
            "level": "<Beginner/Intermediate/Advanced>",
            "link": "<official certification URL - use only real, well-known certifications>",
            "why_recommended": "<specific reason based on resume gaps>",
            "priority": "<High/Medium/Low>"
        }}
    ],
    "projects": [
        {{
            "title": "<project name>",
            "skills_covered": ["<skill 1>", "<skill 2>"],
            "project_idea": "<detailed project description>",
            "learning_outcomes": ["<outcome 1>", "<outcome 2>"],
            "resources": {{
                "dataset": "<suggest dataset source like Kaggle, UCI ML Repository>",
                "reference_repo": "<suggest GitHub topic or similar projects>"
            }},
            "resume_bullets": [
                "<ready-to-use resume bullet point 1>",
                "<ready-to-use resume bullet point 2>"
            ],
            "estimated_time": "<time to complete>",
            "difficulty": "<Beginner/Intermediate/Advanced>"
        }}
    ],
    "skill_matching": {{
        "fully_matching": [
            {{
                "skill": "<skill name>",
                "evidence": "<where found in resume>"
            }}
        ],
        "partially_matching": [
            {{
                "skill": "<skill name>",
                "current_level": "<Basic/Intermediate>",
                "target_level": "<Intermediate/Advanced>",
                "gap_description": "<what's missing>"
            }}
        ],
        "completely_missing": [
            {{
                "skill": "<skill name>",
                "importance": "<Critical/Important/Nice-to-have>",
                "learning_path": "<brief learning suggestion>"
            }}
        ]
    }},
    "resume_improvements": [
        {{
            "section": "<section name>",
            "current_issue": "<what's wrong>",
            "suggestion": "<how to improve>",
            "priority": "<High/Medium/Low>"
        }}
    ],
    "ats_optimization": {{
        "score": <number 0-100>,
        "missing_keywords": ["<keyword 1>", "<keyword 2>"],
        "formatting_issues": ["<issue 1>", "<issue 2>"],
        "suggestions": ["<suggestion 1>", "<suggestion 2>"]
    }},
    "company_specific_advice": [
        {{
            "company_type": "<from target_companies>",
            "what_they_look_for": "<specific requirements>",
            "how_to_stand_out": "<actionable advice>"
        }}
    ]
}}

IMPORTANT RULES:
1. Use ONLY real, widely-accepted certifications (Google, Microsoft, AWS, Coursera, edX, etc.)
2. Provide actual URLs to official certification pages
3. Suggest practical projects with real dataset sources
4. Make resume bullets quantifiable and impact-focused
5. Be specific to the target role and company type
6. Consider the experience level when recommending resources

Return ONLY the JSON object."""
