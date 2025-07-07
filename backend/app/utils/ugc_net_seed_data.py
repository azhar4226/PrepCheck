"""
UGC NET Subject Structure and Seed Data
This module contains the official UGC NET syllabus structure with proper weightages
"""

from app import db
from app.models import Subject, Chapter
import os


# UGC NET Paper 1 Structure (Common for all subjects)
PAPER_1_STRUCTURE = {
    'name': 'UGC NET Paper 1 - Teaching & Research Aptitude',
    'subject_code': 'P1',
    'paper_type': 'paper1',
    'total_marks_paper1': 100,
    'exam_duration_paper1': 60,
    'chapters': [
        {
            'name': 'Teaching Aptitude',
            'description': 'Teaching: Nature, objectives, characteristics and basic requirements. Learner\'s characteristics.',
            'weightage_paper1': 15,
            'estimated_questions_paper1': 5,
            'chapter_order': 1
        },
        {
            'name': 'Research Aptitude',
            'description': 'Research: Meaning, types, and characteristics, Positivism and post-positivism approach to research.',
            'weightage_paper1': 15,
            'estimated_questions_paper1': 5,
            'chapter_order': 2
        },
        {
            'name': 'Reading Comprehension',
            'description': 'Comprehension of unseen passages - focus on understanding, analysis and interpretation.',
            'weightage_paper1': 15,
            'estimated_questions_paper1': 5,
            'chapter_order': 3
        },
        {
            'name': 'Communication',
            'description': 'Communication: Nature, characteristics, types, barriers and effective use in teaching.',
            'weightage_paper1': 10,
            'estimated_questions_paper1': 3,
            'chapter_order': 4
        },
        {
            'name': 'Mathematical Reasoning and Aptitude',
            'description': 'Number series, Letter series, Codes and Relationships, Mathematical Aptitude.',
            'weightage_paper1': 10,
            'estimated_questions_paper1': 3,
            'chapter_order': 5
        },
        {
            'name': 'Logical Reasoning',
            'description': 'Understanding the structure of arguments: Evaluating and distinguishing deductive and inductive reasoning.',
            'weightage_paper1': 10,
            'estimated_questions_paper1': 3,
            'chapter_order': 6
        },
        {
            'name': 'Data Interpretation',
            'description': 'Sources, acquisition and interpretation of data - Quantitative and Qualitative data.',
            'weightage_paper1': 10,
            'estimated_questions_paper1': 3,
            'chapter_order': 7
        },
        {
            'name': 'Information and Communication Technology (ICT)',
            'description': 'ICT: General abbreviations and terminology. Basics of Internet and e-mail.',
            'weightage_paper1': 10,
            'estimated_questions_paper1': 3,
            'chapter_order': 8
        },
        {
            'name': 'People, Development and Environment',
            'description': 'Development and environment ecology and climate change including disaster and disaster management.',
            'weightage_paper1': 5,
            'estimated_questions_paper1': 2,
            'chapter_order': 9
        },
        {
            'name': 'Higher Education System',
            'description': 'Institutions of higher learning and education in ancient India and their contribution.',
            'weightage_paper1': 0,  # Combined with other topics
            'estimated_questions_paper1': 3,
            'chapter_order': 10
        }
    ]
}

# UGC NET Computer Science Paper 2 Structure (Example subject)
COMPUTER_SCIENCE_STRUCTURE = {
    'name': 'Computer Science and Applications',
    'subject_code': 'CS',
    'paper_type': 'paper2',
    'total_marks_paper2': 100,
    'exam_duration_paper2': 120,
    'chapters': [
        {
            'name': 'Discrete Mathematics and Graph Theory',
            'description': 'Sets, Relations, Functions, Mathematical Logic, Combinatorics, Graph Theory',
            'weightage_paper2': 15,
            'estimated_questions_paper2': 8,
            'chapter_order': 1
        },
        {
            'name': 'Computer System Architecture',
            'description': 'Digital Logic, Computer Organization, Memory Systems, I/O Systems',
            'weightage_paper2': 12,
            'estimated_questions_paper2': 6,
            'chapter_order': 2
        },
        {
            'name': 'Programming and Data Structures',
            'description': 'Programming Languages, Data Structures, Algorithms, Complexity Analysis',
            'weightage_paper2': 18,
            'estimated_questions_paper2': 9,
            'chapter_order': 3
        },
        {
            'name': 'Database Systems',
            'description': 'ER Model, Relational Model, SQL, Normalization, Transaction Management',
            'weightage_paper2': 12,
            'estimated_questions_paper2': 6,
            'chapter_order': 4
        },
        {
            'name': 'Computer Networks',
            'description': 'OSI Model, TCP/IP, Routing, Network Security',
            'weightage_paper2': 10,
            'estimated_questions_paper2': 5,
            'chapter_order': 5
        },
        {
            'name': 'Operating Systems',
            'description': 'Process Management, Memory Management, File Systems, Deadlocks',
            'weightage_paper2': 12,
            'estimated_questions_paper2': 6,
            'chapter_order': 6
        },
        {
            'name': 'Software Engineering',
            'description': 'SDLC, Testing, Design Patterns, Project Management',
            'weightage_paper2': 8,
            'estimated_questions_paper2': 4,
            'chapter_order': 7
        },
        {
            'name': 'Web Technologies',
            'description': 'HTML, CSS, JavaScript, Web Frameworks, Web Services',
            'weightage_paper2': 8,
            'estimated_questions_paper2': 4,
            'chapter_order': 8
        },
        {
            'name': 'Theory of Computation',
            'description': 'Finite Automata, Regular Languages, Context-Free Languages, Turing Machines',
            'weightage_paper2': 5,
            'estimated_questions_paper2': 2,
            'chapter_order': 9
        }
    ]
}

# English Literature Paper 2 Structure
ENGLISH_LITERATURE_STRUCTURE = {
    'name': 'English Literature',
    'subject_code': 'ENG',
    'paper_type': 'paper2',
    'total_marks_paper2': 100,
    'exam_duration_paper2': 120,
    'chapters': [
        {
            'name': 'Old and Middle English Literature',
            'description': 'Beowulf, Chaucer, Medieval Drama, Morality Plays',
            'weightage_paper2': 10,
            'estimated_questions_paper2': 5,
            'chapter_order': 1
        },
        {
            'name': 'Renaissance Literature',
            'description': 'Shakespeare, Marlowe, Spenser, Metaphysical Poetry',
            'weightage_paper2': 15,
            'estimated_questions_paper2': 8,
            'chapter_order': 2
        },
        {
            'name': 'Restoration and 18th Century Literature',
            'description': 'Dryden, Pope, Swift, Johnson, Novel beginnings',
            'weightage_paper2': 12,
            'estimated_questions_paper2': 6,
            'chapter_order': 3
        },
        {
            'name': 'Romantic Literature',
            'description': 'Wordsworth, Coleridge, Byron, Shelley, Keats',
            'weightage_paper2': 12,
            'estimated_questions_paper2': 6,
            'chapter_order': 4
        },
        {
            'name': 'Victorian Literature',
            'description': 'Tennyson, Browning, Victorian Novel, Hardy',
            'weightage_paper2': 15,
            'estimated_questions_paper2': 8,
            'chapter_order': 5
        },
        {
            'name': 'Modern Literature',
            'description': 'Modernist Poetry, Stream of Consciousness, Joyce, Woolf',
            'weightage_paper2': 12,
            'estimated_questions_paper2': 6,
            'chapter_order': 6
        },
        {
            'name': 'Contemporary Literature',
            'description': 'Postmodern Literature, Contemporary Poetry and Drama',
            'weightage_paper2': 10,
            'estimated_questions_paper2': 5,
            'chapter_order': 7
        },
        {
            'name': 'Indian English Literature',
            'description': 'R.K. Narayan, Mulk Raj Anand, Indian Poetry in English',
            'weightage_paper2': 8,
            'estimated_questions_paper2': 4,
            'chapter_order': 8
        },
        {
            'name': 'Literary Theory and Criticism',
            'description': 'Classical Criticism, Modern Critical Theories',
            'weightage_paper2': 6,
            'estimated_questions_paper2': 2,
            'chapter_order': 9
        }
    ]
}

# Psychology Paper 2 Structure
PSYCHOLOGY_STRUCTURE = {
    'name': 'Psychology',
    'subject_code': 'PSY',
    'paper_type': 'paper2',
    'total_marks_paper2': 100,
    'exam_duration_paper2': 120,
    'chapters': [
        {
            'name': 'Foundations of Psychology',
            'description': 'Definition, scope, methods, schools of psychology',
            'weightage_paper2': 10,
            'estimated_questions_paper2': 5,
            'chapter_order': 1
        },
        {
            'name': 'Biological Bases of Behaviour',
            'description': 'Nervous system, Brain functions, Endocrine system',
            'weightage_paper2': 12,
            'estimated_questions_paper2': 6,
            'chapter_order': 2
        },
        {
            'name': 'Sensation and Perception',
            'description': 'Sensory processes, Perceptual organization, Attention',
            'weightage_paper2': 10,
            'estimated_questions_paper2': 5,
            'chapter_order': 3
        },
        {
            'name': 'Learning and Memory',
            'description': 'Classical conditioning, Operant conditioning, Memory processes',
            'weightage_paper2': 15,
            'estimated_questions_paper2': 8,
            'chapter_order': 4
        },
        {
            'name': 'Cognition and Intelligence',
            'description': 'Thinking, Problem solving, Intelligence theories, Creativity',
            'weightage_paper2': 12,
            'estimated_questions_paper2': 6,
            'chapter_order': 5
        },
        {
            'name': 'Developmental Psychology',
            'description': 'Physical, Cognitive, Social development across lifespan',
            'weightage_paper2': 12,
            'estimated_questions_paper2': 6,
            'chapter_order': 6
        },
        {
            'name': 'Personality',
            'description': 'Personality theories, Assessment, Individual differences',
            'weightage_paper2': 10,
            'estimated_questions_paper2': 5,
            'chapter_order': 7
        },
        {
            'name': 'Abnormal Psychology',
            'description': 'Classification of disorders, Anxiety, Mood disorders',
            'weightage_paper2': 10,
            'estimated_questions_paper2': 5,
            'chapter_order': 8
        },
        {
            'name': 'Social Psychology',
            'description': 'Attitudes, Stereotypes, Group dynamics, Conformity',
            'weightage_paper2': 9,
            'estimated_questions_paper2': 4,
            'chapter_order': 9
        }
    ]
}


def seed_ugc_net_subjects():
    """Seed UGC NET subjects with proper structure and weightages"""
    print("🌱 Seeding UGC NET subjects and chapters...")
    
    subjects_to_create = [
        PAPER_1_STRUCTURE,
        COMPUTER_SCIENCE_STRUCTURE,
        ENGLISH_LITERATURE_STRUCTURE,
        PSYCHOLOGY_STRUCTURE
    ]
    
    for subject_data in subjects_to_create:
        # Check if subject already exists
        existing_subject = Subject.query.filter_by(subject_code=subject_data['subject_code']).first()
        
        if existing_subject:
            print(f"ℹ️  Subject {subject_data['name']} already exists, skipping...")
            continue
        
        # Create subject
        subject = Subject(
            name=subject_data['name'],
            description=f"UGC NET {subject_data['name']} - Official syllabus structure",
            subject_code=subject_data['subject_code'],
            paper_type=subject_data['paper_type'],
            total_marks_paper1=subject_data.get('total_marks_paper1', 0),
            total_marks_paper2=subject_data.get('total_marks_paper2', 0),
            exam_duration_paper1=subject_data.get('exam_duration_paper1', 0),
            exam_duration_paper2=subject_data.get('exam_duration_paper2', 0),
            is_active=True
        )
        
        db.session.add(subject)
        db.session.flush()  # Get the subject ID
        
        print(f"✅ Created subject: {subject.name}")
        
        # Create chapters for this subject
        for chapter_data in subject_data['chapters']:
            chapter = Chapter(
                name=chapter_data['name'],
                description=chapter_data['description'],
                subject_id=subject.id,
                weightage_paper1=chapter_data.get('weightage_paper1', 0),
                weightage_paper2=chapter_data.get('weightage_paper2', 0),
                estimated_questions_paper1=chapter_data.get('estimated_questions_paper1', 0),
                estimated_questions_paper2=chapter_data.get('estimated_questions_paper2', 0),
                chapter_order=chapter_data['chapter_order'],
                is_active=True
            )
            
            db.session.add(chapter)
            print(f"  📚 Added chapter: {chapter.name}")
    
    try:
        db.session.commit()
        print("✅ UGC NET subjects and chapters seeded successfully!")
        
        # Print summary
        total_subjects = Subject.query.count()
        total_chapters = Chapter.query.count()
        print(f"\n📊 Summary:")
        print(f"  Total Subjects: {total_subjects}")
        print(f"  Total Chapters: {total_chapters}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error seeding UGC NET data: {str(e)}")
        raise e


def get_subject_weightage_info(subject_id, paper_type='paper2'):
    """Get weightage information for a subject"""
    subject = Subject.query.get(subject_id)
    if not subject:
        return None
    
    chapters = Chapter.query.filter_by(subject_id=subject_id, is_active=True).order_by(Chapter.chapter_order).all()
    
    weightage_info = {
        'subject_id': subject_id,
        'subject_name': subject.name,
        'paper_type': paper_type,
        'total_marks': subject.total_marks_paper2 if paper_type == 'paper2' else subject.total_marks_paper1,
        'exam_duration': subject.exam_duration_paper2 if paper_type == 'paper2' else subject.exam_duration_paper1,
        'chapters': []
    }
    
    for chapter in chapters:
        if paper_type == 'paper2':
            weightage = chapter.weightage_paper2
            estimated_questions = chapter.estimated_questions_paper2
        else:
            weightage = chapter.weightage_paper1
            estimated_questions = chapter.estimated_questions_paper1
        
        if weightage > 0:  # Only include chapters with weightage
            weightage_info['chapters'].append({
                'chapter_id': chapter.id,
                'chapter_name': chapter.name,
                'weightage': weightage,
                'estimated_questions': estimated_questions,
                'chapter_order': chapter.chapter_order
            })
    
    return weightage_info


if __name__ == '__main__':
    # This allows running the script directly for testing
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    from app import create_app
    app = create_app()
    
    with app.app_context():
        seed_ugc_net_subjects()
