from django.core.management.base import BaseCommand
from polls.models import Question, Choice, Category, Tag, Author, QuestionExtended


class Command(BaseCommand):
    help = 'Display statistics about the data in the database'

    def handle(self, *args, **options):
        # Statistics
        question_count = Question.objects.count()
        choice_count = Choice.objects.count()
        category_count = Category.objects.count()
        tag_count = Tag.objects.count()
        author_count = Author.objects.count()
        extended_count = QuestionExtended.objects.count()

        self.stdout.write(self.style.SUCCESS('=== DATABASE STATISTICS ==='))
        self.stdout.write(f'Questions: {question_count}')
        self.stdout.write(f'Choices: {choice_count}')
        self.stdout.write(f'Categories: {category_count}')
        self.stdout.write(f'Tags: {tag_count}')
        self.stdout.write(f'Authors: {author_count}')
        self.stdout.write(f'Extended Questions: {extended_count}')

        # Show questions with their relationships
        self.stdout.write('\n' + self.style.SUCCESS('=== QUESTIONS WITH RELATIONSHIPS ==='))
        for question in Question.objects.all():
            self.stdout.write(f'\nQuestion: {question.question_text}')
            self.stdout.write(f'Published: {question.pub_date}')
            
            # Choices
            choices = question.choice_set.all()
            self.stdout.write(f'Choices ({choices.count()}):')
            for choice in choices:
                self.stdout.write(f'  - {choice.choice_text} ({choice.votes} votes)')
            
            # Extended info
            try:
                extended = question.extended
                self.stdout.write(f'Category: {extended.category.name if extended.category else "None"}')
                self.stdout.write(f'Author: {extended.author.name}')
                self.stdout.write(f'Difficulty: {extended.difficulty_level}')
                self.stdout.write(f'Featured: {extended.is_featured}')
                self.stdout.write(f'View Count: {extended.view_count}')
                tags = extended.tags.all()
                if tags:
                    tag_names = ', '.join([tag.name for tag in tags])
                    self.stdout.write(f'Tags: {tag_names}')
            except QuestionExtended.DoesNotExist:
                self.stdout.write('No extended information available')
