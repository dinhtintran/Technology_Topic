from django.core.management.base import BaseCommand
from django.db.models import Count, Q, Avg
from polls.models import Question, Choice, Category, Tag, Author, QuestionExtended


class Command(BaseCommand):
    help = 'Demonstrate various Django ORM query relationships'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== DJANGO ORM RELATIONSHIP QUERIES DEMO ===\n'))

        # 1. FORWARD RELATIONSHIPS (Từ model có ForeignKey đến model được tham chiếu)
        self.stdout.write(self.style.WARNING('1. FORWARD RELATIONSHIPS'))
        self.stdout.write('=' * 50)
        
        # QuestionExtended -> Question (OneToOne forward)
        self.stdout.write('\na) OneToOne Forward: QuestionExtended -> Question')
        extended_questions = QuestionExtended.objects.all()
        for ext_q in extended_questions[:3]:
            self.stdout.write(f'Extended Question ID {ext_q.id} -> Question: "{ext_q.question.question_text}"')
        
        # QuestionExtended -> Category (ForeignKey forward)
        self.stdout.write('\nb) ForeignKey Forward: QuestionExtended -> Category')
        for ext_q in extended_questions[:3]:
            category_name = ext_q.category.name if ext_q.category else "No category"
            self.stdout.write(f'Question "{ext_q.question.question_text}" -> Category: {category_name}')
        
        # QuestionExtended -> Author (ForeignKey forward)
        self.stdout.write('\nc) ForeignKey Forward: QuestionExtended -> Author')
        for ext_q in extended_questions[:3]:
            self.stdout.write(f'Question "{ext_q.question.question_text}" -> Author: {ext_q.author.name}')
        
        # QuestionExtended -> Tags (ManyToMany forward)
        self.stdout.write('\nd) ManyToMany Forward: QuestionExtended -> Tags')
        for ext_q in extended_questions[:3]:
            tags = ext_q.tags.all()
            tag_names = ', '.join([tag.name for tag in tags]) if tags else "No tags"
            self.stdout.write(f'Question "{ext_q.question.question_text}" -> Tags: {tag_names}')

        # 2. REVERSE RELATIONSHIPS (Từ model được tham chiếu về model có ForeignKey)
        self.stdout.write(f'\n\n{self.style.WARNING("2. REVERSE RELATIONSHIPS")}')
        self.stdout.write('=' * 50)
        
        # Question -> QuestionExtended (OneToOne reverse)
        self.stdout.write('\na) OneToOne Reverse: Question -> QuestionExtended')
        questions = Question.objects.all()[:3]
        for question in questions:
            try:
                extended = question.extended
                self.stdout.write(f'Question "{question.question_text}" -> Extended info: Category={extended.category}, Difficulty={extended.difficulty_level}')
            except QuestionExtended.DoesNotExist:
                self.stdout.write(f'Question "{question.question_text}" -> No extended info')
        
        # Question -> Choices (ForeignKey reverse)
        self.stdout.write('\nb) ForeignKey Reverse: Question -> Choices')
        for question in questions:
            choices = question.choice_set.all()
            self.stdout.write(f'Question "{question.question_text}" has {choices.count()} choices:')
            for choice in choices:
                self.stdout.write(f'  - {choice.choice_text} ({choice.votes} votes)')
        
        # Category -> QuestionExtended (ForeignKey reverse)
        self.stdout.write('\nc) ForeignKey Reverse: Category -> QuestionExtended')
        categories = Category.objects.all()[:3]
        for category in categories:
            questions_in_category = category.questionextended_set.all()
            self.stdout.write(f'Category "{category.name}" has {questions_in_category.count()} questions:')
            for ext_q in questions_in_category:
                self.stdout.write(f'  - {ext_q.question.question_text}')
        
        # Author -> QuestionExtended (ForeignKey reverse)
        self.stdout.write('\nd) ForeignKey Reverse: Author -> QuestionExtended')
        authors = Author.objects.all()[:3]
        for author in authors:
            author_questions = author.questionextended_set.all()
            self.stdout.write(f'Author "{author.name}" has {author_questions.count()} questions:')
            for ext_q in author_questions:
                self.stdout.write(f'  - {ext_q.question.question_text}')
        
        # Tag -> QuestionExtended (ManyToMany reverse)
        self.stdout.write('\ne) ManyToMany Reverse: Tag -> QuestionExtended')
        tags = Tag.objects.all()[:3]
        for tag in tags:
            tagged_questions = tag.questionextended_set.all()
            self.stdout.write(f'Tag "{tag.name}" is used in {tagged_questions.count()} questions:')
            for ext_q in tagged_questions:
                self.stdout.write(f'  - {ext_q.question.question_text}')

        # 3. COMPLEX QUERIES WITH JOINS
        self.stdout.write(f'\n\n{self.style.WARNING("3. COMPLEX QUERIES WITH JOINS")}')
        self.stdout.write('=' * 50)
        
        # Select related (giảm số lượng database queries)
        self.stdout.write('\na) Using select_related for ForeignKey/OneToOne:')
        extended_with_related = QuestionExtended.objects.select_related(
            'question', 'category', 'author'
        ).all()[:3]
        for ext_q in extended_with_related:
            self.stdout.write(f'Question: "{ext_q.question.question_text}", Category: {ext_q.category.name if ext_q.category else "None"}, Author: {ext_q.author.name}')
        
        # Prefetch related (cho ManyToMany và reverse ForeignKey)
        self.stdout.write('\nb) Using prefetch_related for ManyToMany:')
        extended_with_tags = QuestionExtended.objects.prefetch_related('tags').all()[:3]
        for ext_q in extended_with_tags:
            tag_names = ', '.join([tag.name for tag in ext_q.tags.all()])
            self.stdout.write(f'Question: "{ext_q.question.question_text}", Tags: {tag_names if tag_names else "No tags"}')
        
        # 4. AGGREGATION QUERIES
        self.stdout.write(f'\n\n{self.style.WARNING("4. AGGREGATION QUERIES")}')
        self.stdout.write('=' * 50)
        
        # Count questions per category
        self.stdout.write('\na) Count questions per category:')
        categories_with_count = Category.objects.annotate(
            question_count=Count('questionextended')
        ).order_by('-question_count')
        for category in categories_with_count:
            self.stdout.write(f'{category.name}: {category.question_count} questions')
        
        # Count questions per author
        self.stdout.write('\nb) Count questions per author:')
        authors_with_count = Author.objects.annotate(
            question_count=Count('questionextended')
        ).order_by('-question_count')
        for author in authors_with_count:
            self.stdout.write(f'{author.name}: {author.question_count} questions')
        
        # Average votes per question
        self.stdout.write('\nc) Average votes per question:')
        questions_with_avg_votes = Question.objects.annotate(
            avg_votes=Avg('choice__votes')
        ).order_by('-avg_votes')
        for question in questions_with_avg_votes:
            avg_votes = question.avg_votes or 0
            self.stdout.write(f'"{question.question_text}": {avg_votes:.1f} average votes')

        # 5. FILTERING WITH RELATIONSHIPS
        self.stdout.write(f'\n\n{self.style.WARNING("5. FILTERING WITH RELATIONSHIPS")}')
        self.stdout.write('=' * 50)
        
        # Questions in Technology category
        self.stdout.write('\na) Questions in Technology category:')
        tech_questions = Question.objects.filter(
            extended__category__name='Technology'
        )
        for question in tech_questions:
            self.stdout.write(f'- {question.question_text}')
        
        # Questions by specific author
        self.stdout.write('\nb) Questions by Alice Johnson:')
        alice_questions = Question.objects.filter(
            extended__author__name='Alice Johnson'
        )
        for question in alice_questions:
            self.stdout.write(f'- {question.question_text}')
        
        # Questions with specific tags
        self.stdout.write('\nc) Questions with Python tag:')
        python_questions = Question.objects.filter(
            extended__tags__name='Python'
        )
        for question in python_questions:
            self.stdout.write(f'- {question.question_text}')
        
        # Easy difficulty questions
        self.stdout.write('\nd) Easy difficulty questions:')
        easy_questions = Question.objects.filter(
            extended__difficulty_level='easy'
        )
        for question in easy_questions:
            self.stdout.write(f'- {question.question_text}')
        
        # Featured questions with high view count
        self.stdout.write('\ne) Featured questions with view count > 500:')
        popular_featured = Question.objects.filter(
            extended__is_featured=True,
            extended__view_count__gt=500
        )
        for question in popular_featured:
            view_count = question.extended.view_count
            self.stdout.write(f'- {question.question_text} ({view_count} views)')

        # 6. COMPLEX FILTERING WITH Q OBJECTS
        self.stdout.write(f'\n\n{self.style.WARNING("6. COMPLEX FILTERING WITH Q OBJECTS")}')
        self.stdout.write('=' * 50)
        
        # Questions that are either easy OR in Technology category
        self.stdout.write('\na) Questions that are easy OR in Technology category:')
        easy_or_tech = Question.objects.filter(
            Q(extended__difficulty_level='easy') | Q(extended__category__name='Technology')
        ).distinct()
        for question in easy_or_tech:
            difficulty = question.extended.difficulty_level
            category = question.extended.category.name if question.extended.category else "No category"
            self.stdout.write(f'- {question.question_text} ({difficulty}, {category})')
        
        # Questions that are NOT easy AND have high view count
        self.stdout.write('\nb) Questions that are NOT easy AND have view count > 300:')
        hard_popular = Question.objects.filter(
            ~Q(extended__difficulty_level='easy') & Q(extended__view_count__gt=300)
        )
        for question in hard_popular:
            difficulty = question.extended.difficulty_level
            view_count = question.extended.view_count
            self.stdout.write(f'- {question.question_text} ({difficulty}, {view_count} views)')

        self.stdout.write(f'\n{self.style.SUCCESS("=== QUERY DEMO COMPLETED ===")}')
