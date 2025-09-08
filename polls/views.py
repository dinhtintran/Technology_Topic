from django.db.models import F, Count, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator

from .models import Choice, Question, Category, Tag, Author, QuestionExtended


# Function-based views
def index(request):
    """Display list of latest questions"""
    latest_question_list = Question.objects.order_by("-pub_date")[:5]
    
    # Get statistics for display
    total_questions = Question.objects.count()
    total_categories = Category.objects.count()
    total_authors = Author.objects.count()
    
    context = {
        "latest_question_list": latest_question_list,
        "total_questions": total_questions,
        "total_categories": total_categories,
        "total_authors": total_authors,
    }
    return render(request, "polls/index.html", context)


def detail(request, question_id):
    """Display question detail and voting form"""
    question = get_object_or_404(Question, pk=question_id)
    
    # Get extended information if available
    try:
        extended = question.extended
        context = {
            "question": question,
            "extended": extended,
            "category": extended.category,
            "author": extended.author,
            "tags": extended.tags.all(),
            "difficulty": extended.get_difficulty_level_display(),
        }
    except QuestionExtended.DoesNotExist:
        context = {
            "question": question,
            "extended": None,
        }
    
    return render(request, "polls/detail.html", context)


def results(request, question_id):
    """Display voting results for a question"""
    question = get_object_or_404(Question, pk=question_id)
    
    # Calculate total votes
    total_votes = sum(choice.votes for choice in question.choice_set.all())
    
    # Get choices with percentage
    choices_with_percentage = []
    for choice in question.choice_set.all():
        percentage = (choice.votes / total_votes * 100) if total_votes > 0 else 0
        choices_with_percentage.append({
            'choice': choice,
            'percentage': round(percentage, 1)
        })
    
    context = {
        "question": question,
        "choices_with_percentage": choices_with_percentage,
        "total_votes": total_votes,
    }
    return render(request, "polls/results.html", context)


def vote(request, question_id):
    """Handle voting submission"""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        
        # Update view count if extended info exists
        try:
            question.extended.view_count = F("view_count") + 1
            question.extended.save()
        except QuestionExtended.DoesNotExist:
            pass
        
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def category_list(request):
    """Display list of all categories with question count"""
    categories = Category.objects.annotate(
        question_count=Count('questionextended')
    ).order_by('-question_count')
    
    context = {
        "categories": categories,
        "title": "Categories"
    }
    return render(request, "polls/category_list.html", context)


def category_detail(request, category_id):
    """Display questions in a specific category"""
    category = get_object_or_404(Category, pk=category_id)
    questions = Question.objects.filter(
        extended__category=category
    ).select_related('extended__author').prefetch_related('extended__tags')
    
    # Pagination
    paginator = Paginator(questions, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "category": category,
        "questions": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "polls/category_detail.html", context)


def author_list(request):
    """Display list of all authors with question count"""
    authors = Author.objects.annotate(
        question_count=Count('questionextended')
    ).order_by('-question_count')
    
    context = {
        "authors": authors,
        "title": "Authors"
    }
    return render(request, "polls/author_list.html", context)


def author_detail(request, author_id):
    """Display questions by a specific author"""
    author = get_object_or_404(Author, pk=author_id)
    questions = Question.objects.filter(
        extended__author=author
    ).select_related('extended__category').prefetch_related('extended__tags')
    
    context = {
        "author": author,
        "questions": questions,
    }
    return render(request, "polls/author_detail.html", context)


def tag_list(request):
    """Display list of all tags with question count"""
    tags = Tag.objects.annotate(
        question_count=Count('questionextended')
    ).order_by('-question_count')
    
    context = {
        "tags": tags,
        "title": "Tags"
    }
    return render(request, "polls/tag_list.html", context)


def search(request):
    """Search questions by text, category, author, or tags"""
    query = request.GET.get('q', '')
    questions = Question.objects.none()
    
    if query:
        questions = Question.objects.filter(
            Q(question_text__icontains=query) |
            Q(extended__category__name__icontains=query) |
            Q(extended__author__name__icontains=query) |
            Q(extended__tags__name__icontains=query)
        ).distinct().select_related(
            'extended__category', 'extended__author'
        ).prefetch_related('extended__tags')
    
    # Pagination
    paginator = Paginator(questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "query": query,
        "questions": page_obj,
        "page_obj": page_obj,
        "total_results": questions.count() if query else 0,
    }
    return render(request, "polls/search.html", context)