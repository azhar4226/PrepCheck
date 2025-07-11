#!/usr/bin/env python3
"""
Seed file for UGC NET subjects and chapters
This file populates the database with UGC NET subjects and their corresponding chapters
"""
import os
import sys

from app import db, create_app
from app.models import Subject, Chapter

def seed_subjects_and_chapters():
    """
    Seed the database with UGC NET subjects and their chapters
    """
    
    # UGC NET subjects with their chapters
    ugc_net_data = {
        # Paper 1 - General Paper (Common for all subjects)
        "Teaching Aptitude": {
            "subject_code": "001",
            "paper_type": "paper1",
            "description": "General Paper on Teaching & Research Aptitude",
            "chapters": [
                {"name": "Teaching Aptitude", "weightage": 15, "estimated_questions": 8, "chapter_order": 1,
                 "description": "Nature, objectives, characteristics and basic requirements of teaching"},
                {"name": "Research Aptitude", "weightage": 15, "estimated_questions": 8, "chapter_order": 2,
                 "description": "Research methodology, types of research, research ethics"},
                {"name": "Reading Comprehension", "weightage": 10, "estimated_questions": 5, "chapter_order": 3,
                 "description": "Comprehension passages and analytical reasoning"},
                {"name": "Communication", "weightage": 10, "estimated_questions": 5, "chapter_order": 4,
                 "description": "Communication types, barriers, and effective communication"},
                {"name": "Mathematical Reasoning", "weightage": 10, "estimated_questions": 5, "chapter_order": 5,
                 "description": "Number series, coding-decoding, mathematical operations"},
                {"name": "Logical Reasoning", "weightage": 10, "estimated_questions": 5, "chapter_order": 6,
                 "description": "Logical deduction, syllogism, analytical reasoning"},
                {"name": "Data Interpretation", "weightage": 10, "estimated_questions": 5, "chapter_order": 7,
                 "description": "Tables, graphs, charts interpretation"},
                {"name": "Information and Communication Technology", "weightage": 10, "estimated_questions": 5, "chapter_order": 8,
                 "description": "ICT in education, digital initiatives, cyber security"},
                {"name": "People, Development and Environment", "weightage": 10, "estimated_questions": 5, "chapter_order": 9,
                 "description": "Environmental studies, sustainable development, biodiversity"},
                {"name": "Higher Education System", "weightage": 10, "estimated_questions": 5, "chapter_order": 10,
                 "description": "Governance, polity and administration in higher education"}
            ]
        },
        
        # Paper 2 Subjects - Major NET subjects
        "Computer Science and Applications": {
            "subject_code": "087",
            "paper_type": "paper2",
            "description": "Computer Science and Applications for UGC NET",
            "chapters": [
                {"name": "Discrete Structures and Optimization", "weightage": 15, "estimated_questions": 12, "chapter_order": 1,
                 "description": "Logic, set theory, combinatorics, graph theory, optimization techniques"},
                {"name": "Computer System Architecture", "weightage": 12, "estimated_questions": 10, "chapter_order": 2,
                 "description": "Digital logic, computer organization, memory hierarchy, I/O systems"},
                {"name": "Programming Languages and Algorithms", "weightage": 15, "estimated_questions": 12, "chapter_order": 3,
                 "description": "Programming paradigms, data structures, algorithm analysis"},
                {"name": "Operating Systems", "weightage": 10, "estimated_questions": 8, "chapter_order": 4,
                 "description": "Process management, memory management, file systems"},
                {"name": "Database Management Systems", "weightage": 12, "estimated_questions": 10, "chapter_order": 5,
                 "description": "Relational model, SQL, normalization, transaction management"},
                {"name": "Computer Networks", "weightage": 10, "estimated_questions": 8, "chapter_order": 6,
                 "description": "Network protocols, OSI model, TCP/IP, network security"},
                {"name": "Software Engineering", "weightage": 8, "estimated_questions": 6, "chapter_order": 7,
                 "description": "Software development life cycle, testing, project management"},
                {"name": "Web Technologies", "weightage": 8, "estimated_questions": 6, "chapter_order": 8,
                 "description": "HTML, CSS, JavaScript, web frameworks, web services"},
                {"name": "Artificial Intelligence", "weightage": 10, "estimated_questions": 8, "chapter_order": 9,
                 "description": "Machine learning, neural networks, expert systems"}
            ]
        },
        
        "Management": {
            "subject_code": "017",
            "paper_type": "paper2",
            "description": "Management for UGC NET",
            "chapters": [
                {"name": "Management Theory and Practice", "weightage": 15, "estimated_questions": 12, "chapter_order": 1,
                 "description": "Evolution of management thought, functions of management"},
                {"name": "Organizational Behaviour", "weightage": 12, "estimated_questions": 10, "chapter_order": 2,
                 "description": "Individual behavior, group dynamics, organizational culture"},
                {"name": "Human Resource Management", "weightage": 12, "estimated_questions": 10, "chapter_order": 3,
                 "description": "Recruitment, selection, training, performance management"},
                {"name": "Marketing Management", "weightage": 12, "estimated_questions": 10, "chapter_order": 4,
                 "description": "Marketing mix, consumer behavior, market research"},
                {"name": "Financial Management", "weightage": 12, "estimated_questions": 10, "chapter_order": 5,
                 "description": "Financial planning, capital structure, investment decisions"},
                {"name": "Operations Management", "weightage": 10, "estimated_questions": 8, "chapter_order": 6,
                 "description": "Production planning, quality management, supply chain"},
                {"name": "Strategic Management", "weightage": 12, "estimated_questions": 10, "chapter_order": 7,
                 "description": "Strategic planning, competitive advantage, corporate strategy"},
                {"name": "International Business", "weightage": 8, "estimated_questions": 6, "chapter_order": 8,
                 "description": "Global business environment, international trade"},
                {"name": "Entrepreneurship", "weightage": 7, "estimated_questions": 4, "chapter_order": 9,
                 "description": "Business planning, startup management, innovation"}
            ]
        },
        
        "Economics": {
            "subject_code": "001",
            "paper_type": "paper2",
            "description": "Economics for UGC NET",
            "chapters": [
                {"name": "Micro Economics", "weightage": 15, "estimated_questions": 12, "chapter_order": 1,
                 "description": "Consumer theory, producer theory, market structures"},
                {"name": "Macro Economics", "weightage": 15, "estimated_questions": 12, "chapter_order": 2,
                 "description": "National income, money and banking, fiscal policy"},
                {"name": "International Economics", "weightage": 12, "estimated_questions": 10, "chapter_order": 3,
                 "description": "International trade, balance of payments, exchange rates"},
                {"name": "Public Economics", "weightage": 10, "estimated_questions": 8, "chapter_order": 4,
                 "description": "Public goods, taxation, public expenditure"},
                {"name": "Development Economics", "weightage": 12, "estimated_questions": 10, "chapter_order": 5,
                 "description": "Economic development, poverty, inequality"},
                {"name": "Indian Economy", "weightage": 12, "estimated_questions": 10, "chapter_order": 6,
                 "description": "Economic planning, agricultural economy, industrial policy"},
                {"name": "Econometrics", "weightage": 10, "estimated_questions": 8, "chapter_order": 7,
                 "description": "Statistical methods, regression analysis, hypothesis testing"},
                {"name": "Economic Thought", "weightage": 8, "estimated_questions": 6, "chapter_order": 8,
                 "description": "Classical, neo-classical, and modern economic theories"},
                {"name": "Environmental Economics", "weightage": 6, "estimated_questions": 4, "chapter_order": 9,
                 "description": "Environmental valuation, sustainable development"}
            ]
        },
        
        "English": {
            "subject_code": "002",
            "paper_type": "paper2",
            "description": "English Literature for UGC NET",
            "chapters": [
                {"name": "British Literature (Medieval to 17th Century)", "weightage": 12, "estimated_questions": 10, "chapter_order": 1,
                 "description": "Chaucer, Shakespeare, Milton, Metaphysical poets"},
                {"name": "British Literature (18th-19th Century)", "weightage": 12, "estimated_questions": 10, "chapter_order": 2,
                 "description": "Romantic and Victorian literature, novel development"},
                {"name": "British Literature (20th Century)", "weightage": 10, "estimated_questions": 8, "chapter_order": 3,
                 "description": "Modernist and contemporary British literature"},
                {"name": "American Literature", "weightage": 12, "estimated_questions": 10, "chapter_order": 4,
                 "description": "Colonial to contemporary American literature"},
                {"name": "Indian English Literature", "weightage": 15, "estimated_questions": 12, "chapter_order": 5,
                 "description": "Indo-Anglian poetry, fiction, and drama"},
                {"name": "Literary Theory and Criticism", "weightage": 12, "estimated_questions": 10, "chapter_order": 6,
                 "description": "Classical to contemporary literary theories"},
                {"name": "Language and Linguistics", "weightage": 10, "estimated_questions": 8, "chapter_order": 7,
                 "description": "Phonetics, syntax, semantics, pragmatics"},
                {"name": "Comparative Literature", "weightage": 8, "estimated_questions": 6, "chapter_order": 8,
                 "description": "Translation studies, world literature"},
                {"name": "Women's Writing", "weightage": 9, "estimated_questions": 6, "chapter_order": 9,
                 "description": "Feminist literature and gender studies"}
            ]
        },
        
        "History": {
            "subject_code": "016",
            "paper_type": "paper2",
            "description": "History for UGC NET",
            "chapters": [
                {"name": "Ancient Indian History", "weightage": 15, "estimated_questions": 12, "chapter_order": 1,
                 "description": "Indus Valley, Vedic period, Mauryan and Gupta empires"},
                {"name": "Medieval Indian History", "weightage": 15, "estimated_questions": 12, "chapter_order": 2,
                 "description": "Delhi Sultanate, Mughal Empire, regional kingdoms"},
                {"name": "Modern Indian History", "weightage": 15, "estimated_questions": 12, "chapter_order": 3,
                 "description": "British rule, freedom struggle, independence"},
                {"name": "World History (Ancient)", "weightage": 10, "estimated_questions": 8, "chapter_order": 4,
                 "description": "Ancient civilizations, Greece, Rome"},
                {"name": "World History (Medieval)", "weightage": 10, "estimated_questions": 8, "chapter_order": 5,
                 "description": "Byzantine, Islamic world, Crusades"},
                {"name": "World History (Modern)", "weightage": 15, "estimated_questions": 12, "chapter_order": 6,
                 "description": "Renaissance, Industrial Revolution, World Wars"},
                {"name": "Historiography", "weightage": 10, "estimated_questions": 8, "chapter_order": 7,
                 "description": "Historical methods, sources, interpretation"},
                {"name": "Art and Culture", "weightage": 10, "estimated_questions": 8, "chapter_order": 8,
                 "description": "Architecture, sculpture, painting, performing arts"}
            ]
        },
        
        "Political Science": {
            "subject_code": "055",
            "paper_type": "paper2",
            "description": "Political Science for UGC NET",
            "chapters": [
                {"name": "Political Theory", "weightage": 15, "estimated_questions": 12, "chapter_order": 1,
                 "description": "State, sovereignty, rights, justice, equality"},
                {"name": "Indian Government and Politics", "weightage": 15, "estimated_questions": 12, "chapter_order": 2,
                 "description": "Constitution, federalism, political parties, elections"},
                {"name": "Comparative Politics", "weightage": 12, "estimated_questions": 10, "chapter_order": 3,
                 "description": "Political systems, democratization, political culture"},
                {"name": "International Relations", "weightage": 15, "estimated_questions": 12, "chapter_order": 4,
                 "description": "Theories of IR, foreign policy, international organizations"},
                {"name": "Public Administration", "weightage": 12, "estimated_questions": 10, "chapter_order": 5,
                 "description": "Administrative theory, bureaucracy, public policy"},
                {"name": "Research Methods", "weightage": 8, "estimated_questions": 6, "chapter_order": 6,
                 "description": "Quantitative and qualitative methods, data analysis"},
                {"name": "Contemporary Issues", "weightage": 12, "estimated_questions": 10, "chapter_order": 7,
                 "description": "Globalization, terrorism, human rights"},
                {"name": "Political Sociology", "weightage": 11, "estimated_questions": 8, "chapter_order": 8,
                 "description": "Social movements, political participation, civil society"}
            ]
        },
        
        "Commerce": {
            "subject_code": "008",
            "paper_type": "paper2",
            "description": "Commerce for UGC NET",
            "chapters": [
                {"name": "Accounting and Auditing", "weightage": 15, "estimated_questions": 12, "chapter_order": 1,
                 "description": "Financial accounting, cost accounting, auditing principles"},
                {"name": "Corporate Finance", "weightage": 12, "estimated_questions": 10, "chapter_order": 2,
                 "description": "Capital budgeting, financial planning, risk management"},
                {"name": "Marketing", "weightage": 12, "estimated_questions": 10, "chapter_order": 3,
                 "description": "Marketing management, consumer behavior, digital marketing"},
                {"name": "Business Law", "weightage": 10, "estimated_questions": 8, "chapter_order": 4,
                 "description": "Contract law, company law, commercial law"},
                {"name": "Income Tax and Corporate Tax", "weightage": 12, "estimated_questions": 10, "chapter_order": 5,
                 "description": "Tax provisions, tax planning, GST"},
                {"name": "Banking and Insurance", "weightage": 10, "estimated_questions": 8, "chapter_order": 6,
                 "description": "Banking operations, insurance principles, financial services"},
                {"name": "International Business", "weightage": 10, "estimated_questions": 8, "chapter_order": 7,
                 "description": "Export-import, foreign exchange, international finance"},
                {"name": "Entrepreneurship Development", "weightage": 9, "estimated_questions": 6, "chapter_order": 8,
                 "description": "Business planning, startup ecosystem, innovation"},
                {"name": "E-Commerce", "weightage": 10, "estimated_questions": 8, "chapter_order": 9,
                 "description": "Digital business models, online marketing, payment systems"}
            ]
        },
        
        "Psychology": {
            "subject_code": "037",
            "paper_type": "paper2",
            "description": "Psychology for UGC NET",
            "chapters": [
                {"name": "Introduction to Psychology", "weightage": 12, "estimated_questions": 10, "chapter_order": 1,
                 "description": "History, schools of psychology, research methods"},
                {"name": "Cognitive Psychology", "weightage": 12, "estimated_questions": 10, "chapter_order": 2,
                 "description": "Memory, attention, perception, thinking"},
                {"name": "Developmental Psychology", "weightage": 12, "estimated_questions": 10, "chapter_order": 3,
                 "description": "Child development, adolescence, adulthood, aging"},
                {"name": "Social Psychology", "weightage": 12, "estimated_questions": 10, "chapter_order": 4,
                 "description": "Social influence, group dynamics, attitudes"},
                {"name": "Personality Psychology", "weightage": 10, "estimated_questions": 8, "chapter_order": 5,
                 "description": "Personality theories, assessment, individual differences"},
                {"name": "Abnormal Psychology", "weightage": 12, "estimated_questions": 10, "chapter_order": 6,
                 "description": "Mental disorders, psychopathology, diagnosis"},
                {"name": "Psychological Testing", "weightage": 10, "estimated_questions": 8, "chapter_order": 7,
                 "description": "Test construction, reliability, validity, standardization"},
                {"name": "Applied Psychology", "weightage": 10, "estimated_questions": 8, "chapter_order": 8,
                 "description": "Clinical, counseling, organizational psychology"},
                {"name": "Research Methods and Statistics", "weightage": 10, "estimated_questions": 8, "chapter_order": 9,
                 "description": "Experimental design, statistical analysis, research ethics"}
            ]
        },
        
        "Sociology": {
            "subject_code": "062",
            "paper_type": "paper2",
            "description": "Sociology for UGC NET",
            "chapters": [
                {"name": "Sociological Theory", "weightage": 15, "estimated_questions": 12, "chapter_order": 1,
                 "description": "Classical and contemporary sociological theories"},
                {"name": "Social Structure", "weightage": 12, "estimated_questions": 10, "chapter_order": 2,
                 "description": "Social stratification, caste, class, gender"},
                {"name": "Indian Society", "weightage": 15, "estimated_questions": 12, "chapter_order": 3,
                 "description": "Caste system, family, kinship, tribal society"},
                {"name": "Social Institutions", "weightage": 12, "estimated_questions": 10, "chapter_order": 4,
                 "description": "Family, marriage, religion, education"},
                {"name": "Social Change", "weightage": 10, "estimated_questions": 8, "chapter_order": 5,
                 "description": "Modernization, globalization, social movements"},
                {"name": "Research Methods", "weightage": 10, "estimated_questions": 8, "chapter_order": 6,
                 "description": "Quantitative and qualitative methods, sampling"},
                {"name": "Rural and Urban Sociology", "weightage": 12, "estimated_questions": 10, "chapter_order": 7,
                 "description": "Rural-urban differences, urbanization, migration"},
                {"name": "Applied Sociology", "weightage": 8, "estimated_questions": 6, "chapter_order": 8,
                 "description": "Social problems, social policy, social work"},
                {"name": "Contemporary Issues", "weightage": 6, "estimated_questions": 4, "chapter_order": 9,
                 "description": "Globalization, environment, human rights"}
            ]
        },
        
        "Education": {
            "subject_code": "012",
            "paper_type": "paper2",
            "description": "Education for UGC NET",
            "chapters": [
                {"name": "Foundations of Education", "weightage": 15, "estimated_questions": 12, "chapter_order": 1,
                 "description": "Philosophy, sociology, psychology of education"},
                {"name": "Educational Psychology", "weightage": 12, "estimated_questions": 10, "chapter_order": 2,
                 "description": "Learning theories, motivation, individual differences"},
                {"name": "Curriculum and Instruction", "weightage": 12, "estimated_questions": 10, "chapter_order": 3,
                 "description": "Curriculum development, teaching methods, assessment"},
                {"name": "Educational Technology", "weightage": 10, "estimated_questions": 8, "chapter_order": 4,
                 "description": "ICT in education, e-learning, educational media"},
                {"name": "Educational Administration", "weightage": 10, "estimated_questions": 8, "chapter_order": 5,
                 "description": "Leadership, planning, management in education"},
                {"name": "Teacher Education", "weightage": 10, "estimated_questions": 8, "chapter_order": 6,
                 "description": "Teacher training, professional development, competencies"},
                {"name": "Educational Research", "weightage": 10, "estimated_questions": 8, "chapter_order": 7,
                 "description": "Research methods, statistics, action research"},
                {"name": "Contemporary Issues", "weightage": 11, "estimated_questions": 8, "chapter_order": 8,
                 "description": "Inclusive education, quality, equity, policy"},
                {"name": "Comparative Education", "weightage": 10, "estimated_questions": 8, "chapter_order": 9,
                 "description": "Education systems, international perspectives"}
            ]
        }
    }
    
    try:
        
        print("Starting to seed subjects and chapters...")
        
        # Track statistics
        subjects_created = 0
        chapters_created = 0
        
        for subject_name, subject_data in ugc_net_data.items():
            # Check if subject already exists
            existing_subject = Subject.query.filter_by(name=subject_name).first()
            
            if existing_subject:
                print(f"Subject '{subject_name}' already exists. Skipping...")
                continue
            
            # Create new subject
            new_subject = Subject(
                name=subject_name,
                description=subject_data["description"],
                subject_code=subject_data["subject_code"],
                paper_type=subject_data["paper_type"],
                is_active=True
            )
            
            db.session.add(new_subject)
            db.session.flush()  # Flush to get the ID
            
            subjects_created += 1
            print(f"Created subject: {subject_name} (Code: {subject_data['subject_code']})")
            
            # Create chapters for this subject
            for chapter_data in subject_data["chapters"]:
                # Check if chapter already exists for this subject
                existing_chapter = Chapter.query.filter_by(
                    name=chapter_data["name"],
                    subject_id=new_subject.id
                ).first()
                
                if existing_chapter:
                    print(f"  Chapter '{chapter_data['name']}' already exists for subject '{subject_name}'. Skipping...")
                    continue
                
                new_chapter = Chapter(
                    name=chapter_data["name"],
                    description=chapter_data["description"],
                    subject_id=new_subject.id,
                    weightage=chapter_data["weightage"],
                    estimated_questions=chapter_data["estimated_questions"],
                    chapter_order=chapter_data["chapter_order"],
                    is_active=True
                )
                
                db.session.add(new_chapter)
                chapters_created += 1
                print(f"  Created chapter: {chapter_data['name']} (Weightage: {chapter_data['weightage']}%)")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Seeding completed successfully!")
        print(f"📊 Statistics:")
        print(f"   - Subjects created: {subjects_created}")
        print(f"   - Chapters created: {chapters_created}")
        print(f"   - Total subjects in database: {Subject.query.count()}")
        print(f"   - Total chapters in database: {Chapter.query.count()}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error during seeding: {str(e)}")
        raise e

def verify_seeding():
    """
    Verify that the seeding was successful by checking the database
    """
    try:
        print("\n🔍 Verifying seeding results...")
        
        subjects = Subject.query.all()
        print(f"Total subjects: {len(subjects)}")
        
        for subject in subjects:
            chapters_count = Chapter.query.filter_by(subject_id=subject.id).count()
            total_weightage = db.session.query(db.func.sum(Chapter.weightage)).filter_by(subject_id=subject.id).scalar() or 0
            print(f"  📚 {subject.name} ({subject.subject_code}) - {subject.paper_type}")
            print(f"      Chapters: {chapters_count}, Total Weightage: {total_weightage}%")
            
            if total_weightage != 100 and chapters_count > 0:
                print(f"      ⚠️  Warning: Total weightage is {total_weightage}% (should be 100%)")
                    
    except Exception as e:
        print(f"❌ Error during verification: {str(e)}")

def get_subject_weightage_info(subject_id=None):
    """
    Returns a dictionary of subject(s) and their total chapter weightage.
    If subject_id is provided, returns info for that subject only.
    """
    from app.models import Subject, Chapter
    result = {}
    query = Subject.query
    if subject_id:
        query = query.filter_by(id=subject_id)
    subjects = query.all()
    for subject in subjects:
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        total_weightage = sum(ch.weightage for ch in chapters)
        result[subject.name] = {
            'subject_id': subject.id,
            'subject_code': subject.subject_code,
            'total_weightage': total_weightage,
            'chapter_count': len(chapters),
            'chapters': [
                {
                    'chapter_id': ch.id,
                    'name': ch.name,
                    'weightage': ch.weightage
                } for ch in chapters
            ]
        }
    return result

if __name__ == "__main__":
    print("🌱 UGC NET Subjects and Chapters Seeding Script")
    print("=" * 50)
    app = create_app()
    with app.app_context():
        try:
            # Run the seeding
            seed_subjects_and_chapters()
            
            # Verify the results
            verify_seeding()
            
            print("\n✅ Script completed successfully!")
        except Exception as e:
            print(f"\n❌ Script failed: {str(e)}")
            exit(1)