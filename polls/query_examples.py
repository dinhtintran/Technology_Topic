"""
Django ORM Query Examples
=========================

Để chạy các query này, mở Django shell:
python manage.py shell

Sau đó copy-paste các đoạn code dưới đây:
"""

# Import models
from polls.models import Question, Choice, Category, Tag, Author, QuestionExtended
from django.db.models import Count, Q, Avg, F
from django.utils import timezone

# =================
# 1. BASIC QUERIES
# =================

# Lấy tất cả questions
all_questions = Question.objects.all()
print(f"Total questions: {all_questions.count()}")

# Lấy question theo ID
question = Question.objects.get(id=1)
print(f"Question 1: {question.question_text}")

# Lấy hoặc tạo mới
category, created = Category.objects.get_or_create(
    name="New Category",
    defaults={'description': 'A new category'}
)
print(f"Category created: {created}")

# =================
# 2. FORWARD RELATIONSHIPS
# =================

# OneToOne forward: QuestionExtended -> Question
extended = QuestionExtended.objects.first()
question_text = extended.question.question_text
print(f"Extended question: {question_text}")

# ForeignKey forward: QuestionExtended -> Category
category_name = extended.category.name if extended.category else "No category"
print(f"Category: {category_name}")

# ManyToMany forward: QuestionExtended -> Tags
tags = extended.tags.all()
tag_names = [tag.name for tag in tags]
print(f"Tags: {tag_names}")

# =================
# 3. REVERSE RELATIONSHIPS
# =================

# OneToOne reverse: Question -> QuestionExtended
question = Question.objects.first()
try:
    extended_info = question.extended
    print(f"Extended info exists: {extended_info.difficulty_level}")
except QuestionExtended.DoesNotExist:
    print("No extended info")

# ForeignKey reverse: Question -> Choices
choices = question.choice_set.all()
print(f"Choices count: {choices.count()}")

# ForeignKey reverse: Category -> QuestionExtended
tech_category = Category.objects.get(name="Technology")
tech_questions = tech_category.questionextended_set.all()
print(f"Technology questions: {tech_questions.count()}")

# ManyToMany reverse: Tag -> QuestionExtended
python_tag = Tag.objects.get(name="Python")
python_questions = python_tag.questionextended_set.all()
print(f"Python tagged questions: {python_questions.count()}")

# =================
# 4. OPTIMIZATION QUERIES
# =================

# select_related() - cho ForeignKey và OneToOne
optimized_extended = QuestionExtended.objects.select_related(
    'question', 'category', 'author'
).all()

for ext in optimized_extended:
    # Không tạo thêm database queries
    print(f"{ext.question.question_text} by {ext.author.name}")

# prefetch_related() - cho ManyToMany và reverse ForeignKey
optimized_questions = Question.objects.prefetch_related(
    'choice_set', 'extended__tags'
).all()

for q in optimized_questions:
    # Không tạo thêm database queries
    choices_count = q.choice_set.count()
    try:
        tags_count = q.extended.tags.count()
        print(f"{q.question_text}: {choices_count} choices, {tags_count} tags")
    except QuestionExtended.DoesNotExist:
        print(f"{q.question_text}: {choices_count} choices, no extended info")

# =================
# 5. FILTERING
# =================

# Filter với relationships
tech_questions = Question.objects.filter(extended__category__name="Technology")
easy_questions = Question.objects.filter(extended__difficulty_level="easy")
alice_questions = Question.objects.filter(extended__author__name="Alice Johnson")
python_questions = Question.objects.filter(extended__tags__name="Python")

# Complex filtering với Q objects
easy_or_tech = Question.objects.filter(
    Q(extended__difficulty_level="easy") | Q(extended__category__name="Technology")
).distinct()

featured_and_popular = Question.objects.filter(
    Q(extended__is_featured=True) & Q(extended__view_count__gt=500)
)

# =================
# 6. AGGREGATION
# =================

# Count questions per category
categories_with_count = Category.objects.annotate(
    question_count=Count('questionextended')
).order_by('-question_count')

for cat in categories_with_count:
    print(f"{cat.name}: {cat.question_count} questions")

# Average votes per question
questions_with_avg = Question.objects.annotate(
    avg_votes=Avg('choice__votes'),
    total_votes=Count('choice__votes')
).order_by('-avg_votes')

for q in questions_with_avg:
    print(f"{q.question_text}: avg={q.avg_votes:.1f}, total={q.total_votes}")

# =================
# 7. UPDATE QUERIES
# =================

# Update single object
question = Question.objects.get(id=1)
question.question_text = "Updated question text"
question.save()

# Bulk update
Question.objects.filter(
    extended__difficulty_level="easy"
).update(pub_date=timezone.now())

# Update with F() expressions
Choice.objects.filter(question_id=1).update(votes=F('votes') + 1)

# =================
# 8. DELETE QUERIES
# =================

# Delete single object
# question = Question.objects.get(id=999)
# question.delete()

# Bulk delete
# Question.objects.filter(extended__view_count__lt=10).delete()

# =================
# 9. RAW SQL (nếu cần)
# =================

# Raw query
questions_raw = Question.objects.raw(
    "SELECT * FROM polls_question WHERE pub_date > %s",
    [timezone.now() - timezone.timedelta(days=30)]
)

# Extra conditions
questions_extra = Question.objects.extra(
    where=["pub_date > %s"],
    params=[timezone.now() - timezone.timedelta(days=30)]
)

# =================
# 10. USEFUL METHODS
# =================

# exists() - check if any records exist
has_questions = Question.objects.filter(extended__category__name="Technology").exists()

# first() and last()
first_question = Question.objects.first()
last_question = Question.objects.last()

# values() and values_list()
question_texts = Question.objects.values_list('question_text', flat=True)
question_data = Question.objects.values('id', 'question_text', 'pub_date')

# distinct()
unique_categories = QuestionExtended.objects.values_list(
    'category__name', flat=True
).distinct()

# order_by()
recent_questions = Question.objects.order_by('-pub_date')
popular_questions = Question.objects.annotate(
    total_votes=Count('choice__votes')
).order_by('-total_votes')

print("=== Query examples completed ===")
