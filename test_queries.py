#!/usr/bin/env python
import os
import sys
import django

# Thiết lập Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from polls.models import Question, Choice, Category, Tag, Author, QuestionExtended
from django.db.models import Count, Q, Avg

def test_relationships():
    print("=== TESTING DJANGO ORM RELATIONSHIPS ===\n")
    
    # 1. Forward relationships
    print("1. FORWARD RELATIONSHIPS:")
    ext = QuestionExtended.objects.first()
    print(f"   Question: {ext.question.question_text}")
    print(f"   Category: {ext.category.name if ext.category else 'None'}")
    print(f"   Author: {ext.author.name}")
    tags = [tag.name for tag in ext.tags.all()]
    print(f"   Tags: {tags}")
    
    # 2. Reverse relationships
    print("\n2. REVERSE RELATIONSHIPS:")
    question = Question.objects.first()
    print(f"   Question: {question.question_text}")
    choices = [choice.choice_text for choice in question.choice_set.all()]
    print(f"   Choices: {choices}")
    
    try:
        extended = question.extended
        print(f"   Extended: difficulty={extended.difficulty_level}, featured={extended.is_featured}")
    except QuestionExtended.DoesNotExist:
        print("   No extended info")
    
    # 3. Aggregation
    print("\n3. AGGREGATION QUERIES:")
    category_counts = Category.objects.annotate(
        question_count=Count('questionextended')
    ).values('name', 'question_count')
    
    for cat in category_counts:
        print(f"   {cat['name']}: {cat['question_count']} questions")
    
    # 4. Complex filtering
    print("\n4. COMPLEX FILTERING:")
    tech_questions = Question.objects.filter(
        extended__category__name="Technology"
    ).count()
    print(f"   Technology questions: {tech_questions}")
    
    easy_questions = Question.objects.filter(
        extended__difficulty_level="easy"
    ).count()
    print(f"   Easy questions: {easy_questions}")
    
    # 5. Optimization
    print("\n5. OPTIMIZATION WITH select_related:")
    optimized = QuestionExtended.objects.select_related(
        'question', 'category', 'author'
    ).first()
    print(f"   {optimized.question.question_text} by {optimized.author.name} in {optimized.category.name}")
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_relationships()
