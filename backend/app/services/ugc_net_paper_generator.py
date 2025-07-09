"""
UGC NET Paper Generator Service
Handles the generation of UGC NET mock papers based on weightage system
"""

import random
import json
from typing import Dict, List, Any
from app import db
from app.models import Subject, Chapter, QuestionBank
from app.utils.ugc_net_seed_data import get_subject_weightage_info


class UGCNetPaperGenerator:
    """Service class for generating UGC NET mock papers with proper weightage distribution"""
    
    def __init__(self):
        self.min_questions_per_chapter = 1
        self.max_questions_per_chapter = 15
    
    def generate_paper(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a UGC NET paper based on configuration
        
        Args:
            config: Dictionary containing:
                - subject_id: ID of the subject (for Paper 2)
                - paper_type: 'paper1', 'paper2', or 'mock' (both papers)
                - total_questions: Total number of questions
                - difficulty_distribution: Dict with easy, medium, hard percentages
                - source_distribution: Dict with previous_year, ai_generated percentages
                - weightage_config: Optional custom weightage configuration
        
        Returns:
            Dictionary with generated paper data and statistics
        """
        try:
            subject_id = config['subject_id']
            paper_type = config['paper_type']
            total_questions = config['total_questions']
            
            # Handle mock test (Paper 1 + Paper 2)
            if paper_type == 'mock':
                return self._generate_mock_test(config)
            
            # Get subject and validate
            subject = Subject.query.get(subject_id)
            if not subject:
                return {'success': False, 'error': 'Subject not found'}
            
            # Get chapters with weightage
            weightage_config = config.get('weightage_config')
            if weightage_config:
                # Handle custom weightage config (dict mapping chapter_id to weightage)
                if isinstance(weightage_config, dict) and 'chapters' not in weightage_config:
                    # Convert simple weightage dict to proper format
                    chapters_data = []
                    for chapter_id_str, weightage in weightage_config.items():
                        try:
                            chapter_id = int(chapter_id_str)
                            chapter = Chapter.query.get(chapter_id)
                            if chapter and chapter.subject_id == subject_id:
                                chapters_data.append({
                                    'chapter_id': chapter_id,
                                    'chapter_name': chapter.name,
                                    'weightage': weightage
                                })
                        except (ValueError, TypeError):
                            continue
                else:
                    # Use provided chapters data directly
                    chapters_data = weightage_config.get('chapters', [])
            else:
                # Use default weightage info from seed data
                weightage_info = get_subject_weightage_info(subject_id, paper_type)
                chapters_data = weightage_info.get('chapters', []) if weightage_info else []
            
            if not chapters_data:
                return {'success': False, 'error': 'No chapters found for this subject'}
            
            # Calculate question distribution based on weightage
            question_distribution = self._calculate_question_distribution(
                chapters_data, total_questions
            )
            
            # Generate questions for each chapter
            generated_questions = []
            statistics = {
                'total_questions': 0,
                'chapter_wise_distribution': {},
                'difficulty_distribution': {'easy': 0, 'medium': 0, 'hard': 0},
                'source_distribution': {'previous_year': 0, 'ai_generated': 0, 'manual': 0}
            }
            
            for chapter_info in question_distribution:
                chapter_id = chapter_info['chapter_id']
                required_questions = chapter_info['questions_needed']
                
                # Get questions for this chapter
                chapter_questions = self._get_chapter_questions(
                    chapter_id,
                    required_questions,
                    config.get('difficulty_distribution', {}),
                    config.get('source_distribution', {})
                )
                
                generated_questions.extend(chapter_questions)
                
                # Update statistics
                statistics['chapter_wise_distribution'][chapter_info['chapter_name']] = {
                    'required': required_questions,
                    'generated': len(chapter_questions),
                    'weightage': chapter_info['weightage']
                }
                
                # Update difficulty and source statistics
                for question in chapter_questions:
                    difficulty = question.difficulty
                    source = question.source
                    
                    statistics['difficulty_distribution'][difficulty] += 1
                    statistics['source_distribution'][source] += 1
            
            # Shuffle questions to randomize order
            random.shuffle(generated_questions)
            
            statistics['total_questions'] = len(generated_questions)
            
            # Check if we have enough questions
            if len(generated_questions) < total_questions * 0.8:  # Allow 20% shortfall
                return {
                    'success': False,
                    'error': f'Insufficient questions in database. Generated {len(generated_questions)} out of {total_questions} required'
                }
            
            return {
                'success': True,
                'paper': {
                    'subject': subject.to_dict(),
                    'paper_type': paper_type,
                    'total_questions': len(generated_questions),
                    'questions': generated_questions
                },
                'statistics': statistics
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_question_distribution(self, chapters_data: List[Dict], total_questions: int) -> List[Dict]:
        """Calculate how many questions should come from each chapter based on weightage"""
        
        # Calculate total weightage
        total_weightage = sum(chapter['weightage'] for chapter in chapters_data if chapter['weightage'] > 0)
        
        if total_weightage == 0:
            # Equal distribution if no weightage
            questions_per_chapter = total_questions // len(chapters_data)
            return [
                {
                    'chapter_id': chapter['chapter_id'],
                    'chapter_name': chapter['chapter_name'],
                    'weightage': chapter['weightage'],
                    'questions_needed': questions_per_chapter
                }
                for chapter in chapters_data
            ]
        
        distribution = []
        allocated_questions = 0
        
        for chapter in chapters_data:
            if chapter['weightage'] > 0:
                # Calculate questions based on weightage proportion
                questions_needed = int((chapter['weightage'] / total_weightage) * total_questions)
                
                # Ensure minimum and maximum bounds
                questions_needed = max(self.min_questions_per_chapter, questions_needed)
                questions_needed = min(self.max_questions_per_chapter, questions_needed)
                
                distribution.append({
                    'chapter_id': chapter['chapter_id'],
                    'chapter_name': chapter['chapter_name'],
                    'weightage': chapter['weightage'],
                    'questions_needed': questions_needed
                })
                
                allocated_questions += questions_needed
        
        # Adjust if we've allocated more or fewer questions than needed
        remaining_questions = total_questions - allocated_questions
        if remaining_questions != 0:
            # Distribute remaining questions proportionally
            for i, chapter_dist in enumerate(distribution):
                if remaining_questions > 0:
                    distribution[i]['questions_needed'] += 1
                    remaining_questions -= 1
                elif remaining_questions < 0 and distribution[i]['questions_needed'] > self.min_questions_per_chapter:
                    distribution[i]['questions_needed'] -= 1
                    remaining_questions += 1
        
        return distribution
    
    def _get_chapter_questions(self, chapter_id: int, required_count: int, 
                             difficulty_dist: Dict, source_dist: Dict) -> List[QuestionBank]:
        """Get questions for a specific chapter with difficulty and source distribution"""
        
        # Get all available questions for this chapter
        # First try verified questions
        available_questions = QuestionBank.query.filter_by(
            chapter_id=chapter_id,
            is_verified=True
        ).all()
        
        # If no verified questions found, include unverified ones for development/testing
        if not available_questions:
            print(f"No verified questions found for chapter {chapter_id}, including unverified questions for testing")
            available_questions = QuestionBank.query.filter_by(
                chapter_id=chapter_id
            ).all()
        
        if not available_questions:
            return []
        
        # If we don't have enough questions, return all available
        if len(available_questions) <= required_count:
            return available_questions
        
        # Try to maintain difficulty distribution
        selected_questions = []
        
        # Calculate target counts for each difficulty
        easy_target = int(required_count * difficulty_dist.get('easy', 30) / 100)
        medium_target = int(required_count * difficulty_dist.get('medium', 50) / 100)
        hard_target = required_count - easy_target - medium_target
        
        # Group questions by difficulty
        questions_by_difficulty = {
            'easy': [q for q in available_questions if q.difficulty == 'easy'],
            'medium': [q for q in available_questions if q.difficulty == 'medium'],
            'hard': [q for q in available_questions if q.difficulty == 'hard']
        }
        
        # Select questions by difficulty
        targets = [
            ('easy', easy_target),
            ('medium', medium_target),
            ('hard', hard_target)
        ]
        
        for difficulty, target in targets:
            difficulty_questions = questions_by_difficulty[difficulty]
            if difficulty_questions:
                # Randomly select from available questions of this difficulty
                selected_count = min(target, len(difficulty_questions))
                selected = random.sample(difficulty_questions, selected_count)
                selected_questions.extend(selected)
        
        # If we still need more questions, randomly pick from remaining
        if len(selected_questions) < required_count:
            remaining_questions = [
                q for q in available_questions 
                if q not in selected_questions
            ]
            
            additional_needed = required_count - len(selected_questions)
            if remaining_questions:
                additional_count = min(additional_needed, len(remaining_questions))
                additional = random.sample(remaining_questions, additional_count)
                selected_questions.extend(additional)
        
        return selected_questions[:required_count]  # Ensure we don't exceed required count
    
    def validate_paper_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the paper generation configuration"""
        errors = []
        
        # Check required fields
        required_fields = ['subject_id', 'paper_type', 'total_questions']
        for field in required_fields:
            if field not in config:
                errors.append(f'Missing required field: {field}')
        
        # Validate subject exists
        if 'subject_id' in config:
            subject = Subject.query.get(config['subject_id'])
            if not subject:
                errors.append('Subject not found')
        
        # Validate paper type
        if 'paper_type' in config and config['paper_type'] not in ['paper1', 'paper2', 'mock']:
            errors.append('Paper type must be either "paper1", "paper2", or "mock"')
        
        # Validate total questions
        if 'total_questions' in config:
            if not isinstance(config['total_questions'], int) or config['total_questions'] <= 0:
                errors.append('Total questions must be a positive integer')
        
        # Validate difficulty distribution
        if 'difficulty_distribution' in config:
            diff_dist = config['difficulty_distribution']
            total_percentage = sum(diff_dist.values())
            if abs(total_percentage - 100) > 0.1:  # Allow small floating point errors
                errors.append('Difficulty distribution percentages must sum to 100')
        
        # Validate source distribution
        if 'source_distribution' in config:
            source_dist = config['source_distribution']
            total_percentage = sum(source_dist.values())
            if abs(total_percentage - 100) > 0.1:
                errors.append('Source distribution percentages must sum to 100')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def generate_practice_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a UGC NET practice test with focused chapter selection
        
        Args:
            config: Dictionary containing:
                - subject_id: ID of the subject
                - chapter_ids: List of selected chapter IDs (optional, if not provided uses all chapters)
                - paper_type: 'paper1' or 'paper2'
                - total_questions: Total number of questions (default 20)
                - difficulty_distribution: Dict with easy, medium, hard percentages
                - source_distribution: Dict with previous_year, ai_generated percentages
                - practice_type: 'chapter_wise', 'mixed', 'revision'
        
        Returns:
            Dictionary with generated practice test data and statistics
        """
        try:
            subject_id = config['subject_id']
            paper_type = config.get('paper_type', 'paper2')
            total_questions = config.get('total_questions', 20)
            practice_type = config.get('practice_type', 'chapter_wise')
            chapter_ids = config.get('chapter_ids', [])
            
            # Get subject and validate
            subject = Subject.query.get(subject_id)
            if not subject:
                return {'success': False, 'error': 'Subject not found'}
            
            # Get chapters for practice test
            if chapter_ids:
                # Use selected chapters
                chapters = Chapter.query.filter(
                    Chapter.id.in_(chapter_ids),
                    Chapter.subject_id == subject_id,
                    Chapter.is_active == True
                ).all()
            else:
                # Use all chapters for the subject
                chapters = Chapter.query.filter_by(
                    subject_id=subject_id,
                    is_active=True
                ).all()
            
            if not chapters:
                return {'success': False, 'error': 'No chapters found for practice test'}
            
            # Create practice-specific weightage configuration
            if practice_type == 'chapter_wise' and len(chapters) <= 3:
                # Equal distribution for focused chapter practice
                weightage_per_chapter = 100 // len(chapters)
                chapters_data = []
                for chapter in chapters:
                    chapters_data.append({
                        'chapter_id': chapter.id,
                        'chapter_name': chapter.name,
                        'weightage': weightage_per_chapter
                    })
            else:
                # Use existing weightage or equal distribution
                chapters_data = []
                total_weightage = sum(getattr(chapter, f'weightage_{paper_type}', 10) for chapter in chapters)
                
                if total_weightage == 0:
                    # Equal distribution if no weightage set
                    weightage_per_chapter = 100 // len(chapters)
                    for chapter in chapters:
                        chapters_data.append({
                            'chapter_id': chapter.id,
                            'chapter_name': chapter.name,
                            'weightage': weightage_per_chapter
                        })
                else:
                    # Use existing weightage proportionally
                    for chapter in chapters:
                        chapter_weightage = getattr(chapter, f'weightage_{paper_type}', 10)
                        normalized_weightage = (chapter_weightage / total_weightage) * 100
                        chapters_data.append({
                            'chapter_id': chapter.id,
                            'chapter_name': chapter.name,
                            'weightage': normalized_weightage
                        })
            
            # Calculate question distribution
            question_distribution = self._calculate_question_distribution(
                chapters_data, total_questions
            )
            
            # Generate questions for each chapter
            generated_questions = []
            statistics = {
                'total_questions': 0,
                'chapter_wise_distribution': {},
                'difficulty_distribution': {'easy': 0, 'medium': 0, 'hard': 0},
                'source_distribution': {'previous_year': 0, 'ai_generated': 0, 'manual': 0}
            }
            
            for chapter_info in question_distribution:
                chapter_id = chapter_info['chapter_id']
                required_questions = chapter_info['questions_needed']
                
                # Get questions for this chapter
                chapter_questions = self._get_chapter_questions(
                    chapter_id,
                    required_questions,
                    config.get('difficulty_distribution', {'easy': 30, 'medium': 50, 'hard': 20}),
                    config.get('source_distribution', {'previous_year': 70, 'ai_generated': 30})
                )
                
                # Convert QuestionBank objects to dictionaries for practice test
                chapter_questions_data = []
                for question in chapter_questions:
                    question_dict = question.to_dict(include_answer=False)
                    # Add chapter name for easier reference
                    question_dict['chapter_name'] = chapter_info['chapter_name']
                    chapter_questions_data.append(question_dict)
                
                generated_questions.extend(chapter_questions_data)
                
                # Update statistics
                statistics['chapter_wise_distribution'][chapter_info['chapter_name']] = {
                    'required': required_questions,
                    'generated': len(chapter_questions),
                    'weightage': chapter_info['weightage']
                }
                
                # Update difficulty and source statistics
                for question in chapter_questions:
                    difficulty = question.difficulty
                    source = question.source
                    
                    statistics['difficulty_distribution'][difficulty] += 1
                    statistics['source_distribution'][source] += 1
            
            # Shuffle questions to randomize order
            random.shuffle(generated_questions)
            
            statistics['total_questions'] = len(generated_questions)
            
            # Check if we have enough questions
            if len(generated_questions) < total_questions * 0.6:  # Allow 40% shortfall for practice tests
                return {
                    'success': False,
                    'error': f'Insufficient questions for practice test. Generated {len(generated_questions)} out of {total_questions} required'
                }
            
            # Calculate practice-specific metrics
            practice_stats = {
                'practice_type': practice_type,
                'selected_chapters': [ch['chapter_name'] for ch in chapters_data],
                'estimated_time': len(generated_questions) * 1.5,  # 1.5 minutes per question
                'difficulty_level': self._calculate_difficulty_level(statistics['difficulty_distribution'])
            }
            
            return {
                'success': True,
                'practice_test': {
                    'subject': subject.to_dict(),
                    'paper_type': paper_type,
                    'practice_type': practice_type,
                    'total_questions': len(generated_questions),
                    'questions': generated_questions,
                    'selected_chapters': chapter_ids
                },
                'statistics': statistics,
                'practice_stats': practice_stats
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_difficulty_level(self, difficulty_dist: Dict[str, int]) -> str:
        """Calculate overall difficulty level based on question distribution"""
        total_questions = sum(difficulty_dist.values())
        if total_questions == 0:
            return 'medium'
        
        hard_percentage = (difficulty_dist.get('hard', 0) / total_questions) * 100
        easy_percentage = (difficulty_dist.get('easy', 0) / total_questions) * 100
        
        if hard_percentage >= 40:
            return 'hard'
        elif easy_percentage >= 50:
            return 'easy'
        else:
            return 'medium'
    
    def _generate_mock_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a UGC NET mock test with both Paper 1 and Paper 2
        
        Args:
            config: Dictionary containing mock test configuration
        
        Returns:
            Dictionary with generated mock test data
        """
        try:
            subject_id = config['subject_id']
            total_questions = config.get('total_questions', 150)  # Default: 50 Paper 1 + 100 Paper 2
            difficulty_distribution = config.get('difficulty_distribution', {
                'easy': 30, 'medium': 50, 'hard': 20
            })
            
            # Get the subject for Paper 2
            subject = Subject.query.get(subject_id)
            if not subject:
                return {'success': False, 'error': 'Subject not found for Paper 2'}
            
            # Get Paper 1 subject (Teaching & Research Aptitude)
            paper1_subject = Subject.query.filter_by(subject_code='P1').first()
            if not paper1_subject:
                return {'success': False, 'error': 'Paper 1 subject not found. Please ensure UGC NET Paper 1 is seeded.'}
            
            # Fixed distribution: Paper 1 (50 questions), Paper 2 (100 questions)
            paper1_questions = 50
            paper2_questions = total_questions - paper1_questions
            
            # Generate Paper 1 questions
            paper1_config = {
                'subject_id': paper1_subject.id,
                'paper_type': 'paper1',
                'total_questions': paper1_questions,
                'difficulty_distribution': difficulty_distribution
            }
            
            paper1_result = self.generate_paper(paper1_config)
            if not paper1_result['success']:
                return {'success': False, 'error': f'Failed to generate Paper 1: {paper1_result["error"]}'}
            
            # Generate Paper 2 questions
            paper2_config = {
                'subject_id': subject_id,
                'paper_type': 'paper2',
                'total_questions': paper2_questions,
                'difficulty_distribution': difficulty_distribution
            }
            
            paper2_result = self.generate_paper(paper2_config)
            if not paper2_result['success']:
                return {'success': False, 'error': f'Failed to generate Paper 2: {paper2_result["error"]}'}
            
            # Combine questions from both papers
            all_questions = []
            
            # Add Paper 1 questions (mark them as Paper 1)
            for question in paper1_result['paper']['questions']:
                question_dict = question.to_dict() if hasattr(question, 'to_dict') else question
                question_dict['paper_type'] = 'paper1'
                all_questions.append(question_dict)
            
            # Add Paper 2 questions (mark them as Paper 2)
            for question in paper2_result['paper']['questions']:
                question_dict = question.to_dict() if hasattr(question, 'to_dict') else question
                question_dict['paper_type'] = 'paper2'
                all_questions.append(question_dict)
            
            # Shuffle to randomize order while maintaining paper segregation
            # (In actual exam, papers are separate, but for our mock test we can mix)
            random.shuffle(all_questions)
            
            # Combine statistics
            combined_stats = {
                'total_questions': len(all_questions),
                'paper1_questions': paper1_questions,
                'paper2_questions': paper2_questions,
                'difficulty_distribution': {
                    'easy': 0,
                    'medium': 0,
                    'hard': 0
                },
                'source_distribution': {
                    'previous_year': 0,
                    'ai_generated': 0,
                    'manual': 0
                },
                'paper_breakdown': {
                    'paper1': paper1_result.get('statistics', {}),
                    'paper2': paper2_result.get('statistics', {})
                }
            }
            
            # Calculate combined difficulty and source distribution
            for question in all_questions:
                if isinstance(question, dict):
                    difficulty = question.get('difficulty', 'medium')
                    source = question.get('source', 'manual')
                else:
                    difficulty = getattr(question, 'difficulty', 'medium')
                    source = getattr(question, 'source', 'manual')
                
                combined_stats['difficulty_distribution'][difficulty] += 1
                combined_stats['source_distribution'][source] += 1
            
            return {
                'success': True,
                'paper': {
                    'paper1_subject': paper1_subject.to_dict(),
                    'paper2_subject': subject.to_dict(),
                    'paper_type': 'mock',
                    'total_questions': len(all_questions),
                    'questions': all_questions
                },
                'statistics': combined_stats
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Mock test generation failed: {str(e)}'}
