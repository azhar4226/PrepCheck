"""
UGC NET Mock Test Generator Service
Handles intelligent generation of UGC NET style mock tests with proper weightage distribution
"""

import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy import and_, func

from app import db
from app.models import QuestionBank, Chapter, Subject, UGCNetMockTest, UGCNetMockAttempt
from app.utils.ugc_net_seed_data import get_subject_weightage_info


class UGCNetMockTestService:
    """Service for generating and managing UGC NET mock tests"""
    
    @staticmethod
    def calculate_chapter_question_distribution(
        subject_id: int, 
        paper_type: str = 'paper2',
        total_questions: int = 50
    ) -> Dict:
        """
        Calculate how many questions should come from each chapter based on weightage
        """
        weightage_info = get_subject_weightage_info(subject_id, paper_type)
        if not weightage_info:
            raise ValueError(f"Subject {subject_id} not found or has no weightage info")
        
        distribution = {}
        total_weightage = sum(ch['weightage'] for ch in weightage_info['chapters'])
        
        if total_weightage == 0:
            # Equal distribution if no weightage defined
            questions_per_chapter = total_questions // len(weightage_info['chapters'])
            for chapter in weightage_info['chapters']:
                distribution[chapter['chapter_id']] = questions_per_chapter
        else:
            # Distribute based on weightage
            for chapter in weightage_info['chapters']:
                proportion = chapter['weightage'] / total_weightage
                questions_count = max(1, round(total_questions * proportion))  # At least 1 question
                distribution[chapter['chapter_id']] = questions_count
        
        # Adjust if total doesn't match due to rounding
        current_total = sum(distribution.values())
        if current_total != total_questions:
            # Add/remove questions from chapters with highest weightage
            sorted_chapters = sorted(
                weightage_info['chapters'], 
                key=lambda x: x['weightage'], 
                reverse=True
            )
            
            diff = total_questions - current_total
            for i, chapter in enumerate(sorted_chapters):
                if diff == 0:
                    break
                chapter_id = chapter['chapter_id']
                if diff > 0:
                    distribution[chapter_id] += 1
                    diff -= 1
                elif diff < 0 and distribution[chapter_id] > 1:
                    distribution[chapter_id] -= 1
                    diff += 1
        
        return {
            'distribution': distribution,
            'weightage_info': weightage_info
        }
    
    @staticmethod
    def get_questions_by_criteria(
        chapter_id: int,
        count: int,
        difficulty_distribution: Optional[Dict[str, float]] = None,
        source_distribution: Optional[Dict[str, float]] = None,
        exclude_question_ids: Optional[List[int]] = None
    ) -> List[QuestionBank]:
        """
        Get questions from question bank based on criteria
        """
        if difficulty_distribution is None:
            difficulty_distribution = {'easy': 0.3, 'medium': 0.5, 'hard': 0.2}
        
        if source_distribution is None:
            source_distribution = {'previous_year': 0.7, 'ai_generated': 0.3}
        
        if exclude_question_ids is None:
            exclude_question_ids = []
        
        selected_questions = []
        
        # Calculate counts for each difficulty and source
        for difficulty, diff_ratio in difficulty_distribution.items():
            diff_count = max(1, round(count * diff_ratio))
            
            for source, source_ratio in source_distribution.items():
                source_count = max(1, round(diff_count * source_ratio))
                
                # Query questions
                query = QuestionBank.query.filter(
                    and_(
                        QuestionBank.chapter_id == chapter_id,
                        QuestionBank.difficulty == difficulty,
                        QuestionBank.source == source,
                        QuestionBank.is_verified == True,
                        ~QuestionBank.id.in_(exclude_question_ids)
                    )
                )
                
                available_questions = query.all()
                
                if len(available_questions) >= source_count:
                    # Randomly select required count
                    selected = random.sample(available_questions, source_count)
                    selected_questions.extend(selected)
                    exclude_question_ids.extend([q.id for q in selected])
                else:
                    # Use all available questions
                    selected_questions.extend(available_questions)
                    exclude_question_ids.extend([q.id for q in available_questions])
                
                # Break if we have enough questions
                if len(selected_questions) >= count:
                    break
            
            if len(selected_questions) >= count:
                break
        
        # If we still don't have enough, fill with any available questions
        if len(selected_questions) < count:
            remaining_needed = count - len(selected_questions)
            
            fallback_query = QuestionBank.query.filter(
                and_(
                    QuestionBank.chapter_id == chapter_id,
                    QuestionBank.is_verified == True,
                    ~QuestionBank.id.in_(exclude_question_ids)
                )
            )
            
            fallback_questions = fallback_query.limit(remaining_needed).all()
            selected_questions.extend(fallback_questions)
        
        return selected_questions[:count]  # Ensure we don't exceed the count
    
    @staticmethod
    def generate_mock_test_questions(
        subject_id: int,
        paper_type: str = 'paper2',
        total_questions: int = 50,
        difficulty_distribution: Optional[Dict[str, float]] = None,
        source_distribution: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Generate a complete mock test with proper question distribution
        """
        if difficulty_distribution is None:
            difficulty_distribution = {'easy': 0.3, 'medium': 0.5, 'hard': 0.2}
        
        if source_distribution is None:
            source_distribution = {'previous_year': 0.7, 'ai_generated': 0.3}
        
        # Get chapter distribution
        chapter_distribution = UGCNetMockTestService.calculate_chapter_question_distribution(
            subject_id, paper_type, total_questions
        )
        
        mock_test_questions = []
        chapter_wise_questions = {}
        exclude_question_ids = []
        
        for chapter_id, question_count in chapter_distribution['distribution'].items():
            if question_count > 0:
                chapter_questions = UGCNetMockTestService.get_questions_by_criteria(
                    chapter_id=chapter_id,
                    count=question_count,
                    difficulty_distribution=difficulty_distribution,
                    source_distribution=source_distribution,
                    exclude_question_ids=exclude_question_ids
                )
                
                chapter_wise_questions[chapter_id] = chapter_questions
                mock_test_questions.extend(chapter_questions)
                exclude_question_ids.extend([q.id for q in chapter_questions])
        
        # Shuffle the final question order
        random.shuffle(mock_test_questions)
        
        return {
            'questions': mock_test_questions,
            'chapter_wise_distribution': chapter_wise_questions,
            'weightage_info': chapter_distribution['weightage_info'],
            'total_questions': len(mock_test_questions),
            'difficulty_distribution': difficulty_distribution,
            'source_distribution': source_distribution
        }
    
    @staticmethod
    def create_mock_test(
        title: str,
        subject_id: int,
        paper_type: str,
        created_by_user_id: int,
        description: Optional[str] = None,
        total_questions: int = 50,
        total_marks: int = 100,
        time_limit: int = 180,
        difficulty_distribution: Optional[Dict[str, float]] = None,
        source_distribution: Optional[Dict[str, float]] = None
    ) -> UGCNetMockTest:
        """
        Create a new UGC NET mock test configuration
        """
        if difficulty_distribution is None:
            difficulty_distribution = {'easy': 30.0, 'medium': 50.0, 'hard': 20.0}
        
        if source_distribution is None:
            source_distribution = {'previous_year': 70.0, 'ai_generated': 30.0}
        
        mock_test = UGCNetMockTest(
            title=title,
            description=description,
            subject_id=subject_id,
            paper_type=paper_type,
            total_questions=total_questions,
            total_marks=total_marks,
            time_limit=time_limit,
            previous_year_percentage=source_distribution.get('previous_year', 70.0),
            ai_generated_percentage=source_distribution.get('ai_generated', 30.0),
            easy_percentage=difficulty_distribution.get('easy', 30.0),
            medium_percentage=difficulty_distribution.get('medium', 50.0),
            hard_percentage=difficulty_distribution.get('hard', 20.0),
            created_by=created_by_user_id,
            is_active=True
        )
        
        db.session.add(mock_test)
        db.session.commit()
        
        return mock_test
    
    @staticmethod
    def generate_mock_test_for_user(
        mock_test_id: int,
        user_id: int
    ) -> Dict:
        """
        Generate a specific mock test instance for a user
        """
        mock_test = UGCNetMockTest.query.get(mock_test_id)
        if not mock_test:
            raise ValueError(f"Mock test {mock_test_id} not found")
        
        # Convert percentages back to ratios
        difficulty_distribution = {
            'easy': mock_test.easy_percentage / 100.0,
            'medium': mock_test.medium_percentage / 100.0,
            'hard': mock_test.hard_percentage / 100.0
        }
        
        source_distribution = {
            'previous_year': mock_test.previous_year_percentage / 100.0,
            'ai_generated': mock_test.ai_generated_percentage / 100.0
        }
        
        # Generate questions
        generated_test = UGCNetMockTestService.generate_mock_test_questions(
            subject_id=mock_test.subject_id,
            paper_type=mock_test.paper_type,
            total_questions=mock_test.total_questions,
            difficulty_distribution=difficulty_distribution,
            source_distribution=source_distribution
        )
        
        # Create attempt record
        attempt = UGCNetMockAttempt(
            user_id=user_id,
            mock_test_id=mock_test_id,
            total_marks=mock_test.total_marks
        )
        
        # Store questions data
        questions_data = [
            {
                'question_id': q.id,
                'chapter_id': q.chapter_id,
                'difficulty': q.difficulty,
                'source': q.source,
                'marks': q.marks
            } for q in generated_test['questions']
        ]
        
        attempt.set_questions_data(questions_data)
        
        db.session.add(attempt)
        db.session.commit()
        
        return {
            'attempt_id': attempt.id,
            'mock_test': mock_test.to_dict(),
            'questions': [q.to_dict() for q in generated_test['questions']],
            'weightage_info': generated_test['weightage_info'],
            'chapter_wise_distribution': {
                str(ch_id): [q.to_dict() for q in questions] 
                for ch_id, questions in generated_test['chapter_wise_distribution'].items()
            }
        }
    
    @staticmethod
    def calculate_attempt_analytics(attempt_id: int) -> Dict:
        """
        Calculate comprehensive analytics for a mock test attempt
        """
        attempt = UGCNetMockAttempt.query.get(attempt_id)
        if not attempt:
            raise ValueError(f"Attempt {attempt_id} not found")
        
        if not attempt.is_completed:
            return {'error': 'Attempt not completed yet'}
        
        questions_data = attempt.get_questions_data()
        user_answers = attempt.get_answers()
        
        # Chapter-wise performance analysis
        chapter_performance = {}
        strength_areas = []
        weakness_areas = []
        
        for question_data in questions_data:
            chapter_id = question_data['chapter_id']
            question_id = str(question_data['question_id'])
            
            if chapter_id not in chapter_performance:
                chapter_performance[chapter_id] = {
                    'total_questions': 0,
                    'correct_answers': 0,
                    'total_marks': 0,
                    'marks_obtained': 0
                }
            
            chapter_performance[chapter_id]['total_questions'] += 1
            chapter_performance[chapter_id]['total_marks'] += question_data['marks']
            
            # Check if answer is correct
            question = QuestionBank.query.get(question_data['question_id'])
            if question and question_id in user_answers:
                if user_answers[question_id].upper() == question.correct_option:
                    chapter_performance[chapter_id]['correct_answers'] += 1
                    chapter_performance[chapter_id]['marks_obtained'] += question_data['marks']
        
        # Calculate percentages and identify strengths/weaknesses
        for chapter_id, performance in chapter_performance.items():
            if performance['total_questions'] > 0:
                performance['accuracy'] = (performance['correct_answers'] / performance['total_questions']) * 100
                performance['marks_percentage'] = (performance['marks_obtained'] / performance['total_marks']) * 100
                
                chapter = Chapter.query.get(chapter_id)
                chapter_name = chapter.name if chapter else f"Chapter {chapter_id}"
                
                if performance['accuracy'] >= 70:
                    strength_areas.append(chapter_name)
                elif performance['accuracy'] < 50:
                    weakness_areas.append(chapter_name)
        
        # Generate study recommendations
        study_plan = UGCNetMockTestService.generate_study_recommendations(
            chapter_performance, weakness_areas, attempt.mock_test.subject_id
        )
        
        # Update attempt with analytics
        attempt.set_chapter_performance(chapter_performance)
        attempt.set_strength_areas(strength_areas)
        attempt.set_weakness_areas(weakness_areas)
        attempt.set_study_plan(study_plan)
        
        db.session.commit()
        
        return {
            'attempt_id': attempt_id,
            'overall_score': attempt.score,
            'overall_percentage': attempt.percentage,
            'total_marks': attempt.total_marks,
            'time_taken': attempt.time_taken,
            'chapter_performance': chapter_performance,
            'strength_areas': strength_areas,
            'weakness_areas': weakness_areas,
            'study_plan': study_plan
        }
    
    @staticmethod
    def generate_study_recommendations(
        chapter_performance: Dict,
        weakness_areas: List[str],
        subject_id: int
    ) -> Dict:
        """
        Generate personalized study recommendations based on performance
        """
        recommendations = {
            'priority_chapters': [],
            'suggested_daily_time': {},
            'practice_focus': [],
            'estimated_improvement_time': '2-3 weeks'
        }
        
        # Sort chapters by performance (worst first)
        sorted_performance = sorted(
            chapter_performance.items(),
            key=lambda x: x[1].get('accuracy', 0)
        )
        
        for chapter_id, performance in sorted_performance:
            chapter = Chapter.query.get(chapter_id)
            if not chapter:
                continue
            
            if performance.get('accuracy', 0) < 60:
                priority_level = 'high' if performance['accuracy'] < 40 else 'medium'
                recommendations['priority_chapters'].append({
                    'chapter_name': chapter.name,
                    'current_accuracy': performance['accuracy'],
                    'priority': priority_level,
                    'suggested_time_per_day': 45 if priority_level == 'high' else 30
                })
        
        # Focus areas
        if len(weakness_areas) > 3:
            recommendations['practice_focus'] = [
                'Focus on fundamental concepts',
                'Practice more previous year questions',
                'Take chapter-wise mini tests'
            ]
        else:
            recommendations['practice_focus'] = [
                'Revision of weak topics',
                'Mixed practice tests',
                'Time management improvement'
            ]
        
        return recommendations


def create_sample_mock_tests():
    """Create sample UGC NET mock tests for testing"""
    from app.models import User, Subject
    
    # Get admin user
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        print("No admin user found. Create admin first.")
        return
    
    # Get UGC NET subjects
    paper1_subject = Subject.query.filter_by(subject_code='P1').first()
    cs_subject = Subject.query.filter_by(subject_code='CS').first()
    
    if not paper1_subject or not cs_subject:
        print("UGC NET subjects not found. Run seed_ugc_net_subjects() first.")
        return
    
    # Create sample mock tests
    mock_tests = [
        {
            'title': 'UGC NET Paper 1 - Teaching & Research Aptitude Mock Test 1',
            'subject_id': paper1_subject.id,
            'paper_type': 'paper1',
            'description': 'Comprehensive mock test covering all Paper 1 topics',
            'total_questions': 50,
            'time_limit': 60
        },
        {
            'title': 'UGC NET Computer Science Paper 2 - Mock Test 1',
            'subject_id': cs_subject.id,
            'paper_type': 'paper2',
            'description': 'Complete Computer Science Paper 2 mock test with proper weightage',
            'total_questions': 50,
            'time_limit': 120
        }
    ]
    
    for test_data in mock_tests:
        existing_test = UGCNetMockTest.query.filter_by(title=test_data['title']).first()
        if existing_test:
            print(f"Mock test '{test_data['title']}' already exists")
            continue
        
        mock_test = UGCNetMockTestService.create_mock_test(
            title=test_data['title'],
            subject_id=test_data['subject_id'],
            paper_type=test_data['paper_type'],
            created_by_user_id=admin.id,
            description=test_data['description'],
            total_questions=test_data['total_questions'],
            time_limit=test_data['time_limit']
        )
        
        print(f"✅ Created mock test: {mock_test.title}")
    
    print("🎯 Sample UGC NET mock tests created successfully!")


if __name__ == '__main__':
    # Test the service
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        create_sample_mock_tests()
