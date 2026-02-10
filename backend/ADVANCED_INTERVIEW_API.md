# Advanced Mock Interview System - API Documentation

## Overview

The Advanced Mock Interview System provides adaptive, skill-aware interviews with anti-cheating mechanisms and comprehensive evaluation.

## Key Features

1. **Pre-Interview Intelligence**: Analyzes user resume and skills before starting
2. **Adaptive Difficulty**: Adjusts based on experience level and performance
3. **Multiple Interview Types**: Technical, Aptitude, Soft Skills, or Full
4. **Anti-Cheating**: Tab switch detection, paste prevention, time tracking
5. **Reasoning-Focused Evaluation**: Evaluates approach, not just answers
6. **Comprehensive Reports**: Detailed feedback with next actions

## API Endpoints

### 1. Start Interview

**Endpoint**: `POST /api/ai/advanced-interview/start`

**Request Body**:
```json
{
  "interview_type": "full",  // full | technical | aptitude | soft-skills
  "user_context": {
    "user_id": "user123",
    "desired_role": "Data Analyst",
    "experience_level": "0-2 years",
    "existing_skills": ["SQL", "Excel"],
    "missing_skills": ["Python", "Power BI"],
    "target_companies": ["Product-based companies"]
  },
  "custom_config": {  // Optional
    "technical_weight": 40.0,
    "aptitude_weight": 30.0,
    "soft_skills_weight": 30.0,
    "difficulty_level": "medium",
    "total_questions": 10
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "interview_user123_abc123",
    "interview_type": "full",
    "config": {
      "technical_weight": 40.0,
      "aptitude_weight": 30.0,
      "soft_skills_weight": 30.0,
      "difficulty_level": "medium",
      "skills_to_test": ["Python", "Power BI", "SQL"],
      "total_questions": 10
    },
    "rules": {
      "time_limit_per_question": 300,
      "allow_tab_switch": false,
      "allow_paste": false,
      "max_tab_switches": 3,
      "track_time": true
    },
    "question_distribution": {
      "technical": 4,
      "aptitude": 3,
      "soft_skills": 3
    },
    "message": "Interview session created. Follow the rules strictly."
  }
}
```

---

### 2. Technical Interview

#### Get Technical Question

**Endpoint**: `POST /api/ai/advanced-interview/technical/question`

**Request**:
```json
{
  "session_id": "interview_user123_abc123",
  "question_number": 1
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "question": {
      "question_id": "tech_1",
      "skill": "Python",
      "difficulty": "medium",
      "question_text": "Write a function to find the second largest element in an array...",
      "question_type": "coding",
      "time_limit": 300,
      "hints": ["Consider edge cases", "Think about time complexity"],
      "expected_approach": "Sort or use two-pass algorithm",
      "test_cases": [
        {"input": "[1,2,3,4,5]", "output": "4"},
        {"input": "[5,5,4,3]", "output": "4"}
      ],
      "evaluation_criteria": [
        "Approach explanation quality",
        "Code correctness",
        "Edge case handling"
      ]
    },
    "instructions": [
      "First, explain your approach in detail",
      "Then write your code solution",
      "Do not switch tabs or paste code"
    ],
    "anti_cheat_active": true
  }
}
```

#### Submit Technical Answer

**Endpoint**: `POST /api/ai/advanced-interview/technical/submit`

**Request**:
```json
{
  "session_id": "interview_user123_abc123",
  "question_id": "tech_1",
  "approach_explanation": "I will iterate through the array once to find the maximum, then iterate again to find the second maximum...",
  "code_solution": "def second_largest(arr):\n    if len(arr) < 2:\n        return None\n    ...",
  "time_taken": 245,
  "tab_switches": 0,
  "paste_attempts": 0
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "overall_score": 85,
    "approach_score": 90,
    "code_score": 80,
    "approach_feedback": "Clear explanation of the two-pass algorithm...",
    "code_feedback": "Code is correct and handles edge cases well...",
    "strengths": ["Clear logic", "Good edge case handling"],
    "weaknesses": ["Could optimize to single pass"],
    "edge_cases_handled": true,
    "time_complexity": "O(n)",
    "space_complexity": "O(1)",
    "code_readability": 85,
    "improvement_suggestions": ["Consider single-pass solution"],
    "passed_test_cases": 2,
    "total_test_cases": 2
  }
}
```

---

### 3. Aptitude Interview

#### Get Aptitude Question

**Endpoint**: `POST /api/ai/advanced-interview/aptitude/question`

**Request**:
```json
{
  "session_id": "interview_user123_abc123",
  "question_number": 1
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "question": {
      "question_id": "apt_1",
      "difficulty": "medium",
      "category": "logical_reasoning",
      "question_text": "If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops definitely Lazzies?",
      "options": [
        "A) Yes",
        "B) No",
        "C) Cannot be determined",
        "D) Only sometimes"
      ],
      "time_limit": 60,
      "requires_reasoning": true
    },
    "instructions": [
      "Select the correct answer",
      "Explain your reasoning",
      "Time limit will be enforced"
    ]
  }
}
```

#### Submit Aptitude Answer

**Endpoint**: `POST /api/ai/advanced-interview/aptitude/submit`

**Request**:
```json
{
  "session_id": "interview_user123_abc123",
  "question_id": "apt_1",
  "answer": "A",
  "reasoning": "This is a transitive property. If A→B and B→C, then A→C. Therefore all Bloops are Lazzies.",
  "time_taken": 45
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "is_correct": true,
    "score": 95,
    "reasoning_quality": 90,
    "reasoning_feedback": "Excellent use of logical reasoning and transitive property",
    "speed_rating": "optimal",
    "explanation": "Correct! This demonstrates transitive property in logic.",
    "improvement_tip": "Great work! Continue practicing similar logical reasoning problems."
  }
}
```

---

### 4. Soft Skills Interview

#### Get Soft Skills Question

**Endpoint**: `POST /api/ai/advanced-interview/soft-skills/question`

**Request**:
```json
{
  "session_id": "interview_user123_abc123",
  "question_number": 1,
  "previous_answer": null  // For adaptive follow-ups
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "question": {
      "question_id": "soft_1",
      "question_text": "Tell me about a time when you had to work with a difficult team member. How did you handle it?",
      "question_type": "behavioral",
      "star_method_applicable": true,
      "evaluation_focus": ["Conflict resolution", "Communication", "Teamwork"],
      "time_limit": 180,
      "follow_up_prompts": [
        "What was the outcome?",
        "What would you do differently?"
      ]
    },
    "instructions": [
      "Use the STAR method",
      "Be specific and provide examples",
      "Focus on your role and impact"
    ],
    "star_method_guide": {
      "Situation": "Describe the context",
      "Task": "Explain your responsibility",
      "Action": "Detail what you did",
      "Result": "Share the outcome and impact"
    }
  }
}
```

#### Submit Soft Skills Answer

**Endpoint**: `POST /api/ai/advanced-interview/soft-skills/submit`

**Request**:
```json
{
  "session_id": "interview_user123_abc123",
  "question_id": "soft_1",
  "answer": "In my previous internship (Situation), I was assigned to work with a team member who was consistently missing deadlines (Task). I scheduled a one-on-one meeting to understand their challenges (Action). We discovered they were overwhelmed with tasks, so I helped redistribute the workload. As a result, we completed the project on time and our team collaboration improved significantly (Result).",
  "time_taken": 120
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "overall_score": 88,
    "clarity_score": 90,
    "structure_score": 95,
    "impact_score": 80,
    "confidence_level": "high",
    "star_method_used": true,
    "star_breakdown": {
      "situation": "present",
      "task": "present",
      "action": "present",
      "result": "present"
    },
    "communication_quality": "excellent",
    "strengths": [
      "Clear STAR structure",
      "Specific example",
      "Demonstrated empathy"
    ],
    "weaknesses": [
      "Could quantify the impact more"
    ],
    "improvement_suggestions": [
      "Add specific metrics to the result",
      "Mention long-term impact"
    ],
    "follow_up_needed": false
  }
}
```

---

### 5. Get Interview Report

**Endpoint**: `GET /api/ai/advanced-interview/report/{session_id}`

**Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "interview_user123_abc123",
    "overall_score": 74.5,
    "technical": {
      "score": 68.0,
      "strengths": ["Basic SQL", "Problem understanding"],
      "weaknesses": ["Edge case handling", "Code optimization"],
      "priority_skills": ["Python", "Algorithms"],
      "questions_attempted": 4
    },
    "aptitude": {
      "score": 76.0,
      "correct_answers": 2,
      "total_questions": 3,
      "accuracy": 66.7,
      "analysis": "Answered 2/3 correctly. Good foundation, practice more complex problems."
    },
    "soft_skills": {
      "score": 82.0,
      "star_method_usage": "2/3",
      "feedback": "Used STAR method in 2/3 answers. Good communication, work on structuring answers better.",
      "questions_answered": 3
    },
    "cheating_flags": {
      "tab_switches": 1,
      "paste_attempts": 0,
      "suspicious_speed": false,
      "identical_answers": false,
      "severity": "low"
    },
    "next_actions": [
      "Practice Python and Algorithms",
      "Solve 5 coding problems daily",
      "Practice STAR method for behavioral questions",
      "Attempt 1 more mock interview before real interviews"
    ],
    "interview_duration": 1800,
    "readiness_level": "needs_practice",
    "weights_used": {
      "technical": 40.0,
      "aptitude": 30.0,
      "soft_skills": 30.0
    }
  }
}
```

---

### 6. Get Session Status

**Endpoint**: `GET /api/ai/advanced-interview/session/{session_id}/status`

**Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "interview_user123_abc123",
    "status": "active",
    "current_question": 5,
    "questions_answered": {
      "technical": 2,
      "aptitude": 2,
      "soft_skills": 1
    },
    "cheating_indicators": {
      "tab_switches": 1,
      "paste_attempts": 0
    }
  }
}
```

---

## Interview Flow

```
1. Start Interview
   ↓
2. Get Question (Technical/Aptitude/Soft Skills)
   ↓
3. Submit Answer
   ↓
4. Repeat steps 2-3 for all questions
   ↓
5. Get Final Report
```

## Anti-Cheating Features

1. **Tab Switch Detection**: Frontend tracks when user switches tabs
2. **Paste Prevention**: Disable paste in code editor
3. **Time Tracking**: Enforce time limits per question
4. **Suspicious Speed Detection**: Flag answers completed too quickly
5. **Severity Levels**: none, low, medium, high

## Evaluation Criteria

### Technical
- Approach explanation quality (40%)
- Code correctness (30%)
- Edge case handling (15%)
- Time/space complexity (10%)
- Code readability (5%)

### Aptitude
- Correctness (60%)
- Reasoning quality (30%)
- Speed (10%)

### Soft Skills
- Clarity (25%)
- Structure/STAR method (25%)
- Impact (25%)
- Communication quality (25%)

## Best Practices

1. **Always collect user context** before starting interview
2. **Track cheating indicators** on frontend
3. **Enforce time limits** strictly
4. **Store session data** for report generation
5. **Handle partial submissions** gracefully

## Testing

Test the endpoints using FastAPI docs:
- Development: `http://localhost:8001/docs`
- Look for "AI - Advanced Mock Interview" tag

---

**Status**: ✅ FULLY IMPLEMENTED
**Version**: 1.0.0
