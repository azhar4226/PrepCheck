import google.generativeai as genai
import json
import os
from datetime import datetime
import re

class AIService:
    def __init__(self):
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_quiz(self, topic, difficulty, num_questions, additional_context=""):
        """Generate a complete quiz using Gemini AI"""
        
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
