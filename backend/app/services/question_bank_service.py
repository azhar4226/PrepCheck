"""
Question Bank Service for managing AI-generated and verified questions
"""
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple

from app import db
from app.models import QuestionBank, User, QuestionPerformance
from sqlalchemy import and_, or_, func


class QuestionBankService:
    """Service for managing the question bank functionality"""
    
    @staticmethod
    def generate_content_hash(question_text: str, options: Dict[str, str], correct_option: str) -> str:
        """Generate a unique hash for question content to detect duplicates"""
        content = f"{question_text.strip().lower()}{options['A'].strip().lower()}{options['B'].strip().lower()}{options['C'].strip().lower()}{options['D'].strip().lower()}{correct_option}"
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def check_duplicate(question_text: str, options: Dict[str, str], correct_option: str) -> Optional[QuestionBank]:
        """Check if a question already exists in the question bank"""
        content_hash = QuestionBankService.generate_content_hash(question_text, options, correct_option)
        return QuestionBank.query.filter_by(content_hash=content_hash).first()
    
    @staticmethod
    def store_ai_question(
        question_data: Dict,
        topic: str,
        difficulty: str,
        chapter_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        verification_data: Optional[Dict] = None
    ) -> Tuple[QuestionBank, bool]:
        """
        Store an AI-generated question in the question bank
        Returns (question_bank_entry, is_new)
        """
        
        # Extract question data
        question_text = question_data['question']
        options = question_data['options']
        correct_option = question_data['correct_answer']
        explanation = question_data.get('explanation', '')
        marks = question_data.get('marks', 1)
        
        # Check for duplicates
        existing_question = QuestionBankService.check_duplicate(question_text, options, correct_option)
        if existing_question:
            # Update usage metadata for existing question
            existing_question.increment_usage()
            db.session.commit()
            return existing_question, False
        
        # Create new question bank entry
        content_hash = QuestionBankService.generate_content_hash(question_text, options, correct_option)
        
        question_bank_entry = QuestionBank(
            question_text=question_text,
            option_a=options['A'],
            option_b=options['B'],
            option_c=options['C'],
            option_d=options['D'],
            correct_option=correct_option,
            explanation=explanation,
            marks=marks,
            topic=topic,
            difficulty=difficulty.lower(),
            source='ai_generated',
            chapter_id=chapter_id,
            content_hash=content_hash,
            usage_count=1,
            last_used=datetime.utcnow()
        )
        
        # Set tags if provided
        if tags:
            question_bank_entry.set_tags(tags)
        
        # Apply verification data if provided
        if verification_data and verification_data.get('is_verified'):
            question_bank_entry.mark_verified(
                method='gemini',
                confidence=verification_data.get('confidence', 0.8),
                verified_by_user_id=verification_data.get('verified_by'),
                notes=verification_data.get('notes')
            )
        
        try:
            db.session.add(question_bank_entry)
            db.session.commit()
            return question_bank_entry, True
        except Exception as e:
            db.session.rollback()
            raise e
    
    @staticmethod
    def bulk_store_ai_questions(
        questions_data: List[Dict],
        topic: str,
        difficulty: str,
        chapter_id: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """
        Bulk store multiple AI-generated questions
        Returns summary of storage operation
        """
        results = {
            'total_questions': len(questions_data),
            'new_questions': 0,
            'duplicate_questions': 0,
            'failed_questions': 0,
            'stored_question_ids': [],
            'duplicate_question_ids': [],
            'errors': []
        }
        
        for i, question_data in enumerate(questions_data):
            try:
                question_bank_entry, is_new = QuestionBankService.store_ai_question(
                    question_data=question_data,
                    topic=topic,
                    difficulty=difficulty,
                    chapter_id=chapter_id,
                    tags=tags
                )
                
                if is_new:
                    results['new_questions'] += 1
                    results['stored_question_ids'].append(question_bank_entry.id)
                else:
                    results['duplicate_questions'] += 1
                    results['duplicate_question_ids'].append(question_bank_entry.id)
                    
            except Exception as e:
                results['failed_questions'] += 1
                results['errors'].append({
                    'question_index': i,
                    'question_text': question_data.get('question', 'Unknown'),
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def verify_question(
        question_bank_id: int,
        verification_method: str,
        confidence: float,
        verified_by_user_id: int,
        notes: Optional[str] = None
    ) -> bool:
        """Verify a question in the question bank"""
        try:
            question = QuestionBank.query.get(question_bank_id)
            if not question:
                return False
            
            question.mark_verified(verification_method, confidence, verified_by_user_id, notes)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @staticmethod
    def search_questions(
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        verified_only: bool = True,
        chapter_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[QuestionBank]:
        """Search questions in the question bank with filters"""
        query = QuestionBank.query
        
        if verified_only:
            query = query.filter_by(is_verified=True)
        
        if topic:
            query = query.filter(QuestionBank.topic.ilike(f'%{topic}%'))
        
        if difficulty:
            query = query.filter_by(difficulty=difficulty.lower())
        
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
        
        if tags:
            # Search for questions that have any of the specified tags
            # For simple text search in JSON field
            tag_filters = []
            for tag in tags:
                tag_filters.append(func.json_extract(QuestionBank.tags, f'$[*]').like(f'%{tag}%'))
            if tag_filters:
                query = query.filter(or_(*tag_filters))
        
        # Order by least used first, then by newest
        query = query.order_by(QuestionBank.usage_count.asc(), QuestionBank.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_questions_for_quiz(
        topic: str,
        difficulty: str,
        num_questions: int,
        chapter_id: Optional[int] = None,
        exclude_recent_usage_hours: int = 24
    ) -> List[QuestionBank]:
        """
        Get questions from question bank for creating a new quiz
        Prioritizes verified questions and avoids recently used ones
        """
        from datetime import timedelta
        
        query = QuestionBank.query.filter_by(
            is_verified=True,
            difficulty=difficulty.lower()
        ).filter(
            QuestionBank.topic.ilike(f'%{topic}%')
        )
        
        if chapter_id:
            query = query.filter_by(chapter_id=chapter_id)
        
        # Exclude recently used questions (simplified approach)
        cutoff_time = datetime.utcnow() - timedelta(hours=exclude_recent_usage_hours)
        
        # Order by usage count (least used first), then by verification confidence
        query = query.order_by(
            QuestionBank.usage_count.asc(),
            QuestionBank.verification_confidence.desc(),
            QuestionBank.created_at.desc()
        )
        
        # Get all available questions and filter in Python for simplicity
        all_questions = query.all()
        available_questions = []
        
        for question in all_questions:
            if question.last_used is None or question.last_used < cutoff_time:
                available_questions.append(question)
                if len(available_questions) >= num_questions:
                    break
        
        return available_questions[:num_questions]
    
    @staticmethod
    def get_question_bank_stats() -> Dict:
        """Get statistics about the question bank"""
        total_questions = QuestionBank.query.count()
        verified_questions = QuestionBank.query.filter_by(is_verified=True).count()
        unverified_questions = total_questions - verified_questions
        
        # Get breakdown by difficulty
        difficulty_stats = db.session.query(
            QuestionBank.difficulty,
            func.count(QuestionBank.id).label('count')
        ).group_by(QuestionBank.difficulty).all()
        
        # Get breakdown by topic (top 10)
        topic_stats = db.session.query(
            QuestionBank.topic,
            func.count(QuestionBank.id).label('count')
        ).group_by(QuestionBank.topic).order_by(
            func.count(QuestionBank.id).desc()
        ).limit(10).all()
        
        return {
            'total_questions': total_questions,
            'verified_questions': verified_questions,
            'unverified_questions': unverified_questions,
            'verification_rate': round((verified_questions / total_questions * 100), 2) if total_questions > 0 else 0,
            'difficulty_breakdown': [{'difficulty': d[0], 'count': d[1]} for d in difficulty_stats],
            'top_topics': [{'topic': t[0], 'count': t[1]} for t in topic_stats]
        }
    
    @staticmethod
    def record_question_performance(
        question_bank_id: int,
        quiz_attempt_id: int,
        user_id: int,
        is_correct: bool,
        selected_option: str,
        time_taken: Optional[int] = None,
        question_position: Optional[int] = None,
        quiz_difficulty: Optional[str] = None,
        quiz_topic: Optional[str] = None
    ) -> QuestionPerformance:
        """Record performance data for a question"""
        
        performance = QuestionPerformance(
            question_bank_id=question_bank_id,
            quiz_attempt_id=quiz_attempt_id,
            user_id=user_id,
            is_correct=is_correct,
            selected_option=selected_option,
            time_taken=time_taken,
            question_position=question_position,
            quiz_difficulty=quiz_difficulty,
            quiz_topic=quiz_topic
        )
        
        db.session.add(performance)
        
        # Update question bank usage statistics
        question = QuestionBank.query.get(question_bank_id)
        if question:
            question.increment_usage()
        
        db.session.commit()
        return performance
    
    @staticmethod
    def get_performance_analytics(
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        days: int = 30,
        min_attempts: int = 1
    ) -> Dict:
        """Get comprehensive performance analytics"""
        
        from datetime import timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Base query for performance data
        query = db.session.query(QuestionPerformance).join(QuestionBank)
        
        # Apply filters
        if topic:
            query = query.filter(QuestionBank.topic.ilike(f'%{topic}%'))
        if difficulty:
            query = query.filter(QuestionBank.difficulty == difficulty)
        
        query = query.filter(QuestionPerformance.answered_at >= start_date)
        
        # Get performance metrics
        performances = query.all()
        
        if not performances:
            return {
                'total_questions': 0,
                'total_attempts': 0,
                'overall_success_rate': 0,
                'average_time': 0,
                'top_performers': [],
                'worst_performers': [],
                'daily_usage': [],
                'difficulty_breakdown': {},
                'topic_breakdown': {}
            }
        
        # Calculate metrics
        total_attempts = len(performances)
        correct_attempts = sum(1 for p in performances if p.is_correct)
        overall_success_rate = (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0
        
        # Average time calculation
        times = [p.time_taken for p in performances if p.time_taken]
        average_time = sum(times) / len(times) if times else 0
        
        # Get question-level analytics
        question_stats = {}
        for perf in performances:
            qid = perf.question_bank_id
            if qid not in question_stats:
                question_stats[qid] = {
                    'question': perf.question_bank,
                    'attempts': 0,
                    'correct': 0,
                    'total_time': 0,
                    'time_count': 0
                }
            
            stats = question_stats[qid]
            stats['attempts'] += 1
            if perf.is_correct:
                stats['correct'] += 1
            if perf.time_taken:
                stats['total_time'] += perf.time_taken
                stats['time_count'] += 1
        
        # Calculate success rates and identify top/worst performers
        question_analytics = []
        for qid, stats in question_stats.items():
            success_rate = (stats['correct'] / stats['attempts']) * 100
            avg_time = stats['total_time'] / stats['time_count'] if stats['time_count'] > 0 else 0
            
            if stats['attempts'] >= min_attempts:  # Only include questions with minimum attempts
                question_analytics.append({
                    'question_id': qid,
                    'question_text': stats['question'].question_text[:100] + '...' if len(stats['question'].question_text) > 100 else stats['question'].question_text,
                    'topic': stats['question'].topic,
                    'difficulty': stats['question'].difficulty,
                    'attempts': stats['attempts'],
                    'success_rate': round(success_rate, 2),
                    'average_time': round(avg_time, 1)
                })
        
        # Sort for top and worst performers
        question_analytics.sort(key=lambda x: x['success_rate'], reverse=True)
        top_performers = question_analytics[:5]
        worst_performers = question_analytics[-5:] if len(question_analytics) > 5 else []
        
        # Daily usage trends
        daily_usage = {}
        for perf in performances:
            date_str = perf.answered_at.date().isoformat()
            daily_usage[date_str] = daily_usage.get(date_str, 0) + 1
        
        daily_usage_list = [{'date': date, 'count': count} for date, count in sorted(daily_usage.items())]
        
        # Difficulty breakdown
        difficulty_breakdown = {}
        for perf in performances:
            diff = perf.question_bank.difficulty
            if diff not in difficulty_breakdown:
                difficulty_breakdown[diff] = {'attempts': 0, 'correct': 0}
            difficulty_breakdown[diff]['attempts'] += 1
            if perf.is_correct:
                difficulty_breakdown[diff]['correct'] += 1
        
        # Add success rates to difficulty breakdown
        for diff, stats in difficulty_breakdown.items():
            stats['success_rate'] = round((stats['correct'] / stats['attempts']) * 100, 2) if stats['attempts'] > 0 else 0
        
        # Topic breakdown
        topic_breakdown = {}
        for perf in performances:
            topic = perf.question_bank.topic
            if topic not in topic_breakdown:
                topic_breakdown[topic] = {'attempts': 0, 'correct': 0}
            topic_breakdown[topic]['attempts'] += 1
            if perf.is_correct:
                topic_breakdown[topic]['correct'] += 1
        
        # Add success rates to topic breakdown
        for topic, stats in topic_breakdown.items():
            stats['success_rate'] = round((stats['correct'] / stats['attempts']) * 100, 2) if stats['attempts'] > 0 else 0
        
        return {
            'total_questions': len(question_stats),
            'total_attempts': total_attempts,
            'overall_success_rate': round(overall_success_rate, 2),
            'average_time': round(average_time, 1),
            'top_performers': top_performers,
            'worst_performers': worst_performers,
            'daily_usage': daily_usage_list,
            'difficulty_breakdown': difficulty_breakdown,
            'topic_breakdown': topic_breakdown,
            'period_days': days
        }
    
    @staticmethod
    def get_detailed_analytics(
        days: int = 30,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Dict:
        """Get comprehensive analytics for the question bank dashboard"""
        from datetime import timedelta
        
        # Get basic overview
        overview_stats = QuestionBankService.get_question_bank_stats()
        
        # Get performance analytics
        performance_analytics = QuestionBankService.get_performance_analytics(
            topic=topic,
            difficulty=difficulty,
            days=days
        )
        
        # Combine overview with performance data
        overview = {
            'total_questions': overview_stats['total_questions'],
            'verified_questions': overview_stats['verified_questions'],
            'avg_success_rate': performance_analytics['overall_success_rate'],
            'avg_response_time': performance_analytics['average_time'],
            'total_usage': performance_analytics['total_attempts'],
            'student_attempts': performance_analytics['total_attempts']  # Same for now
        }
        
        # Get usage trends
        usage_trends = QuestionBankService.get_usage_trends(days=days)
        
        # Get questions that need review based on performance
        questions_needing_review = []
        questions = QuestionBank.query.filter_by(is_verified=True).all()
        for question in questions:
            stats = question.get_performance_stats()
            if stats['total_attempts'] >= 10 and stats['success_rate'] <= 60:
                questions_needing_review.append({
                    'id': question.id,
                    'question_text': question.question_text[:100] + '...' if len(question.question_text) > 100 else question.question_text,
                    'topic': question.topic,
                    'difficulty': question.difficulty,
                    'success_rate': stats['success_rate'],
                    'total_attempts': stats['total_attempts']
                })
        
        # Get top performing questions
        top_questions = {
            'most_answered': performance_analytics['top_performers'][:10],
            'highest_success': performance_analytics['top_performers'][:10],
            'needs_review': questions_needing_review[:10]
        }
        
        # Generate insights
        insights = []
        if performance_analytics['overall_success_rate'] < 70:
            insights.append({
                'type': 'warning',
                'message': f'Overall success rate ({performance_analytics["overall_success_rate"]:.1f}%) is below target (70%)',
                'suggestion': 'Review questions with low success rates and consider revising'
            })
        
        if overview_stats['verification_rate'] < 80:
            insights.append({
                'type': 'info',
                'message': f'Verification rate ({overview_stats["verification_rate"]:.1f}%) could be improved',
                'suggestion': 'Prioritize verifying unverified questions'
            })
        
        if len(questions_needing_review) > 0:
            insights.append({
                'type': 'action',
                'message': f'{len(questions_needing_review)} questions may need review based on performance',
                'suggestion': 'Review poorly performing questions for accuracy'
            })
        
        # Get recommendations
        total_questions = QuestionBank.query.count()
        verified_questions = QuestionBank.query.filter_by(is_verified=True).count()
        
        recommendations = []
        if verified_questions / total_questions < 0.8 if total_questions > 0 else False:
            recommendations.append({
                'type': 'verification',
                'priority': 'high',
                'message': f'Only {verified_questions} out of {total_questions} questions are verified.',
                'action': 'Review and verify pending questions'
            })
        
        recommendations_data = {'recommendations': recommendations}
        
        return {
            'overview': overview,
            'trends': usage_trends,
            'performance': performance_analytics,
            'topQuestions': top_questions,
            'insights': insights,
            'recommendations': recommendations_data['recommendations']
        }
    
    @staticmethod
    def get_question_performance_analytics(question_id: int) -> Dict:
        """Get detailed performance analytics for a specific question"""
        question = QuestionBank.query.get(question_id)
        if not question:
            return {'error': 'Question not found'}
        
        # Get basic question info
        question_info = question.to_dict(include_answer=True)
        
        # Get performance stats
        performance_stats = question.get_performance_stats()
        
        # Get usage trends for this question
        usage_trends = question.get_usage_trends(days=90)
        
        # Get detailed performance breakdown
        performances = QuestionPerformance.query.filter_by(question_bank_id=question_id).all()
        
        # Analyze answer distribution
        answer_distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
        time_distribution = []
        
        for perf in performances:
            answer_distribution[perf.selected_option] += 1
            if perf.time_taken:
                time_distribution.append(perf.time_taken)
        
        # Calculate percentiles for time
        if time_distribution:
            time_distribution.sort()
            n = len(time_distribution)
            time_percentiles = {
                'p25': time_distribution[n//4] if n > 0 else 0,
                'p50': time_distribution[n//2] if n > 0 else 0,
                'p75': time_distribution[3*n//4] if n > 0 else 0,
                'p90': time_distribution[9*n//10] if n > 0 else 0
            }
        else:
            time_percentiles = {'p25': 0, 'p50': 0, 'p75': 0, 'p90': 0}
        
        return {
            'question': question_info,
            'performance': performance_stats,
            'usage_trends': usage_trends,
            'answer_distribution': answer_distribution,
            'time_analysis': {
                'distribution': time_distribution[:100],  # Limit to first 100 for visualization
                'percentiles': time_percentiles
            },
            'recommendations': [
                {
                    'type': 'performance',
                    'message': f'Question has {performance_stats["success_rate"]:.1f}% success rate',
                    'action': 'Monitor' if performance_stats['success_rate'] > 60 else 'Review question accuracy'
                }
            ]
        }
    
    @staticmethod
    def get_usage_trends(days: int = 30) -> Dict:
        """Get usage trends over specified time period"""
        from datetime import timedelta, date
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get daily question bank usage
        daily_usage = db.session.query(
            func.date(QuestionPerformance.answered_at).label('date'),
            func.count(QuestionPerformance.id).label('attempts'),
            func.count(func.distinct(QuestionPerformance.question_bank_id)).label('unique_questions'),
            func.avg(func.cast(QuestionPerformance.is_correct, db.Integer)).label('success_rate')
        ).filter(
            QuestionPerformance.answered_at >= start_date,
            QuestionPerformance.answered_at <= end_date
        ).group_by(func.date(QuestionPerformance.answered_at)).all()
        
        # Fill in missing dates with zero values
        trends_data = []
        current_date = start_date.date()
        usage_dict = {usage.date: usage for usage in daily_usage}
        
        while current_date <= end_date.date():
            if current_date in usage_dict:
                usage = usage_dict[current_date]
                trends_data.append({
                    'date': current_date.isoformat(),
                    'attempts': usage.attempts,
                    'unique_questions': usage.unique_questions,
                    'success_rate': round(float(usage.success_rate) * 100, 2) if usage.success_rate else 0
                })
            else:
                trends_data.append({
                    'date': current_date.isoformat(),
                    'attempts': 0,
                    'unique_questions': 0,
                    'success_rate': 0
                })
            current_date += timedelta(days=1)
        
        # Calculate weekly and monthly aggregates
        weekly_aggregates = []
        monthly_aggregates = []
        
        # Simple weekly aggregation (last 4 weeks)
        for i in range(0, min(len(trends_data), 28), 7):
            week_data = trends_data[i:i+7]
            weekly_aggregates.append({
                'week': f'Week {len(weekly_aggregates) + 1}',
                'total_attempts': sum(d['attempts'] for d in week_data),
                'avg_success_rate': sum(d['success_rate'] for d in week_data) / len(week_data) if week_data else 0
            })
        
        return {
            'daily': trends_data,
            'weekly': weekly_aggregates,
            'period_days': days,
            'summary': {
                'total_attempts': sum(d['attempts'] for d in trends_data),
                'avg_daily_attempts': sum(d['attempts'] for d in trends_data) / days,
                'peak_day': max(trends_data, key=lambda x: x['attempts'])['date'] if trends_data else None,
                'avg_success_rate': sum(d['success_rate'] for d in trends_data) / len(trends_data) if trends_data else 0
            }
        }
    
    @staticmethod
    def get_improvement_recommendations() -> Dict:
        """Get AI-driven recommendations for question bank improvements"""
        # Get base data for recommendations
        total_questions = QuestionBank.query.count()
        verified_questions = QuestionBank.query.filter_by(is_verified=True).count()
        verification_rate = (verified_questions / total_questions) * 100 if total_questions > 0 else 0
        
        base_recommendations = []
        if verification_rate < 80:
            base_recommendations.append({
                'type': 'verification',
                'priority': 'high',
                'message': f'Only {verification_rate:.1f}% of questions are verified.',
                'action': 'Review and verify pending questions'
            })
        
        # Get performance analytics
        performance_data = QuestionBankService.get_performance_analytics(days=30)
        
        # Get questions that need review
        review_questions = []
        questions = QuestionBank.query.filter_by(is_verified=True).all()
        for question in questions:
            stats = question.get_performance_stats()
            if stats['total_attempts'] >= 10 and stats['success_rate'] <= 60:
                review_questions.append({
                    'id': question.id,
                    'success_rate': stats['success_rate'],
                    'total_attempts': stats['total_attempts']
                })
        
        # Enhanced recommendations with AI insights
        ai_recommendations = []
        
        # Content gap analysis
        if len(performance_data['topic_breakdown']) > 0:
            topic_performance = performance_data['topic_breakdown']
            weak_topics = [topic for topic, stats in topic_performance.items() 
                          if stats['success_rate'] < 60 and stats['attempts'] > 5]
            
            for topic in weak_topics:
                ai_recommendations.append({
                    'type': 'content_improvement',
                    'priority': 'high',
                    'category': 'Question Quality',
                    'message': f'Topic "{topic}" shows low success rate ({topic_performance[topic]["success_rate"]:.1f}%)',
                    'action': f'Review and improve questions in "{topic}" topic',
                    'impact': 'High - will improve student learning outcomes',
                    'effort': 'Medium - requires expert review'
                })
        
        # Difficulty balance analysis
        if len(performance_data['difficulty_breakdown']) > 0:
            diff_data = performance_data['difficulty_breakdown']
            total_attempts = sum(stats['attempts'] for stats in diff_data.values())
            
            for difficulty, stats in diff_data.items():
                percentage = (stats['attempts'] / total_attempts) * 100 if total_attempts > 0 else 0
                
                if percentage < 20:  # Less than 20% of questions
                    ai_recommendations.append({
                        'type': 'content_balance',
                        'priority': 'medium',
                        'category': 'Content Distribution',
                        'message': f'Only {percentage:.1f}% of questions are {difficulty} difficulty',
                        'action': f'Generate more {difficulty} difficulty questions',
                        'impact': 'Medium - will provide better difficulty balance',
                        'effort': 'Low - can be automated'
                    })
        
        # Usage optimization
        if performance_data['total_attempts'] > 0:
            avg_time = performance_data['average_time']
            if avg_time > 90:  # More than 90 seconds average
                ai_recommendations.append({
                    'type': 'performance_optimization',
                    'priority': 'medium',
                    'category': 'User Experience',
                    'message': f'Average response time ({avg_time:.1f}s) is high',
                    'action': 'Review question complexity and clarity',
                    'impact': 'Medium - will improve user experience',
                    'effort': 'Medium - requires question review'
                })
        
        # Verification recommendations
        if verification_rate < 90:
            ai_recommendations.append({
                'type': 'quality_assurance',
                'priority': 'high',
                'category': 'Quality Control',
                'message': f'Verification rate ({verification_rate:.1f}%) needs improvement',
                'action': 'Implement automated verification for AI-generated questions',
                'impact': 'High - ensures question quality',
                'effort': 'Low - can be automated'
            })
        
        # Combine all recommendations
        all_recommendations = base_recommendations + ai_recommendations
        
        # Sort by priority
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        all_recommendations.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return {
            'recommendations': all_recommendations,
            'summary': {
                'total_recommendations': len(all_recommendations),
                'high_priority': len([r for r in all_recommendations if r['priority'] == 'high']),
                'medium_priority': len([r for r in all_recommendations if r['priority'] == 'medium']),
                'low_priority': len([r for r in all_recommendations if r['priority'] == 'low'])
            },
            'categories': {
                'Quality Control': len([r for r in all_recommendations if r.get('category') == 'Quality Control']),
                'Content Distribution': len([r for r in all_recommendations if r.get('category') == 'Content Distribution']),
                'Question Quality': len([r for r in all_recommendations if r.get('category') == 'Question Quality']),
                'User Experience': len([r for r in all_recommendations if r.get('category') == 'User Experience'])
            }
        }
    
    @staticmethod
    def find_question_in_bank(
        question_text: str,
        options: Dict[str, str],
        correct_option: str
    ) -> Optional[QuestionBank]:
        """Find a question in the bank by content match"""
        content_hash = QuestionBankService.generate_content_hash(question_text, options, correct_option)
        return QuestionBank.query.filter_by(content_hash=content_hash).first()

    @staticmethod
    def get_user_question_analytics(user_id: int, days: int = 30) -> Dict:
        """Get user-specific question analytics from the question bank"""
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get user's question performance data
        user_performance = db.session.query(
            QuestionPerformance
        ).filter(
            QuestionPerformance.user_id == user_id,
            QuestionPerformance.answered_at >= start_date,
            QuestionPerformance.answered_at <= end_date
        ).all()
        
        if not user_performance:
            return {
                'total_questions_answered': 0,
                'correct_answers': 0,
                'accuracy_rate': 0,
                'most_difficult_topics': [],
                'strongest_topics': [],
                'question_types_breakdown': {},
                'improvement_suggestions': []
            }
        
        # Calculate basic stats
        total_answered = len(user_performance)
        correct_answers = sum(1 for p in user_performance if p.is_correct)
        accuracy_rate = (correct_answers / total_answered * 100) if total_answered > 0 else 0
        
        # Group by topic/difficulty to find patterns
        topic_performance = {}
        difficulty_performance = {}
        
        for performance in user_performance:
            question = performance.question_bank
            if question:
                # Track topic performance
                topic = question.topic or 'Unknown'
                if topic not in topic_performance:
                    topic_performance[topic] = {'total': 0, 'correct': 0}
                topic_performance[topic]['total'] += 1
                if performance.is_correct:
                    topic_performance[topic]['correct'] += 1
                
                # Track difficulty performance
                difficulty = question.difficulty or 'Unknown'
                if difficulty not in difficulty_performance:
                    difficulty_performance[difficulty] = {'total': 0, 'correct': 0}
                difficulty_performance[difficulty]['total'] += 1
                if performance.is_correct:
                    difficulty_performance[difficulty]['correct'] += 1
        
        # Calculate topic percentages and sort
        topic_scores = []
        for topic, data in topic_performance.items():
            percentage = (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0
            topic_scores.append({
                'topic': topic,
                'accuracy': round(percentage, 2),
                'questions_answered': data['total'],
                'correct_answers': data['correct']
            })
        
        topic_scores.sort(key=lambda x: x['accuracy'])
        
        # Most difficult (lowest accuracy) and strongest (highest accuracy) topics
        most_difficult = topic_scores[:3] if len(topic_scores) >= 3 else topic_scores
        strongest = topic_scores[-3:] if len(topic_scores) >= 3 else []
        strongest.reverse()  # Highest first
        
        # Question types breakdown by difficulty
        difficulty_breakdown = {}
        for difficulty, data in difficulty_performance.items():
            percentage = (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0
            difficulty_breakdown[difficulty] = {
                'accuracy': round(percentage, 2),
                'questions_answered': data['total'],
                'correct_answers': data['correct']
            }
        
        # Generate improvement suggestions based on performance
        suggestions = []
        
        # Suggest focusing on difficult topics
        if most_difficult:
            worst_topic = most_difficult[0]
            if worst_topic['accuracy'] < 60:
                suggestions.append({
                    'type': 'topic_improvement',
                    'message': f"Focus on improving {worst_topic['topic']} - current accuracy: {worst_topic['accuracy']}%",
                    'priority': 'high'
                })
        
        # Suggest difficulty level adjustments
        if 'Hard' in difficulty_breakdown and difficulty_breakdown['Hard']['accuracy'] < 40:
            suggestions.append({
                'type': 'difficulty_adjustment',
                'message': "Consider practicing more medium-level questions before attempting hard questions",
                'priority': 'medium'
            })
        
        # Suggest practice frequency if low activity
        if total_answered < 10:
            suggestions.append({
                'type': 'practice_frequency',
                'message': "Increase practice frequency - aim for at least 10 questions per week",
                'priority': 'medium'
            })
        
        return {
            'total_questions_answered': total_answered,
            'correct_answers': correct_answers,
            'accuracy_rate': round(accuracy_rate, 2),
            'most_difficult_topics': most_difficult,
            'strongest_topics': strongest,
            'question_types_breakdown': difficulty_breakdown,
            'improvement_suggestions': suggestions,
            'period_days': days
        }
