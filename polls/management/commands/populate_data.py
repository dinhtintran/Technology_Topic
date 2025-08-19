from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from polls.models import Question, Choice, Category, Tag, Author, QuestionExtended


class Command(BaseCommand):
    help = 'Populate database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            QuestionExtended.objects.all().delete()
            Question.objects.all().delete()
            Category.objects.all().delete()
            Tag.objects.all().delete()
            Author.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Data cleared!'))

        # Tạo Categories
        categories_data = [
            {'name': 'Technology', 'description': 'Questions about technology and programming'},
            {'name': 'Science', 'description': 'Scientific questions and facts'},
            {'name': 'Sports', 'description': 'Sports related questions'},
            {'name': 'Entertainment', 'description': 'Movies, music, and entertainment'},
            {'name': 'General Knowledge', 'description': 'General knowledge questions'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')

        # Tạo Tags
        tags_data = [
            {'name': 'Python', 'color': '#3776ab'},
            {'name': 'JavaScript', 'color': '#f7df1e'},
            {'name': 'Web Development', 'color': '#61dafb'},
            {'name': 'AI/ML', 'color': '#ff6b6b'},
            {'name': 'Database', 'color': '#4ecdc4'},
            {'name': 'Physics', 'color': '#ffe66d'},
            {'name': 'Chemistry', 'color': '#a8e6cf'},
            {'name': 'Football', 'color': '#ffd93d'},
            {'name': 'Basketball', 'color': '#ff8b94'},
            {'name': 'Movies', 'color': '#b4a7d6'},
        ]

        tags = []
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_data['name'],
                defaults={'color': tag_data['color']}
            )
            tags.append(tag)
            if created:
                self.stdout.write(f'Created tag: {tag.name}')

        # Tạo Authors
        authors_data = [
            {'name': 'Alice Johnson', 'email': 'alice@example.com', 'bio': 'Tech enthusiast and educator'},
            {'name': 'Bob Smith', 'email': 'bob@example.com', 'bio': 'Science teacher and researcher'},
            {'name': 'Carol Davis', 'email': 'carol@example.com', 'bio': 'Sports journalist'},
            {'name': 'David Wilson', 'email': 'david@example.com', 'bio': 'Entertainment blogger'},
            {'name': 'Eva Brown', 'email': 'eva@example.com', 'bio': 'Quiz master and trivia expert'},
        ]

        authors = []
        for author_data in authors_data:
            author, created = Author.objects.get_or_create(
                email=author_data['email'],
                defaults={
                    'name': author_data['name'],
                    'bio': author_data['bio']
                }
            )
            authors.append(author)
            if created:
                self.stdout.write(f'Created author: {author.name}')

        # Tạo Questions với Choices
        questions_data = [
            {
                'text': 'What is the most popular programming language in 2024?',
                'choices': ['Python', 'JavaScript', 'Java', 'C++'],
                'category': 'Technology',
                'difficulty': 'easy',
                'tags': ['Python', 'JavaScript'],
            },
            {
                'text': 'Which planet is known as the Red Planet?',
                'choices': ['Venus', 'Mars', 'Jupiter', 'Saturn'],
                'category': 'Science',
                'difficulty': 'easy',
                'tags': ['Physics'],
            },
            {
                'text': 'How many players are on a basketball team on the court at one time?',
                'choices': ['4', '5', '6', '7'],
                'category': 'Sports',
                'difficulty': 'easy',
                'tags': ['Basketball'],
            },
            {
                'text': 'What does SQL stand for?',
                'choices': ['Structured Query Language', 'Simple Query Language', 'Standard Query Language', 'System Query Language'],
                'category': 'Technology',
                'difficulty': 'medium',
                'tags': ['Database'],
            },
            {
                'text': 'Which movie won the Academy Award for Best Picture in 2023?',
                'choices': ['Everything Everywhere All at Once', 'Top Gun: Maverick', 'The Banshees of Inisherin', 'Tar'],
                'category': 'Entertainment',
                'difficulty': 'hard',
                'tags': ['Movies'],
            },
        ]

        for i, question_data in enumerate(questions_data):
            # Tạo random pub_date trong 30 ngày qua
            days_ago = random.randint(0, 30)
            pub_date = timezone.now() - timedelta(days=days_ago)
            
            question = Question.objects.create(
                question_text=question_data['text'],
                pub_date=pub_date
            )

            # Tạo choices
            for j, choice_text in enumerate(question_data['choices']):
                # Choice đầu tiên sẽ có nhiều vote nhất
                votes = random.randint(10, 50) if j == 0 else random.randint(0, 20)
                Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    votes=votes
                )

            # Tạo QuestionExtended
            category = Category.objects.get(name=question_data['category'])
            author = random.choice(authors)
            
            question_extended = QuestionExtended.objects.create(
                question=question,
                category=category,
                author=author,
                difficulty_level=question_data['difficulty'],
                is_featured=random.choice([True, False]),
                view_count=random.randint(10, 1000)
            )

            # Thêm tags
            question_tags = [Tag.objects.get(name=tag_name) for tag_name in question_data['tags']]
            question_extended.tags.set(question_tags)

            self.stdout.write(f'Created question: {question.question_text}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(questions_data)} questions with choices and extended data!'
            )
        )
