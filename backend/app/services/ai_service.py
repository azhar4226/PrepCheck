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
            
        # Force mock mode for development
        api_key = os.environ.get('GEMINI_API_KEY', '')
        
        # Always use mock in development unless we have a real API key
        self.use_mock = True
        self.model = None
        
        # Only try real API if we have what looks like a real key
        if api_key and len(api_key) > 30 and api_key.startswith('AI'):
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                # Test with a simple prompt
                test_response = self.model.generate_content("Hello")
                self.use_mock = False
                print("✅ Gemini AI service initialized successfully")
            except Exception as e:
                print(f"⚠️  Gemini AI initialization failed, using mock: {e}")
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
        """Generate a mock quiz for development/testing"""
        
        # Sample question templates based on difficulty
        templates = {
            'easy': [
                f"What is the basic concept of {topic}?",
                f"Which of the following is true about {topic}?",
                f"What is the primary purpose of {topic}?",
            ],
            'medium': [
                f"How does {topic} work in practice?",
                f"What are the advantages of using {topic}?",
                f"Which approach is best for implementing {topic}?",
            ],
            'hard': [
                f"What are the complex implications of {topic}?",
                f"How would you optimize {topic} for performance?",
                f"What are the advanced techniques in {topic}?",
            ]
        }
        
        questions = []
        used_templates = set()
        
        for i in range(int(num_questions)):
            # Select a template
            available_templates = [t for t in templates.get(difficulty, templates['medium']) if t not in used_templates]
            if not available_templates:
                available_templates = templates.get(difficulty, templates['medium'])
                used_templates.clear()
            
            template = random.choice(available_templates)
            used_templates.add(template)
            
            # Generate options
            correct_idx = random.randint(0, 3)
            options = {}
            option_letters = ['A', 'B', 'C', 'D']
            
            for j, letter in enumerate(option_letters):
                if j == correct_idx:
                    options[letter] = f"Correct answer for {topic} (Option {letter})"
                else:
                    options[letter] = f"Incorrect option {j+1} for {topic}"
            
            questions.append({
                "question": template,
                "options": options,
                "correct_answer": option_letters[correct_idx],
                "explanation": f"This is the correct answer because it accurately describes the fundamental concept of {topic}. The other options contain common misconceptions or incomplete information.",
                "marks": 1
            })
        
        return {
            "title": f"{topic} - {difficulty.title()} Level Quiz",
            "description": f"AI-generated quiz on {topic} with {difficulty} difficulty level. {additional_context}",
            "questions": questions
        }
    
    def _generate_real_quiz(self, topic, difficulty, num_questions, additional_context=""):
        """Generate a quiz using real Gemini AI"""
        
        if not self.model:
            raise Exception("AI model not available - using mock service")
        
        prompt = f"""
        Create a multiple-choice quiz with the following specifications:
        
        Topic: {topic}
        Difficulty Level: {difficulty}
        Number of Questions: {num_questions}
        Additional Context: {additional_context}
        
        Please generate a quiz in the following JSON format:
        {{
            "title": "Quiz title",
            "description": "Brief description of the quiz",
            "questions": [
                {{
                    "question": "Question text here",
                    "options": {{
                        "A": "Option A text",
                        "B": "Option B text", 
                        "C": "Option C text",
                        "D": "Option D text"
                    }},
                    "correct_answer": "A",
                    "explanation": "Explanation for the correct answer",
                    "marks": 1
                }}
            ]
        }}
        
        Requirements:
        - Each question should have exactly 4 options (A, B, C, D)
        - Only ONE option should be correct
        - Questions should be clear and unambiguous
        - Explanations should be educational and detailed
        - Difficulty should be appropriate for the specified level
        - Questions should cover different aspects of the topic
        - Avoid overly technical jargon unless appropriate for the difficulty level
        
        Make sure the JSON is valid and properly formatted.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Clean the response to extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                quiz_data = json.loads(json_str)
            else:
                # Fallback parsing
                quiz_data = json.loads(response_text)
            
            # Validate and clean the data
            validated_quiz = self._validate_quiz_data(quiz_data)
            
            # Add metadata
            validated_quiz['timestamp'] = datetime.utcnow().isoformat()
            validated_quiz['model'] = 'Gemini Pro'
            validated_quiz['confidence'] = 0.85  # Default confidence
            
            return validated_quiz
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate quiz: {str(e)}")
    
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
