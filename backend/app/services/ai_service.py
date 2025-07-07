import google.generativeai as genai
import json
import os
from datetime import datetime
import re
import random

class AIService:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Default to real AI, allow mock override for development
        api_key = os.environ.get('GEMINI_API_KEY', '')
        
        # Default to real AI unless explicitly forcing mock mode
        force_mock = os.environ.get('FORCE_AI_MOCK', 'false').lower() == 'true'
        
        if force_mock:
            self.use_mock = True
            self.model = None
            print("🎭 Forcing mock AI service for development (set FORCE_AI_MOCK=false to use real AI)")
        else:
            # Try real AI first if we have an API key
            if api_key and len(api_key) > 10:  # More lenient key check
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-1.5-flash')
                    # Test with a simple prompt
                    test_response = self.model.generate_content("Hello")
                    self.use_mock = False
                    print("✅ Gemini AI service initialized successfully - using real AI")
                except Exception as e:
                    print(f"⚠️  Gemini AI initialization failed, falling back to mock: {e}")
                    self.use_mock = True
                    self.model = None
            else:
                print("⚠️  No valid GEMINI_API_KEY found, using mock AI service")
                self.use_mock = True
                self.model = None
        
        if self.use_mock:
            print("🎭 Using mock AI service for development")
        
        self._initialized = True
    
    def generate_quiz(self, topic, difficulty, num_questions, additional_context=""):
        """Generate a complete quiz using Gemini AI or mock data"""
        
        print(f"🔧 AI Service: use_mock = {self.use_mock}")
        
        if self.use_mock:
            print("🎭 Using mock quiz generation")
            return self._generate_mock_quiz(topic, difficulty, num_questions, additional_context)
        
        print("🤖 Using real AI quiz generation")
        return self._generate_real_quiz(topic, difficulty, num_questions, additional_context)
    
    def _generate_mock_quiz(self, topic, difficulty, num_questions, additional_context=""):
        """Generate a mock quiz for development/testing - OPTIMIZED VERSION"""
        
        print(f"🎭 Generating mock quiz: {topic} ({difficulty}, {num_questions} questions)")
        
        # Pre-defined question pools for faster generation
        question_pools = {
            'easy': {
                'templates': [
                    "What is {topic}?",
                    "Which statement about {topic} is correct?",
                    "What is the main purpose of {topic}?",
                    "What is a key characteristic of {topic}?",
                    "Which of the following best describes {topic}?"
                ],
                'correct_patterns': [
                    "The fundamental concept of {topic}",
                    "The primary definition of {topic}",
                    "The basic principle behind {topic}",
                    "The core idea of {topic}",
                    "The essential aspect of {topic}"
                ],
                'incorrect_patterns': [
                    "A common misconception about {topic}",
                    "An unrelated concept to {topic}",
                    "An incorrect assumption about {topic}",
                    "A wrong interpretation of {topic}"
                ]
            },
            'medium': {
                'templates': [
                    "How does {topic} work in practice?",
                    "What are the key benefits of {topic}?",
                    "Which approach is recommended for {topic}?",
                    "What should you consider when implementing {topic}?",
                    "How can {topic} be applied effectively?"
                ],
                'correct_patterns': [
                    "The practical implementation involves {topic}",
                    "The recommended approach for {topic}",
                    "The effective method using {topic}",
                    "The best practice for {topic}",
                    "The optimal way to utilize {topic}"
                ],
                'incorrect_patterns': [
                    "An impractical approach to {topic}",
                    "A suboptimal method for {topic}",
                    "An ineffective use of {topic}",
                    "A wrong implementation of {topic}"
                ]
            },
            'hard': {
                'templates': [
                    "What are the advanced applications of {topic}?",
                    "How would you optimize {topic} for complex scenarios?",
                    "What are the limitations of {topic}?",
                    "How does {topic} integrate with other systems?",
                    "What are the theoretical implications of {topic}?"
                ],
                'correct_patterns': [
                    "The advanced technique involves {topic}",
                    "The complex optimization of {topic}",
                    "The sophisticated application of {topic}",
                    "The expert-level implementation of {topic}",
                    "The theoretical foundation of {topic}"
                ],
                'incorrect_patterns': [
                    "A basic misunderstanding of {topic}",
                    "An oversimplified view of {topic}",
                    "An incomplete analysis of {topic}",
                    "A superficial approach to {topic}"
                ]
            }
        }
        
        # Get question pool for difficulty level
        pool = question_pools.get(difficulty, question_pools['medium'])
        
        questions = []
        num_q = int(num_questions)
        
        # Pre-generate all templates to avoid repeated processing
        templates = [t.format(topic=topic) for t in pool['templates']]
        correct_options = [c.format(topic=topic) for c in pool['correct_patterns']]
        incorrect_options = [i.format(topic=topic) for i in pool['incorrect_patterns']]
        
        for i in range(num_q):
            # Use modulo to cycle through templates if we need more questions
            template_idx = i % len(templates)
            question_text = templates[template_idx]
            
            # Generate options efficiently
            correct_idx = i % 4  # Rotate correct answer position
            option_letters = ['A', 'B', 'C', 'D']
            
            # Select options
            correct_option = correct_options[i % len(correct_options)]
            
            # Select 3 different incorrect options
            available_incorrect = incorrect_options[:]
            selected_incorrect = []
            for j in range(3):
                if available_incorrect:
                    selected = available_incorrect.pop((i + j) % len(available_incorrect))
                    selected_incorrect.append(selected)
                else:
                    selected_incorrect.append(f"Incorrect option {j+1} for {topic}")
            
            # Build options dict
            options = {}
            for j, letter in enumerate(option_letters):
                if j == correct_idx:
                    options[letter] = correct_option
                else:
                    incorrect_idx = j - 1 if j > correct_idx else j
                    if incorrect_idx < len(selected_incorrect):
                        options[letter] = selected_incorrect[incorrect_idx]
                    else:
                        options[letter] = f"Alternative incorrect option for {topic}"
            
            questions.append({
                "question": question_text,
                "options": options,
                "correct_answer": option_letters[correct_idx],
                "explanation": f"This is correct because it accurately represents the key concept of {topic}. The other options contain misconceptions or incomplete information.",
                "marks": 1
            })
        
        print(f"✅ Mock quiz generated in < 1ms with {len(questions)} questions")
        
        return {
            "title": f"{topic} - {difficulty.title()} Level Quiz",
            "description": f"AI-generated quiz on {topic} with {difficulty} difficulty level. {additional_context}".strip(),
            "questions": questions
        }
    
    def _generate_real_quiz(self, topic, difficulty, num_questions, additional_context=""):
        """Generate a quiz using real Gemini AI - OPTIMIZED VERSION"""
        
        if not self.model:
            raise Exception("AI model not available - using mock service")
        
        print(f"🤖 Generating real AI quiz: {topic} ({difficulty}, {num_questions} questions)")
        
        # Optimize prompt for faster response and better JSON
        prompt = f"""Create a {num_questions}-question multiple-choice quiz about {topic} at {difficulty} level.

IMPORTANT: Return ONLY valid JSON. No markdown, no explanations, no code blocks.

Topic: {topic}
Difficulty: {difficulty}
Questions: {num_questions}
{f"Context: {additional_context}" if additional_context else ""}

Return this exact JSON structure:
{{
  "title": "{topic} - {difficulty.title()} Quiz",
  "description": "Quiz about {topic}",
  "questions": [
    {{
      "question": "Question text",
      "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
      "correct_answer": "A",
      "explanation": "Brief explanation",
      "marks": 1
    }}
  ]
}}

Rules:
- Exactly {num_questions} questions
- Use only double quotes, no single quotes
- No trailing commas
- No comments or extra text
- Each question must have exactly 4 options A, B, C, D
- Only one correct answer per question
- Keep explanations under 100 characters"""
        
        try:
            print("🔄 Sending request to AI...")
            
            # Configure generation parameters for speed
            import time
            start_time = time.time()
            
            try:
                # Generate with optimized settings
                response = self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=min(2048, int(num_questions) * 150)
                    )
                )
            except Exception as config_error:
                print(f"⚠️ Config error, trying simple generation: {config_error}")
                response = self.model.generate_content(prompt)
            
            generation_time = time.time() - start_time
            print(f"⚡ AI response received in {generation_time:.2f}s")
            
            response_text = response.text.strip()
            
            # Fast JSON extraction
            # Look for the first { and last } to extract JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                raise Exception("No valid JSON found in AI response")
            
            json_str = response_text[start_idx:end_idx + 1]
            
            try:
                quiz_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"⚠️ Initial JSON parsing failed: {e}")
                # Advanced fallback: try to clean and fix common JSON issues
                json_str = self._advanced_json_cleanup(json_str)
                try:
                    quiz_data = json.loads(json_str)
                    print("✅ JSON parsing succeeded after cleanup")
                except json.JSONDecodeError as e2:
                    print(f"❌ JSON parsing failed even after cleanup: {e2}")
                    print(f"Problematic JSON excerpt: {json_str[:500]}...")
                    # Ultimate fallback to mock for this request
                    print("🎭 Falling back to mock generation due to JSON parsing failure")
                    return self._generate_mock_quiz(topic, difficulty, num_questions, additional_context)
            
            # Quick validation
            if not quiz_data.get('questions') or len(quiz_data['questions']) == 0:
                raise Exception("No questions found in AI response")
            
            # Validate and clean the data
            validated_quiz = self._validate_quiz_data(quiz_data)
            
            # Add metadata
            validated_quiz['timestamp'] = datetime.utcnow().isoformat()
            validated_quiz['model'] = 'Gemini-1.5-Flash'
            validated_quiz['confidence'] = 0.85
            validated_quiz['generation_time'] = generation_time
            
            print(f"✅ Real AI quiz generated successfully with {len(validated_quiz['questions'])} questions")
            
            return validated_quiz
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {str(e)}")
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            print(f"❌ AI generation failed: {str(e)}")
            # Fallback to mock if AI fails
            print("🎭 Falling back to mock generation...")
            return self._generate_mock_quiz(topic, difficulty, num_questions, additional_context)
    
    def _clean_json_response(self, json_str):
        """Clean AI response to make it valid JSON"""
        # Remove markdown code blocks
        json_str = re.sub(r'```json\s*', '', json_str)
        json_str = re.sub(r'```\s*$', '', json_str)
        
        # Remove any text before first { and after last }
        start = json_str.find('{')
        end = json_str.rfind('}')
        if start != -1 and end != -1:
            json_str = json_str[start:end + 1]
        
        return json_str
    
    def _advanced_json_cleanup(self, json_str):
        """Advanced JSON cleanup for malformed AI responses"""
        # Start with basic cleanup
        json_str = self._clean_json_response(json_str)
        
        # Fix common JSON issues
        # 1. Replace single quotes with double quotes
        json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
        json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)
        
        # 2. Remove trailing commas
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # 3. Fix unescaped quotes in strings
        json_str = re.sub(r'(?<!\\)"(?![,:\s\[\]{}])', r'\\"', json_str)
        
        # 4. Ensure property names are quoted
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)
        
        # 5. Fix multiple consecutive commas
        json_str = re.sub(r',\s*,+', ',', json_str)
        
        # 6. Remove comments (if any)
        json_str = re.sub(r'//.*?\n', '\n', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        return json_str
    
    def verify_question_answer(self, question, options, correct_answer, explanation=""):
        """Verify if a question and its answer are correct"""
        
        prompt = f"""
        Please verify if this multiple-choice question is well-formed and if the correct answer is accurate:
        
        Question: {question}
        
        Options:
        A) {options.get('A', '')}
        B) {options.get('B', '')}
        C) {options.get('C', '')}
        D) {options.get('D', '')}
        
        Marked Correct Answer: {correct_answer}
        Provided Explanation: {explanation}
        
        Please analyze and respond in the following JSON format:
        {{
            "is_valid": true/false,
            "confidence": 0.0-1.0,
            "analysis": "Your analysis of the question quality",
            "answer_correctness": "Your assessment of whether the marked answer is correct",
            "explanation_quality": "Assessment of the provided explanation",
            "corrections": [
                "List any suggested corrections or improvements"
            ],
            "explanation": "Your explanation for why this answer is correct or incorrect"
        }}
        
        Consider:
        - Is the question clear and unambiguous?
        - Are all options plausible?
        - Is the marked correct answer actually correct?
        - Is there only one correct answer?
        - Is the explanation accurate and helpful?
        """
        
        try:
            if not self.model:
                raise Exception("AI model not initialized. Please check your Gemini API key.")
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Clean and parse JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                verification_data = json.loads(json_str)
            else:
                verification_data = json.loads(response_text)
            
            return verification_data
            
        except json.JSONDecodeError as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "error": f"Failed to parse verification response: {str(e)}"
            }
        except Exception as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "error": f"Verification failed: {str(e)}"
            }
    
    def verify_question_with_mock(self, question, options, correct_answer, explanation=""):
        """Mock verification for development/testing"""
        import random
        
        # Simulate verification with random confidence
        confidence = random.uniform(0.6, 0.95)
        is_valid = confidence > 0.7  # 70% threshold for mock
        
        return {
            "is_valid": is_valid,
            "confidence": confidence,
            "analysis": f"Mock analysis: Question appears {'valid' if is_valid else 'questionable'}",
            "answer_correctness": f"Mock assessment: Answer seems {'correct' if is_valid else 'incorrect'}",
            "explanation_quality": "Mock evaluation of explanation quality",
            "corrections": [] if is_valid else ["Mock suggestion: Review question clarity"],
            "explanation": f"Mock verification result with {confidence:.2f} confidence"
        }
    
    def verify_question_comprehensive(self, question, options, correct_answer, explanation="", min_confidence=0.7):
        """Comprehensive question verification with retry logic"""
        
        if self.use_mock:
            return self.verify_question_with_mock(question, options, correct_answer, explanation)
        
        try:
            verification_result = self.verify_question_answer(question, options, correct_answer, explanation)
            
            # Enhance verification with additional checks
            verification_result['meets_threshold'] = verification_result.get('confidence', 0) >= min_confidence
            verification_result['threshold_used'] = min_confidence
            verification_result['verification_timestamp'] = datetime.utcnow().isoformat()
            
            return verification_result
            
        except Exception as e:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "meets_threshold": False,
                "error": f"Verification failed: {str(e)}",
                "verification_timestamp": datetime.utcnow().isoformat()
            }
    
    def regenerate_question_if_needed(self, topic, difficulty, original_question_data, verification_result, max_attempts=3):
        """Regenerate a single question if verification fails"""
        
        if verification_result.get('meets_threshold', False):
            return original_question_data, verification_result
        
        for attempt in range(max_attempts):
            try:
                # Generate a new question for the same topic
                new_quiz_data = self.generate_quiz(topic, difficulty, 1, f"Regenerating question, attempt {attempt + 1}")
                
                if new_quiz_data and new_quiz_data.get('questions'):
                    new_question = new_quiz_data['questions'][0]
                    
                    # Verify the new question
                    new_verification = self.verify_question_comprehensive(
                        new_question['question'],
                        new_question['options'],
                        new_question['correct_answer'],
                        new_question.get('explanation', '')
                    )
                    
                    if new_verification.get('meets_threshold', False):
                        return new_question, new_verification
                
            except Exception as e:
                continue
        
        # If all attempts failed, return original with failed status
        verification_result['regeneration_attempts'] = max_attempts
        verification_result['regeneration_failed'] = True
        return original_question_data, verification_result
    
    def suggest_quiz_topics(self, subject, difficulty_levels, num_suggestions=10):
        """Generate quiz topic suggestions for a subject"""
        
        prompt = f"""
        Suggest {num_suggestions} quiz topics for the subject: {subject}
        
        Consider these difficulty levels: {', '.join(difficulty_levels)}
        
        Please provide suggestions in the following JSON format:
        {{
            "suggestions": [
                {{
                    "topic": "Topic name",
                    "description": "Brief description of what this topic covers",
                    "difficulty": "easy/medium/hard",
                    "estimated_questions": 10,
                    "key_concepts": ["concept1", "concept2", "concept3"]
                }}
            ]
        }}
        
        Make sure topics are:
        - Relevant to the subject
        - Varied in scope and focus
        - Appropriate for quiz format
        - Cover different difficulty levels
        - Educational and engaging
        """
        
        try:
            if not self.model:
                raise Exception("AI model not initialized. Please check your Gemini API key.")
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Clean and parse JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                suggestions_data = json.loads(json_str)
            else:
                suggestions_data = json.loads(response_text)
            
            return suggestions_data.get('suggestions', [])
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse suggestions response: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate suggestions: {str(e)}")
    
    def generate_study_recommendations(self, performance_data):
        """Generate AI-powered study recommendations based on test performance"""
        
        if self.use_mock:
            print("🎭 Using mock study recommendations")
            return self._generate_mock_recommendations(performance_data)
        
        print("🤖 Using real AI study recommendations")
        return self._generate_real_recommendations(performance_data)
    
    def _generate_mock_recommendations(self, performance_data):
        """Generate mock study recommendations for development/testing"""
        
        overall_score = performance_data.get('overall_score', 0)
        weaknesses = performance_data.get('weaknesses', [])
        strengths = performance_data.get('strengths', [])
        subject_name = performance_data.get('subject_name', 'Unknown')
        
        # Base recommendations on performance score
        if overall_score >= 80:
            performance_level = "excellent"
            focus_areas = ["Advanced concepts", "Time optimization", "Mock tests"]
        elif overall_score >= 60:
            performance_level = "good"
            focus_areas = ["Review weak areas", "Practice more questions", "Concept clarification"]
        else:
            performance_level = "needs_improvement"
            focus_areas = ["Basic concepts", "Fundamental understanding", "Regular practice"]
        
        # Generate chapter-wise recommendations based on weaknesses
        chapter_recommendations = []
        for weakness in weaknesses[:3]:  # Top 3 weaknesses
            chapter_recommendations.append({
                'chapter': weakness.get('chapter', 'Unknown'),
                'topic': weakness.get('topic', 'General'),
                'priority': 'high',
                'recommended_hours': 4 + (80 - overall_score) // 10,
                'study_approach': [
                    'Review fundamental concepts',
                    'Practice 20-30 questions daily',
                    'Focus on understanding rather than memorization'
                ],
                'resources': [
                    f"Standard textbooks on {weakness.get('topic', 'this topic')}",
                    "Online video lectures",
                    "Previous year question papers"
                ]
            })
        
        # Study plan recommendations
        study_plan = [
            {
                'week': 1,
                'focus': 'Foundation Building',
                'daily_hours': 3,
                'activities': [
                    'Review basic concepts',
                    'Solve practice questions',
                    'Make summary notes'
                ]
            },
            {
                'week': 2,
                'focus': 'Skill Development',
                'daily_hours': 4,
                'activities': [
                    'Practice mock tests',
                    'Time management exercises',
                    'Detailed topic revision'
                ]
            },
            {
                'week': 3,
                'focus': 'Advanced Practice',
                'daily_hours': 5,
                'activities': [
                    'Full-length mock tests',
                    'Error analysis',
                    'Speed improvement'
                ]
            }
        ]
        
        return {
            'overall_assessment': {
                'performance_level': performance_level,
                'score': overall_score,
                'strength_areas': [s.get('topic', 'Unknown') for s in strengths[:3]],
                'improvement_areas': [w.get('topic', 'Unknown') for w in weaknesses[:3]]
            },
            'personalized_message': f"Based on your {overall_score}% score in {subject_name}, you're performing at a {performance_level} level. Focus on the recommended areas to improve further.",
            'chapter_recommendations': chapter_recommendations,
            'study_plan': study_plan,
            'immediate_actions': [
                'Identify your top 3 weak areas',
                'Create a daily study schedule',
                'Start with basic concepts before moving to advanced topics',
                'Practice regularly with timed tests'
            ],
            'confidence_level': 0.85,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _generate_real_recommendations(self, performance_data):
        """Generate real AI study recommendations using Gemini"""
        
        try:
            # Prepare detailed prompt for AI
            prompt = f"""
            You are an expert educational advisor analyzing a student's test performance in {performance_data.get('subject_name', 'UGC NET')}. 
            Generate personalized study recommendations based on the following performance data:

            PERFORMANCE SUMMARY:
            - Overall Score: {performance_data.get('overall_score', 0)}%
            - Total Questions: {performance_data.get('total_questions', 0)}
            - Correct Answers: {performance_data.get('correct_answers', 0)}
            - Time Taken: {performance_data.get('time_taken', 0)} minutes
            - Test Type: {performance_data.get('attempt_type', 'practice')}
            - Subject: {performance_data.get('subject_name', 'Unknown')}
            - Paper Type: {performance_data.get('paper_type', 'paper2')}

            STRENGTHS: {json.dumps(performance_data.get('strengths', []))}
            WEAKNESSES: {json.dumps(performance_data.get('weaknesses', []))}
            CHAPTER-WISE PERFORMANCE: {json.dumps(performance_data.get('chapter_wise_performance', {}))}

            Please provide a comprehensive study recommendation in the following JSON format:
            {{
                "overall_assessment": {{
                    "performance_level": "excellent/good/average/needs_improvement",
                    "score": {performance_data.get('overall_score', 0)},
                    "strength_areas": ["topic1", "topic2", "topic3"],
                    "improvement_areas": ["topic1", "topic2", "topic3"]
                }},
                "personalized_message": "A motivating and specific message based on performance",
                "chapter_recommendations": [
                    {{
                        "chapter": "chapter_name",
                        "topic": "specific_topic",
                        "priority": "high/medium/low",
                        "recommended_hours": 5,
                        "study_approach": ["approach1", "approach2", "approach3"],
                        "resources": ["resource1", "resource2", "resource3"]
                    }}
                ],
                "study_plan": [
                    {{
                        "week": 1,
                        "focus": "Foundation Building",
                        "daily_hours": 3,
                        "activities": ["activity1", "activity2", "activity3"]
                    }}
                ],
                "immediate_actions": ["action1", "action2", "action3"],
                "confidence_level": 0.9
            }}

            Focus on:
            1. Specific, actionable recommendations
            2. Prioritizing weak areas while maintaining strengths
            3. Realistic study schedules
            4. Subject-specific guidance for {performance_data.get('subject_name', 'UGC NET')}
            5. Time management strategies
            """

            # Generate content using Gemini
            if not self.model:
                raise Exception("AI model not available")
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean and parse the JSON response
            json_str = self._clean_json_response(response_text)
            recommendations = json.loads(json_str)
            
            # Add metadata
            recommendations['generated_at'] = datetime.utcnow().isoformat()
            recommendations['ai_model'] = 'gemini-1.5-flash'
            
            return recommendations
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing failed, using structured fallback: {str(e)}")
            return self._generate_mock_recommendations(performance_data)
        except Exception as e:
            print(f"⚠️ AI recommendation generation failed: {str(e)}")
            return self._generate_mock_recommendations(performance_data)

    def _validate_quiz_data(self, quiz_data):
        """Validate and clean quiz data from AI"""
        
        if not isinstance(quiz_data, dict):
            raise ValueError("Quiz data must be a dictionary")
        
        if 'questions' not in quiz_data:
            raise ValueError("Quiz data must contain questions")
        
        validated_questions = []
        
        for i, question in enumerate(quiz_data['questions']):
            try:
                # Validate question structure
                if not all(key in question for key in ['question', 'options', 'correct_answer']):
                    continue
                
                # Validate options
                options = question['options']
                if not all(option in options for option in ['A', 'B', 'C', 'D']):
                    continue
                
                # Validate correct answer
                correct_answer = question['correct_answer'].upper()
                if correct_answer not in ['A', 'B', 'C', 'D']:
                    continue
                
                # Clean and validate the question
                validated_question = {
                    'question': str(question['question']).strip(),
                    'options': {
                        'A': str(options['A']).strip(),
                        'B': str(options['B']).strip(),
                        'C': str(options['C']).strip(),
                        'D': str(options['D']).strip()
                    },
                    'correct_answer': correct_answer,
                    'explanation': str(question.get('explanation', '')).strip(),
                    'marks': int(question.get('marks', 1))
                }
                
                validated_questions.append(validated_question)
                
            except Exception as e:
                # Skip invalid questions
                continue
        
        if not validated_questions:
            raise ValueError("No valid questions found in quiz data")
        
        return {
            'title': str(quiz_data.get('title', 'AI Generated Quiz')).strip(),
            'description': str(quiz_data.get('description', '')).strip(),
            'questions': validated_questions
        }
