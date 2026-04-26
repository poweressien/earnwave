"""
EarnWave Seed Data Command
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed EarnWave with sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🌊 Seeding EarnWave platform...'))
        self.create_admin()
        self.create_quiz_categories()
        self.create_quizzes()
        self.create_surveys()
        self.create_games()
        self.create_badges()
        self.stdout.write(self.style.SUCCESS('\n✅ EarnWave seeded successfully!\n'))
        self.stdout.write('  Admin login: admin@earnwave.ng / Admin@1234')

    def create_admin(self):
        from accounts.models import User, UserProfile
        if not User.objects.filter(email='admin@earnwave.ng').exists():
            user = User.objects.create_superuser(
                email='admin@earnwave.ng', password='Admin@1234',
                first_name='EarnWave', last_name='Admin'
            )
            UserProfile.objects.get_or_create(user=user)
            self.stdout.write('  ✓ Admin created')
        else:
            self.stdout.write('  - Admin already exists')

    def create_quiz_categories(self):
        from quizzes.models import QuizCategory
        cats = [
            ('General Knowledge', 'general-knowledge', 'book', '#2563EB'),
            ('Science & Tech', 'science-tech', 'flask', '#7C3AED'),
            ('Nigeria & Africa', 'nigeria-africa', 'globe', '#10B981'),
            ('JAMB Prep', 'jamb-prep', 'graduation-cap', '#F59E0B'),
            ('Sports', 'sports', 'futbol', '#EF4444'),
            ('Entertainment', 'entertainment', 'music', '#EC4899'),
        ]
        for name, slug, icon, color in cats:
            QuizCategory.objects.get_or_create(slug=slug, defaults={'name': name, 'icon': icon, 'color': color})
        self.stdout.write(f'  ✓ {len(cats)} quiz categories')

    def create_quizzes(self):
        from quizzes.models import Quiz, QuizQuestion, QuizCategory
        general = QuizCategory.objects.filter(slug='general-knowledge').first()
        ng = QuizCategory.objects.filter(slug='nigeria-africa').first()
        if not general or not ng:
            return

        quizzes = [
            {
                'meta': {'title': 'Nigeria Basics', 'category': ng, 'difficulty': 'easy',
                         'description': 'Test your knowledge about Nigeria — history, geography & culture.',
                         'time_limit_seconds': 30, 'points_per_correct': 10, 'bonus_points': 20, 'is_daily': True},
                'questions': [
                    ('What is the capital of Nigeria?', 'Lagos', 'Abuja', 'Kano', 'Port Harcourt', 'B', 'Abuja became Nigeria\'s capital in 1991, replacing Lagos.'),
                    ('In what year did Nigeria gain independence?', '1957', '1963', '1960', '1955', 'C', 'Nigeria gained independence from Britain on October 1, 1960.'),
                    ('What is Nigeria\'s official currency?', 'Dollar', 'Pound', 'Naira', 'Cedi', 'C', 'The Nigerian Naira (₦) is the official currency.'),
                    ('Which ocean borders Nigeria to the south?', 'Indian Ocean', 'Pacific Ocean', 'Arctic Ocean', 'Atlantic Ocean', 'D', 'The Atlantic Ocean (Gulf of Guinea) borders Nigeria to the south.'),
                    ('What is the largest city in Nigeria by population?', 'Abuja', 'Kano', 'Ibadan', 'Lagos', 'D', 'Lagos is Nigeria\'s largest city with over 15 million people.'),
                ]
            },
            {
                'meta': {'title': 'Tech & The Internet', 'category': general, 'difficulty': 'medium',
                         'description': 'How tech-savvy are you? Test your digital knowledge.',
                         'time_limit_seconds': 25, 'points_per_correct': 15, 'bonus_points': 30},
                'questions': [
                    ('What does HTTP stand for?', 'HyperText Transfer Protocol', 'High Transfer Tech Protocol', 'Hyper Terminal Transfer Point', 'HyperText Transmission Program', 'A', 'HTTP = HyperText Transfer Protocol, the foundation of the web.'),
                    ('Who created Python?', 'Google', 'Microsoft', 'Guido van Rossum', 'Apple', 'C', 'Python was created by Guido van Rossum, first released in 1991.'),
                    ('What does RAM stand for?', 'Read Access Memory', 'Random Access Memory', 'Rapid Access Module', 'Read And Memorize', 'B', 'RAM = Random Access Memory, your computer\'s short-term storage.'),
                    ('What is the most visited website in the world?', 'Facebook', 'YouTube', 'Google', 'Wikipedia', 'C', 'Google.com is the most visited website globally.'),
                ]
            },
            {
                'meta': {'title': 'African Geography', 'category': ng, 'difficulty': 'medium',
                         'description': 'How well do you know the African continent?',
                         'time_limit_seconds': 30, 'points_per_correct': 12, 'bonus_points': 25},
                'questions': [
                    ('Which is the longest river in Africa?', 'Congo River', 'Niger River', 'Nile River', 'Zambezi River', 'C', 'The Nile River, at 6,650 km, is the longest river in Africa.'),
                    ('What is the largest country in Africa by area?', 'Nigeria', 'Sudan', 'Algeria', 'DR Congo', 'C', 'Algeria is the largest African country with 2.38 million km².'),
                    ('Which African country has the largest population?', 'Egypt', 'Ethiopia', 'Nigeria', 'DR Congo', 'C', 'Nigeria is Africa\'s most populous country with 220+ million people.'),
                    ('What is the tallest mountain in Africa?', 'Mount Kenya', 'Mount Kilimanjaro', 'Atlas Mountains', 'Rwenzori', 'B', 'Mount Kilimanjaro in Tanzania at 5,895m is Africa\'s highest peak.'),
                ]
            },
        ]

        for qdata in quizzes:
            quiz, created = Quiz.objects.get_or_create(title=qdata['meta']['title'], defaults=qdata['meta'])
            if created:
                for i, q in enumerate(qdata['questions']):
                    QuizQuestion.objects.create(
                        quiz=quiz, text=q[0], option_a=q[1], option_b=q[2],
                        option_c=q[3], option_d=q[4], correct_answer=q[5],
                        explanation=q[6], order=i + 1
                    )
        self.stdout.write(f'  ✓ {len(quizzes)} quizzes with questions')

    def create_surveys(self):
        from surveys.models import Survey, SurveyQuestion, SurveyOption

        surveys = [
            {
                'meta': {'title': 'Nigerian Internet & Content Habits',
                         'description': 'Help us understand how Nigerians use the internet daily.',
                         'category': 'general', 'points_reward': 50, 'estimated_minutes': 3,
                         'max_responses': 500, 'status': 'active'},
                'questions': [
                    ('How many hours do you spend online daily?', 'multiple_choice',
                     ['Less than 1 hour', '1-3 hours', '3-6 hours', 'More than 6 hours']),
                    ('What content do you consume most?', 'multiple_choice',
                     ['News & Politics', 'Entertainment & Music', 'Education', 'Social Media']),
                    ('Which social media do you use most?', 'multiple_choice',
                     ['WhatsApp', 'Instagram', 'TikTok', 'Twitter/X']),
                    ('What would you like to see more of online?', 'text', []),
                ]
            },
            {
                'meta': {'title': 'Mobile Money & Fintech Survey',
                         'description': 'Sponsored research on digital payments in Nigeria.',
                         'category': 'finance', 'points_reward': 100, 'estimated_minutes': 5,
                         'max_responses': 1000, 'status': 'active',
                         'is_sponsored': True, 'sponsor_name': 'FinTechNG'},
                'questions': [
                    ('Do you use mobile banking?', 'boolean', []),
                    ('Which app do you use most?', 'multiple_choice',
                     ['Opay', 'PalmPay', 'Kuda', 'GTBank App', 'Moniepoint']),
                    ('Rate digital banking in Nigeria (1=Poor, 5=Excellent)', 'rating', []),
                    ('What feature is most important to you?', 'multiple_choice',
                     ['Transaction Speed', 'Low Fees', 'Security', 'Cashback Rewards']),
                ]
            },
            {
                'meta': {'title': 'FMCG Consumer Preferences',
                         'description': 'What brands do Nigerians love? Share your opinion.',
                         'category': 'consumer', 'points_reward': 75, 'estimated_minutes': 4,
                         'max_responses': 800, 'status': 'active'},
                'questions': [
                    ('Where do you buy groceries most?', 'multiple_choice',
                     ['Open market', 'Supermarket', 'Online delivery', 'Corner store']),
                    ('How much do you spend on food weekly?', 'multiple_choice',
                     ['Under ₦2,000', '₦2,000-₦5,000', '₦5,000-₦15,000', 'Over ₦15,000']),
                    ('Do you buy Nigerian-made products over foreign ones?', 'boolean', []),
                ]
            },
        ]

        for sdata in surveys:
            survey, created = Survey.objects.get_or_create(title=sdata['meta']['title'], defaults=sdata['meta'])
            if created:
                for i, (text, qtype, options) in enumerate(sdata['questions']):
                    sq = SurveyQuestion.objects.create(
                        survey=survey, text=text, question_type=qtype, order=i + 1
                    )
                    for j, opt in enumerate(options):
                        SurveyOption.objects.create(question=sq, text=opt, order=j + 1)
        self.stdout.write(f'  ✓ {len(surveys)} surveys with questions')

    def create_games(self):
        from games.models import Game
        games = [
            {'title': 'Memory Match Classic', 'game_type': 'memory', 'difficulty': 'easy',
             'description': 'Flip cards and match emoji pairs as fast as you can!',
             'instructions': 'Click any two cards to flip them. Find all matching pairs before time runs out. Fewer moves = higher score!',
             'points_reward': 25, 'time_limit_seconds': 90},
            {'title': 'Speed Math Blitz', 'game_type': 'math', 'difficulty': 'medium',
             'description': 'Solve rapid-fire math problems and earn big points.',
             'instructions': 'Answer as many math questions as you can in 60 seconds. Correct answers earn points!',
             'points_reward': 35, 'time_limit_seconds': 60},
            {'title': 'Word Scramble Nigeria', 'game_type': 'word', 'difficulty': 'easy',
             'description': 'Unscramble Nigerian city and state names to win.',
             'instructions': 'Rearrange the scrambled letters to spell the correct Nigerian location.',
             'points_reward': 20, 'time_limit_seconds': 120},
            {'title': 'Logic Grid Challenge', 'game_type': 'logic', 'difficulty': 'hard',
             'description': 'Test your logical reasoning with pattern puzzles.',
             'instructions': 'Find the pattern and pick the missing piece. Each level gets harder!',
             'points_reward': 50, 'time_limit_seconds': 180},
        ]
        for gdata in games:
            Game.objects.get_or_create(title=gdata['title'], defaults=gdata)
        self.stdout.write(f'  ✓ {len(games)} games')

    def create_badges(self):
        from rewards.models import Badge
        badges = [
            {'name': 'First Timer', 'description': 'Complete your very first task', 'icon': 'star', 'rarity': 'common', 'condition_type': 'surveys_completed', 'condition_value': 1, 'points_reward': 25},
            {'name': 'Survey King', 'description': 'Complete 10 surveys', 'icon': 'clipboard', 'rarity': 'rare', 'condition_type': 'surveys_completed', 'condition_value': 10, 'points_reward': 100},
            {'name': 'Quiz Wizard', 'description': 'Complete 10 quizzes', 'icon': 'brain', 'rarity': 'rare', 'condition_type': 'quizzes_completed', 'condition_value': 10, 'points_reward': 100},
            {'name': 'Streak Champion', 'description': 'Maintain a 7-day login streak', 'icon': 'fire', 'rarity': 'rare', 'condition_type': 'login_streak', 'condition_value': 7, 'points_reward': 150},
            {'name': 'Super Connector', 'description': 'Refer 5 friends who join', 'icon': 'users', 'rarity': 'epic', 'condition_type': 'referrals', 'condition_value': 5, 'points_reward': 300},
            {'name': 'Points Millionaire', 'description': 'Earn 10,000 lifetime points', 'icon': 'trophy', 'rarity': 'legendary', 'condition_type': 'total_points', 'condition_value': 10000, 'points_reward': 500},
            {'name': 'Game Master', 'description': 'Complete 20 games', 'icon': 'gamepad', 'rarity': 'epic', 'condition_type': 'games_completed', 'condition_value': 20, 'points_reward': 250},
        ]
        for bdata in badges:
            Badge.objects.get_or_create(name=bdata['name'], defaults=bdata)
        self.stdout.write(f'  ✓ {len(badges)} badges')
