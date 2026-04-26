"""
EarnWave Content Seeder
Adds surveys, quizzes, and games to the platform.
Usage: python manage.py seed_content
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Add surveys, quizzes and games content to EarnWave'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('\n🌊 Adding EarnWave content...\n'))
        s = self.add_surveys()
        q = self.add_quizzes()
        g = self.add_games()
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Done! Added {s} surveys, {q} quizzes, {g} games.\n'
        ))

    # ─────────────────────────────────────────────────────────── SURVEYS ──────

    def add_surveys(self):
        from surveys.models import Survey, SurveyQuestion, SurveyOption
        added = 0

        surveys = [

            # ── 1 ─────────────────────────────────────────────────────────────
            {
                'meta': {
                    'title': 'Nigerian Food & Eating Habits',
                    'description': 'Tell us about your daily food choices and preferences.',
                    'category': 'lifestyle', 'points_reward': 60,
                    'estimated_minutes': 4, 'max_responses': 2000, 'status': 'active',
                },
                'questions': [
                    ('How many times do you eat per day?', 'multiple_choice',
                     ['Once', 'Twice', 'Three times', 'More than three times']),
                    ('Which Nigerian dish is your absolute favourite?', 'multiple_choice',
                     ['Jollof Rice', 'Egusi Soup & Eba', 'Pepper Soup', 'Suya']),
                    ('Do you cook at home or eat out more often?', 'multiple_choice',
                     ['Always cook at home', 'Mostly cook at home',
                      'Mostly eat out', 'Always eat out']),
                    ('How much do you spend on food daily on average?', 'multiple_choice',
                     ['Under ₦500', '₦500–₦1,500', '₦1,500–₦3,000', 'Over ₦3,000']),
                    ('Do you eat breakfast every day?', 'boolean', []),
                    ('What is your biggest challenge when it comes to eating well?', 'text', []),
                ],
            },

            # ── 2 ─────────────────────────────────────────────────────────────
            {
                'meta': {
                    'title': 'Social Media Usage in Nigeria 2024',
                    'description': 'How do Nigerians really use social media? Share your habits.',
                    'category': 'tech', 'points_reward': 50,
                    'estimated_minutes': 3, 'max_responses': 3000, 'status': 'active',
                },
                'questions': [
                    ('Which social media platform do you use most?', 'multiple_choice',
                     ['WhatsApp', 'Instagram', 'TikTok', 'Twitter / X']),
                    ('How many hours per day do you spend on social media?', 'multiple_choice',
                     ['Less than 1 hour', '1–3 hours', '3–6 hours', 'Over 6 hours']),
                    ('Have you ever bought something you saw advertised on social media?', 'boolean', []),
                    ('What type of content do you post most?', 'multiple_choice',
                     ['Personal photos/videos', 'Opinions & thoughts',
                      'Business/selling', 'I rarely post']),
                    ('Rate your overall social media experience (1 = Bad, 5 = Excellent)', 'rating', []),
                ],
            },

            # ── 3 ─────────────────────────────────────────────────────────────
            {
                'meta': {
                    'title': 'Education & Career Aspirations',
                    'description': 'Help us understand the career goals of young Nigerians.',
                    'category': 'education', 'points_reward': 75,
                    'estimated_minutes': 5, 'max_responses': 1500, 'status': 'active',
                },
                'questions': [
                    ('What is your highest level of education?', 'multiple_choice',
                     ['Secondary School (WAEC/NECO)', 'OND/HND',
                      'BSc/BA', 'MSc/MBA or higher']),
                    ('What is your current employment status?', 'multiple_choice',
                     ['Student', 'Employed (full-time)', 'Self-employed / Freelancer',
                      'Unemployed / Job-seeking']),
                    ('Which sector would you most like to work in?', 'multiple_choice',
                     ['Technology & Startups', 'Finance & Banking',
                      'Oil & Gas', 'Healthcare']),
                    ('Do you believe your education prepared you for the job market?', 'boolean', []),
                    ('What skills do you think Nigerians need most for the future?', 'text', []),
                    ('How likely are you to consider working abroad (Japa)?', 'multiple_choice',
                     ['Very likely', 'Somewhat likely',
                      'Unlikely', 'I already have plans to']),
                ],
            },

            # ── 4 ─────────────────────────────────────────────────────────────
            {
                'meta': {
                    'title': 'Nigerian Music & Entertainment Survey',
                    'description': 'What music do Nigerians love? Help us map the entertainment landscape.',
                    'category': 'lifestyle', 'points_reward': 45,
                    'estimated_minutes': 3, 'max_responses': 5000, 'status': 'active',
                    'is_sponsored': True, 'sponsor_name': 'AfroBeat Records',
                },
                'questions': [
                    ('Which music genre do you listen to most?', 'multiple_choice',
                     ['Afrobeats', 'Afropop', 'Fuji / Traditional', 'Hip-hop / Rap']),
                    ('Who is your favourite Nigerian artist right now?', 'multiple_choice',
                     ['Burna Boy', 'Wizkid', 'Davido', 'Asake']),
                    ('How do you mainly listen to music?', 'multiple_choice',
                     ['Streaming apps (Spotify, Apple Music)', 'YouTube',
                      'Downloaded MP3s', 'Radio']),
                    ('Have you attended a live music concert in Nigeria?', 'boolean', []),
                    ('Rate the current state of Nigerian entertainment (1–5)', 'rating', []),
                ],
            },

            # ── 5 ─────────────────────────────────────────────────────────────
            {
                'meta': {
                    'title': 'Health & Wellness Habits Survey',
                    'description': 'Tell us about your health routines and wellness practices.',
                    'category': 'health', 'points_reward': 80,
                    'estimated_minutes': 5, 'max_responses': 1000, 'status': 'active',
                },
                'questions': [
                    ('How often do you exercise per week?', 'multiple_choice',
                     ['Never', '1–2 times', '3–4 times', 'Every day']),
                    ('How would you rate your current health?', 'rating', []),
                    ('Do you have health insurance (HMO)?', 'boolean', []),
                    ('What is your biggest health challenge?', 'multiple_choice',
                     ['Stress & Mental health', 'Poor diet',
                      'Lack of exercise', 'Affordability of healthcare']),
                    ('How often do you visit a doctor?', 'multiple_choice',
                     ['When sick only', 'Once a year', 'Every 6 months', 'Rarely/Never']),
                    ('What health improvement would you most like to make?', 'text', []),
                ],
            },

            # ── 6 ─────────────────────────────────────────────────────────────
            {
                'meta': {
                    'title': 'E-commerce & Online Shopping',
                    'description': 'How do Nigerians shop online? Brands want to know.',
                    'category': 'consumer', 'points_reward': 65,
                    'estimated_minutes': 4, 'max_responses': 2500, 'status': 'active',
                    'is_sponsored': True, 'sponsor_name': 'ShopNG',
                },
                'questions': [
                    ('How often do you shop online?', 'multiple_choice',
                     ['Weekly', 'Monthly', 'A few times a year', 'Never']),
                    ('Which platform do you buy from most?', 'multiple_choice',
                     ['Jumia', 'Konga', 'Instagram / WhatsApp sellers',
                      'International sites (Amazon, etc.)']),
                    ('What is your biggest concern when shopping online?', 'multiple_choice',
                     ['Fake products', 'Delayed delivery',
                      'Payment security', 'No return policy']),
                    ('How do you prefer to pay online?', 'multiple_choice',
                     ['Debit card', 'Bank transfer', 'Pay on delivery', 'USSD']),
                    ('Have you ever been scammed shopping online?', 'boolean', []),
                    ('What would make you shop online more often?', 'text', []),
                ],
            },

            # ── 7 ─────────────────────────────────────────────────────────────
            {
                'meta': {
                    'title': 'Transportation & Commuting in Nigeria',
                    'description': 'How do Nigerians get around? Share your commute experience.',
                    'category': 'general', 'points_reward': 55,
                    'estimated_minutes': 3, 'max_responses': 2000, 'status': 'active',
                },
                'questions': [
                    ('What is your main mode of transport?', 'multiple_choice',
                     ['Personal car', 'Bus / BRT', 'Bike (Okada/Bolt rides)',
                      'Tricycle (Keke Napep)']),
                    ('How long is your average daily commute (one way)?', 'multiple_choice',
                     ['Under 30 minutes', '30–60 minutes',
                      '1–2 hours', 'Over 2 hours']),
                    ('Do you use ride-hailing apps (Bolt, Uber, inDrive)?', 'boolean', []),
                    ('Rate the state of transportation in your city (1–5)', 'rating', []),
                    ('What is your biggest transport frustration?', 'multiple_choice',
                     ['Traffic congestion', 'High cost of transport',
                      'Safety concerns', 'Unreliable public transport']),
                ],
            },

            # ── 8 ─────────────────────────────────────────────────────────────
            {
                'meta': {
                    'title': 'Nigerian Youth & Politics Survey',
                    'description': 'What do young Nigerians think about governance and the future?',
                    'category': 'general', 'points_reward': 90,
                    'estimated_minutes': 5, 'max_responses': 800, 'status': 'active',
                },
                'questions': [
                    ('Are you registered to vote?', 'boolean', []),
                    ('How do you rate the current Nigerian government?', 'rating', []),
                    ('What is the most important issue Nigeria needs to fix?', 'multiple_choice',
                     ['Insecurity & crime', 'Unemployment',
                      'Corruption', 'Poor infrastructure']),
                    ('Do you believe youth can change Nigeria\'s politics?', 'multiple_choice',
                     ['Yes, absolutely', 'Somewhat', 'I\'m not sure', 'No, the system is too corrupt']),
                    ('Would you consider running for a political office?', 'boolean', []),
                    ('What gives you hope about Nigeria\'s future?', 'text', []),
                ],
            },

            # ── 9 ─────────────────────────────────────────────────────────────
            {
                'meta': {
                    'title': 'Cryptocurrency & Investment Habits',
                    'description': 'Understanding how young Nigerians invest their money.',
                    'category': 'finance', 'points_reward': 100,
                    'estimated_minutes': 5, 'max_responses': 1200, 'status': 'active',
                    'is_sponsored': True, 'sponsor_name': 'CryptoNG',
                },
                'questions': [
                    ('Do you currently own any cryptocurrency?', 'boolean', []),
                    ('Which investment do you trust most?', 'multiple_choice',
                     ['Real estate', 'Cryptocurrency / Bitcoin',
                      'Stock market', 'Fixed deposits / Savings']),
                    ('How much do you save or invest monthly?', 'multiple_choice',
                     ['Nothing currently', 'Under ₦5,000',
                      '₦5,000–₦20,000', 'Over ₦20,000']),
                    ('Have you ever lost money to a Ponzi scheme?', 'boolean', []),
                    ('Rate your financial literacy (1 = Very low, 5 = Expert)', 'rating', []),
                    ('What financial advice would you give to other young Nigerians?', 'text', []),
                ],
            },

            # ── 10 ────────────────────────────────────────────────────────────
            {
                'meta': {
                    'title': 'Housing & Living Conditions Survey',
                    'description': 'Understanding the housing challenges faced by Nigerians.',
                    'category': 'general', 'points_reward': 70,
                    'estimated_minutes': 4, 'max_responses': 1500, 'status': 'active',
                },
                'questions': [
                    ('What type of housing do you currently live in?', 'multiple_choice',
                     ['Family house (renting)', 'My own apartment',
                      'Shared/face-me-I-face-you', 'Family/parents\' home']),
                    ('What percentage of your income goes to rent?', 'multiple_choice',
                     ['Under 20%', '20–40%', '40–60%', 'Over 60%']),
                    ('Do you have 24-hour electricity supply?', 'boolean', []),
                    ('Rate your overall living conditions (1–5)', 'rating', []),
                    ('In which city/state do you live?', 'multiple_choice',
                     ['Lagos', 'Abuja', 'Port Harcourt', 'Other city']),
                    ('What is the biggest housing challenge in Nigeria?', 'text', []),
                ],
            },
        ]

        for data in surveys:
            title = data['meta']['title']
            if Survey.objects.filter(title=title).exists():
                self.stdout.write(f'  skip (exists): {title}')
                continue
            survey = Survey.objects.create(**data['meta'])
            for i, (text, qtype, options) in enumerate(data['questions']):
                sq = SurveyQuestion.objects.create(
                    survey=survey, text=text,
                    question_type=qtype, order=i + 1
                )
                for j, opt in enumerate(options):
                    SurveyOption.objects.create(question=sq, text=opt, order=j + 1)
            self.stdout.write(f'  ✓ Survey: {title}')
            added += 1

        self.stdout.write(f'\n  → {added} new surveys added (total: {Survey.objects.count()})')
        return added

    # ─────────────────────────────────────────────────────────── QUIZZES ──────

    def add_quizzes(self):
        from quizzes.models import Quiz, QuizQuestion, QuizCategory
        added = 0

        def get_cat(slug):
            return QuizCategory.objects.filter(slug=slug).first()

        quizzes = [

            # ── NIGERIA & AFRICA ──────────────────────────────────────────────
            {
                'meta': dict(title='Nigerian History & Independence',
                             category=get_cat('nigeria-africa'), difficulty='medium',
                             description='Test your knowledge of Nigeria\'s rich history.',
                             time_limit_seconds=30, points_per_correct=12, bonus_points=25),
                'questions': [
                    ('Who was Nigeria\'s first Prime Minister at independence?',
                     'Nnamdi Azikiwe', 'Tafawa Balewa', 'Obafemi Awolowo', 'Ahmadu Bello', 'B',
                     'Sir Abubakar Tafawa Balewa was Nigeria\'s first and only Prime Minister.'),
                    ('In what year was Nigeria declared a Republic?',
                     '1960', '1963', '1966', '1970', 'B',
                     'Nigeria became a republic on October 1, 1963.'),
                    ('Which city hosted the first capital of Nigeria?',
                     'Abuja', 'Enugu', 'Kaduna', 'Lagos', 'D',
                     'Lagos was Nigeria\'s capital from 1914 until 1991.'),
                    ('What does "Nigeria" mean?',
                     'Land of many rivers', 'Niger Area', 'Black people', 'Great water', 'B',
                     '"Nigeria" was coined by Flora Shaw, meaning the area around the Niger River.'),
                    ('Who discovered oil in Nigeria commercially in 1956?',
                     'Shell-BP', 'Chevron', 'ExxonMobil', 'Total', 'A',
                     'Shell-BP discovered commercial quantities of oil at Oloibiri, Bayelsa State in 1956.'),
                ],
            },

            {
                'meta': dict(title='Nigerian States & Geography',
                             category=get_cat('nigeria-africa'), difficulty='easy',
                             description='How well do you know Nigeria\'s 36 states?',
                             time_limit_seconds=25, points_per_correct=10, bonus_points=20),
                'questions': [
                    ('How many states does Nigeria have?',
                     '30', '34', '36', '38', 'C',
                     'Nigeria has 36 states plus the Federal Capital Territory (Abuja).'),
                    ('Which Nigerian state is known as the "Food Basket of the Nation"?',
                     'Benue', 'Kogi', 'Plateau', 'Taraba', 'A',
                     'Benue State is called the Food Basket of the Nation due to its rich agricultural output.'),
                    ('What is the smallest state in Nigeria by area?',
                     'Lagos', 'Anambra', 'Imo', 'Ekiti', 'A',
                     'Lagos is the smallest state by area but the most populous.'),
                    ('Which state is known as the "Gateway State"?',
                     'Ogun', 'Ondo', 'Ekiti', 'Kwara', 'A',
                     'Ogun State is called the Gateway State because it borders Lagos and Benin Republic.'),
                    ('The "Venice of Africa" refers to which Nigerian city?',
                     'Calabar', 'Warri', 'Ganye', 'Makoko (Lagos)', 'D',
                     'Makoko in Lagos is often called the Venice of Africa due to its stilted houses on water.'),
                ],
            },

            {
                'meta': dict(title='African Leaders & Legends',
                             category=get_cat('nigeria-africa'), difficulty='hard',
                             description='Know your African history-makers.',
                             time_limit_seconds=30, points_per_correct=15, bonus_points=35),
                'questions': [
                    ('Who was the first President of Ghana?',
                     'Kofi Annan', 'Kwame Nkrumah', 'John Mahama', 'Jerry Rawlings', 'B',
                     'Kwame Nkrumah became Ghana\'s first President in 1960.'),
                    ('Nelson Mandela served as South Africa\'s President from 1994 to…?',
                     '1998', '1999', '2000', '2002', 'B',
                     'Nelson Mandela served as President from May 1994 to June 1999.'),
                    ('Which African country was never colonised by a European power?',
                     'Morocco', 'Ethiopia', 'Liberia', 'Tanzania', 'B',
                     'Ethiopia successfully resisted colonisation, defeating Italy at the Battle of Adwa in 1896.'),
                    ('Who wrote the novel "Things Fall Apart"?',
                     'Wole Soyinka', 'Chimamanda Adichie', 'Chinua Achebe', 'Ben Okri', 'C',
                     'Chinua Achebe wrote "Things Fall Apart" published in 1958.'),
                    ('In which African country is the Serengeti National Park located?',
                     'Kenya', 'Uganda', 'Tanzania', 'Zimbabwe', 'C',
                     'The Serengeti National Park is in Tanzania.'),
                ],
            },

            # ── GENERAL KNOWLEDGE ────────────────────────────────────────────
            {
                'meta': dict(title='World Geography Basics',
                             category=get_cat('general-knowledge'), difficulty='easy',
                             description='Test your knowledge of countries, capitals and continents.',
                             time_limit_seconds=25, points_per_correct=10, bonus_points=15),
                'questions': [
                    ('What is the largest continent by area?',
                     'Africa', 'Asia', 'North America', 'Europe', 'B',
                     'Asia is the largest continent, covering about 44.6 million km².'),
                    ('What is the capital of France?',
                     'Lyon', 'Marseille', 'Paris', 'Nice', 'C',
                     'Paris is the capital and largest city of France.'),
                    ('Which country has the longest coastline in the world?',
                     'Russia', 'Australia', 'Canada', 'USA', 'C',
                     'Canada has the world\'s longest coastline at over 202,000 km.'),
                    ('What is the smallest country in the world?',
                     'Monaco', 'San Marino', 'Vatican City', 'Liechtenstein', 'C',
                     'Vatican City is the world\'s smallest country at just 0.44 km².'),
                    ('The Amazon River is in which continent?',
                     'Africa', 'Asia', 'South America', 'North America', 'C',
                     'The Amazon River runs through South America, mainly in Brazil.'),
                ],
            },

            {
                'meta': dict(title='Famous Inventions & Inventors',
                             category=get_cat('general-knowledge'), difficulty='medium',
                             description='Who invented what? Test your general knowledge.',
                             time_limit_seconds=28, points_per_correct=12, bonus_points=20),
                'questions': [
                    ('Who invented the telephone?',
                     'Thomas Edison', 'Alexander Graham Bell', 'Nikola Tesla', 'Guglielmo Marconi', 'B',
                     'Alexander Graham Bell invented the telephone and received the patent in 1876.'),
                    ('Which country invented the internet?',
                     'UK', 'Japan', 'USA', 'Germany', 'C',
                     'The internet (ARPANET) was developed in the USA in the late 1960s.'),
                    ('Who invented the light bulb?',
                     'Nikola Tesla', 'Thomas Edison', 'Alexander Fleming', 'James Watt', 'B',
                     'Thomas Edison invented the practical incandescent light bulb in 1879.'),
                    ('What was the first country to send a man to the moon?',
                     'Russia', 'China', 'USA', 'UK', 'C',
                     'The USA landed Apollo 11 on the moon on July 20, 1969.'),
                    ('Who painted the Mona Lisa?',
                     'Michelangelo', 'Pablo Picasso', 'Leonardo da Vinci', 'Vincent van Gogh', 'C',
                     'Leonardo da Vinci painted the Mona Lisa between 1503 and 1519.'),
                ],
            },

            {
                'meta': dict(title='Food & Cuisine Around the World',
                             category=get_cat('general-knowledge'), difficulty='easy',
                             description='How much do you know about global food culture?',
                             time_limit_seconds=25, points_per_correct=10, bonus_points=15,
                             is_daily=True),
                'questions': [
                    ('Which country is Sushi originally from?',
                     'China', 'Korea', 'Japan', 'Thailand', 'C',
                     'Sushi originated in Japan, evolving from a method of preserving fish in rice.'),
                    ('Pizza was originally created in which country?',
                     'USA', 'France', 'Spain', 'Italy', 'D',
                     'Pizza originated in Naples, Italy in the 18th century.'),
                    ('What is the main ingredient in Nigerian Egusi soup?',
                     'Melon seeds', 'Palm nut', 'Groundnut', 'Locust bean', 'A',
                     'Egusi soup is made from ground melon seeds as its primary ingredient.'),
                    ('Which fruit is known as the "King of Fruits"?',
                     'Mango', 'Pineapple', 'Durian', 'Jackfruit', 'C',
                     'Durian is widely known as the King of Fruits in Southeast Asia.'),
                    ('Jollof Rice is believed to have originated from which country?',
                     'Nigeria', 'Ghana', 'Senegal', 'Cameroon', 'C',
                     'Jollof Rice is thought to have originated in Senegal from the Wolof people.'),
                ],
            },

            # ── SCIENCE & TECH ───────────────────────────────────────────────
            {
                'meta': dict(title='Basic Science & Nature',
                             category=get_cat('science-tech'), difficulty='easy',
                             description='Brush up on your science fundamentals.',
                             time_limit_seconds=28, points_per_correct=10, bonus_points=20),
                'questions': [
                    ('What is the chemical symbol for water?',
                     'WA', 'H2O', 'HO2', 'W', 'B',
                     'Water\'s chemical formula is H₂O — 2 hydrogen atoms and 1 oxygen atom.'),
                    ('What planet is closest to the sun?',
                     'Venus', 'Earth', 'Mars', 'Mercury', 'D',
                     'Mercury is the closest planet to the sun.'),
                    ('How many bones are in the adult human body?',
                     '196', '206', '216', '226', 'B',
                     'An adult human body has 206 bones.'),
                    ('What is the powerhouse of the cell?',
                     'Nucleus', 'Ribosome', 'Mitochondria', 'Vacuole', 'C',
                     'The mitochondria is often called the powerhouse of the cell because it generates energy (ATP).'),
                    ('What gas do plants absorb from the atmosphere?',
                     'Oxygen', 'Nitrogen', 'Carbon Dioxide', 'Hydrogen', 'C',
                     'Plants absorb carbon dioxide (CO₂) during photosynthesis.'),
                ],
            },

            {
                'meta': dict(title='Smartphones & Modern Tech',
                             category=get_cat('science-tech'), difficulty='medium',
                             description='How tech-savvy are you in the smartphone era?',
                             time_limit_seconds=25, points_per_correct=12, bonus_points=25),
                'questions': [
                    ('What does "AI" stand for?',
                     'Automated Intelligence', 'Artificial Intelligence',
                     'Advanced Internet', 'Android Interface', 'B',
                     'AI stands for Artificial Intelligence.'),
                    ('Which company makes the iPhone?',
                     'Samsung', 'Google', 'Apple', 'Sony', 'C',
                     'The iPhone is made by Apple Inc.'),
                    ('What does "5G" refer to?',
                     '5th generation WiFi', '5th generation mobile network',
                     '5 gigabytes', '5th generation GPS', 'B',
                     '5G refers to the fifth generation of mobile network technology.'),
                    ('What is the full meaning of "URL"?',
                     'Uniform Resource Locator', 'Universal Resource Link',
                     'Unified Resource Location', 'User Reference Line', 'A',
                     'URL stands for Uniform Resource Locator — the address of a web page.'),
                    ('Which programming language is primarily used for Android apps?',
                     'Swift', 'Python', 'Kotlin / Java', 'Ruby', 'C',
                     'Android apps are primarily built with Kotlin (modern) or Java (legacy).'),
                ],
            },

            {
                'meta': dict(title='Space & The Universe',
                             category=get_cat('science-tech'), difficulty='hard',
                             description='From stars to black holes — how much do you know?',
                             time_limit_seconds=35, points_per_correct=15, bonus_points=40),
                'questions': [
                    ('How long does light from the sun take to reach Earth?',
                     'About 2 minutes', 'About 8 minutes', 'About 20 minutes', 'About 1 hour', 'B',
                     'Sunlight takes approximately 8 minutes and 20 seconds to travel from the sun to Earth.'),
                    ('What is the name of our galaxy?',
                     'Andromeda', 'The Milky Way', 'The Solar Way', 'Cosmos', 'B',
                     'Our galaxy is called the Milky Way.'),
                    ('Which planet has the most moons?',
                     'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'B',
                     'Saturn currently holds the record with 146 confirmed moons as of 2024.'),
                    ('What is a light-year?',
                     'The time light travels in a year', 'The distance light travels in a year',
                     'The brightness of a star', 'A unit of space time', 'B',
                     'A light-year is the distance that light travels in one year — about 9.46 trillion km.'),
                    ('Who was the first human to travel to space?',
                     'Neil Armstrong', 'Buzz Aldrin', 'Yuri Gagarin', 'Alan Shepard', 'C',
                     'Yuri Gagarin of the Soviet Union was the first human in space on April 12, 1961.'),
                ],
            },

            # ── SPORTS ───────────────────────────────────────────────────────
            {
                'meta': dict(title='Football (Soccer) World Cup',
                             category=get_cat('sports'), difficulty='medium',
                             description='The beautiful game — how much do you know?',
                             time_limit_seconds=28, points_per_correct=12, bonus_points=25),
                'questions': [
                    ('Which country has won the FIFA World Cup the most times?',
                     'Germany', 'Argentina', 'Brazil', 'Italy', 'C',
                     'Brazil has won the FIFA World Cup a record 5 times.'),
                    ('Who won the 2022 FIFA World Cup?',
                     'France', 'Brazil', 'Argentina', 'Croatia', 'C',
                     'Argentina won the 2022 World Cup in Qatar, defeating France in the final.'),
                    ('How many players are on a football team (on the pitch)?',
                     '9', '10', '11', '12', 'C',
                     'Each football team has 11 players on the pitch at one time.'),
                    ('Who holds the record for most FIFA World Cup goals?',
                     'Ronaldo (Brazil)', 'Miroslav Klose', 'Just Fontaine', 'Gerd Müller', 'B',
                     'Miroslav Klose of Germany scored 16 World Cup goals — the all-time record.'),
                    ('Super Eagles is the nickname of which country\'s football team?',
                     'Ghana', 'Cameroon', 'Nigeria', 'Senegal', 'C',
                     'The Super Eagles is the nickname of the Nigerian national football team.'),
                ],
            },

            {
                'meta': dict(title='Nigerian Sports Heroes',
                             category=get_cat('sports'), difficulty='easy',
                             description='Celebrate Nigeria\'s greatest sporting legends.',
                             time_limit_seconds=25, points_per_correct=10, bonus_points=20),
                'questions': [
                    ('Which Nigerian sprinter won Olympic gold at Atlanta 1996?',
                     'Blessing Okagbare', 'Falilat Ogunkoya', 'Mary Onyali', 'Chioma Ajunwa', 'D',
                     'Chioma Ajunwa won gold in the long jump at the 1996 Atlanta Olympics.'),
                    ('In which sport did Hakeem Olajuwon achieve global fame?',
                     'Football', 'Boxing', 'Basketball', 'Athletics', 'C',
                     'Hakeem Olajuwon was a legendary NBA basketball player with the Houston Rockets.'),
                    ('Which Nigerian boxer was known as "The Lion"?',
                     'Samuel Peter', 'Dick Tiger', 'Bash Ali', 'David Izon', 'B',
                     'Dick Tiger was a world middleweight and light heavyweight boxing champion.'),
                    ('Nigeria\'s greatest football legend Jay-Jay Okocha played for which club the longest?',
                     'PSG', 'Bolton Wanderers', 'Fenerbahce', 'Eintracht Frankfurt', 'A',
                     'Jay-Jay Okocha played for Paris Saint-Germain (PSG) from 1998 to 2002.'),
                    ('How many times has Nigeria won the Africa Cup of Nations?',
                     '2', '3', '4', '5', 'B',
                     'Nigeria has won the Africa Cup of Nations 3 times (1980, 1994, 2013).'),
                ],
            },

            # ── JAMB PREP ────────────────────────────────────────────────────
            {
                'meta': dict(title='JAMB English Language Practice',
                             category=get_cat('jamb-prep'), difficulty='medium',
                             description='Boost your UTME English score with these practice questions.',
                             time_limit_seconds=35, points_per_correct=15, bonus_points=30),
                'questions': [
                    ('Choose the word closest in meaning to "Benevolent":',
                     'Cruel', 'Generous', 'Timid', 'Foolish', 'B',
                     '"Benevolent" means generous, kind and charitable.'),
                    ('Identify the correct sentence:',
                     'She don\'t like rice', 'She doesn\'t likes rice',
                     'She doesn\'t like rice', 'She not like rice', 'C',
                     'The correct sentence uses the third-person singular: "She doesn\'t like rice."'),
                    ('What figure of speech is used: "The moon smiled down at us"?',
                     'Simile', 'Personification', 'Metaphor', 'Hyperbole', 'B',
                     'Personification gives human qualities (smiling) to a non-human object (the moon).'),
                    ('Choose the word opposite in meaning to "Verbose":',
                     'Talkative', 'Wordy', 'Concise', 'Lengthy', 'C',
                     '"Verbose" means using more words than needed. Its antonym is "Concise".'),
                    ('The plural of "phenomenon" is:',
                     'Phenomenons', 'Phenomenas', 'Phenomena', 'Phenomenon', 'C',
                     'The correct plural of phenomenon is "phenomena" (from Greek).'),
                ],
            },

            {
                'meta': dict(title='JAMB Mathematics Practice',
                             category=get_cat('jamb-prep'), difficulty='hard',
                             description='Sharpen your UTME maths skills with these exam-style questions.',
                             time_limit_seconds=40, points_per_correct=18, bonus_points=40),
                'questions': [
                    ('Simplify: 2³ × 2⁴',
                     '2⁷', '2¹²', '4⁷', '8⁷', 'A',
                     'When multiplying powers with the same base, add the exponents: 2³ × 2⁴ = 2⁷ = 128.'),
                    ('What is 15% of 200?',
                     '25', '30', '35', '40', 'B',
                     '15% of 200 = (15/100) × 200 = 30.'),
                    ('If x + 5 = 12, what is x?',
                     '5', '6', '7', '8', 'C',
                     'x + 5 = 12 → x = 12 - 5 = 7.'),
                    ('What is the area of a rectangle with length 8cm and width 5cm?',
                     '26cm²', '30cm²', '40cm²', '13cm²', 'C',
                     'Area of rectangle = length × width = 8 × 5 = 40cm².'),
                    ('Find the simple interest on ₦5,000 at 10% per annum for 2 years.',
                     '₦500', '₦750', '₦1,000', '₦1,500', 'C',
                     'SI = (P × R × T) / 100 = (5000 × 10 × 2) / 100 = ₦1,000.'),
                ],
            },

            # ── ENTERTAINMENT ────────────────────────────────────────────────
            {
                'meta': dict(title='Nollywood & Nigerian Movies',
                             category=get_cat('entertainment'), difficulty='easy',
                             description='How much do you know about Nollywood, the world\'s 2nd largest film industry?',
                             time_limit_seconds=25, points_per_correct=10, bonus_points=20),
                'questions': [
                    ('Nollywood is the film industry of which country?',
                     'Ghana', 'Kenya', 'Nigeria', 'South Africa', 'C',
                     'Nollywood refers to Nigeria\'s film industry, one of the largest in the world.'),
                    ('Which Nollywood actor is known as "Mr. Ibu"?',
                     'Kanayo O. Kanayo', 'Pete Edochie', 'John Okafor', 'Obi Osotule', 'C',
                     'John Okafor is widely known by his stage name "Mr. Ibu" in Nollywood.'),
                    ('Which Nigerian movie was the first to be screened at the Oscars?',
                     'King of Boys', 'Lionheart', 'The Wedding Party', 'October 1', 'B',
                     '"Lionheart" (2018), directed by Genevieve Nnaji, was Nigeria\'s first Oscar submission.'),
                    ('Who directed the critically acclaimed film "Omo Ghetto"?',
                     'EbonyLife', 'Funke Akindele', 'Kemi Adetiba', 'Toyin Abraham', 'B',
                     '"Omo Ghetto" was directed by Funke Akindele.'),
                    ('Which streaming service released the Nollywood show "Blood Sisters"?',
                     'Amazon Prime', 'Disney+', 'Netflix', 'Showmax', 'C',
                     '"Blood Sisters" was released on Netflix in 2022 as a Nollywood original series.'),
                ],
            },

            {
                'meta': dict(title='Afrobeats & Nigerian Music',
                             category=get_cat('entertainment'), difficulty='medium',
                             description='From Fela to the modern Afrobeats wave — test your music knowledge.',
                             time_limit_seconds=28, points_per_correct=12, bonus_points=25,
                             is_daily=True),
                'questions': [
                    ('Who is known as the "Father of Afrobeats"?',
                     'King Sunny Ade', 'Fela Kuti', 'Ebenezer Obey', 'Miriam Makeba', 'B',
                     'Fela Anikulapo Kuti created and popularised Afrobeat music from Lagos.'),
                    ('Burna Boy won a Grammy Award in which category?',
                     'Best World Music Album', 'Best African Music', 'Best Global Music Album',
                     'Best Pop Album', 'C',
                     'Burna Boy won the Grammy for Best Global Music Album for "Twice as Tall" in 2021.'),
                    ('Which Nigerian artist released the hit "Come Closer"?',
                     'Davido', 'Wizkid', 'Tekno', 'Mr Eazi', 'B',
                     '"Come Closer" is a 2017 hit by Wizkid featuring Drake.'),
                    ('What is the real name of the artist known as "Davido"?',
                     'David Adeleke', 'David Okafor', 'Dapo Adeleke', 'David Akinmolayan', 'A',
                     'Davido\'s real name is David Adedeji Adeleke.'),
                    ('Which Nigerian city is most associated with the rise of Afrobeats?',
                     'Abuja', 'Kano', 'Port Harcourt', 'Lagos', 'D',
                     'Lagos, particularly areas like Surulere and Lekki, is the birthplace of modern Afrobeats.'),
                ],
            },
        ]

        for data in quizzes:
            if data['meta']['category'] is None:
                self.stdout.write(f'  skip (no category): {data["meta"]["title"]}')
                continue
            title = data['meta']['title']
            if Quiz.objects.filter(title=title).exists():
                self.stdout.write(f'  skip (exists): {title}')
                continue
            quiz = Quiz.objects.create(**data['meta'])
            for i, q in enumerate(data['questions']):
                QuizQuestion.objects.create(
                    quiz=quiz, text=q[0],
                    option_a=q[1], option_b=q[2],
                    option_c=q[3], option_d=q[4],
                    correct_answer=q[5], explanation=q[6],
                    order=i + 1
                )
            self.stdout.write(f'  ✓ Quiz: {title} ({len(data["questions"])} questions)')
            added += 1

        self.stdout.write(f'\n  → {added} new quizzes added (total: {Quiz.objects.count()})')
        return added

    # ──────────────────────────────────────────────────────────── GAMES ───────

    def add_games(self):
        from games.models import Game
        added = 0

        games = [
            {
                'title': 'Naija Trivia Blitz',
                'game_type': 'logic',
                'difficulty': 'easy',
                'description': 'Answer rapid-fire questions about Nigeria — cities, culture, food and more!',
                'instructions': 'Pick the correct answer before time runs out. 10 questions, go fast!',
                'points_reward': 30,
                'time_limit_seconds': 60,
            },
            {
                'title': 'Emoji Puzzle Challenge',
                'game_type': 'puzzle',
                'difficulty': 'medium',
                'description': 'Decode the emoji combinations to guess famous Nigerian movies, songs and phrases!',
                'instructions': 'Look at the emoji clues and type or select the correct answer.',
                'points_reward': 40,
                'time_limit_seconds': 120,
            },
            {
                'title': 'Number Sequence Master',
                'game_type': 'math',
                'difficulty': 'hard',
                'description': 'Find the missing number in increasingly complex sequences.',
                'instructions': 'Study the pattern and pick the number that comes next. 12 levels of difficulty!',
                'points_reward': 55,
                'time_limit_seconds': 90,
            },
            {
                'title': 'Capital Cities Africa',
                'game_type': 'word',
                'difficulty': 'medium',
                'description': 'Match African countries with their capital cities against the clock.',
                'instructions': 'Type the capital city of each African country shown. Spelling counts!',
                'points_reward': 35,
                'time_limit_seconds': 90,
            },
        ]

        for data in games:
            if Game.objects.filter(title=data['title']).exists():
                self.stdout.write(f'  skip (exists): {data["title"]}')
                continue
            Game.objects.create(**data)
            self.stdout.write(f'  ✓ Game: {data["title"]}')
            added += 1

        self.stdout.write(f'\n  → {added} new games added (total: {Game.objects.count()})')
        return added
