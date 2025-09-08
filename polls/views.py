from django.db.models import F, Count, Q
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from django.views import View

from .models import Choice, Question, Category, Tag, Author, QuestionExtended


# Class-based views
class IndexView(ListView):
    """Display list of latest questions"""
    model = Question
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"
    paginate_by = 5
    
    def get_queryset(self):
        return Question.objects.select_related('extended__category', 'extended__author').order_by("-pub_date")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "total_questions": Question.objects.count(),
            "total_categories": Category.objects.count(),
            "total_authors": Author.objects.count(),
        })
        return context


class QuestionDetailView(DetailView):
    """Display question detail and voting form"""
    model = Question
    template_name = "polls/detail.html"
    context_object_name = "question"
    pk_url_kwarg = "question_id"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.object
        
        try:
            extended = question.extended
            context.update({
                "extended": extended,
                "category": extended.category,
                "author": extended.author,
                "tags": extended.tags.all(),
                "difficulty": extended.get_difficulty_level_display(),
            })
        except QuestionExtended.DoesNotExist:
            context["extended"] = None
            
        return context


class QuestionResultsView(DetailView):
    """Display voting results for a question"""
    model = Question
    template_name = "polls/results.html"
    context_object_name = "question"
    pk_url_kwarg = "question_id"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.object
        
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
        
        context.update({
            "choices_with_percentage": choices_with_percentage,
            "total_votes": total_votes,
        })
        return context


class CategoryListView(ListView):
    """Display list of all categories with question count"""
    model = Category
    template_name = "polls/category_list.html"
    context_object_name = "categories"
    
    def get_queryset(self):
        return Category.objects.annotate(
            question_count=Count('questionextended')
        ).order_by('-question_count')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Categories"
        return context


class CategoryDetailView(DetailView):
    """Display questions in a specific category"""
    model = Category
    template_name = "polls/category_detail.html"
    context_object_name = "category"
    pk_url_kwarg = "category_id"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        
        questions = Question.objects.filter(
            extended__category=category
        ).select_related('extended__author').prefetch_related('extended__tags')
        
        # Pagination
        paginator = Paginator(questions, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context.update({
            "questions": page_obj,
            "page_obj": page_obj,
        })
        return context


class AuthorListView(ListView):
    """Display list of all authors with question count"""
    model = Author
    template_name = "polls/author_list.html"
    context_object_name = "authors"
    
    def get_queryset(self):
        return Author.objects.annotate(
            question_count=Count('questionextended')
        ).order_by('-question_count')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Authors"
        return context


class TagListView(ListView):
    """Display list of all tags with question count"""
    model = Tag
    template_name = "polls/tag_list.html"
    context_object_name = "tags"
    
    def get_queryset(self):
        return Tag.objects.annotate(
            question_count=Count('questionextended')
        ).order_by('-question_count')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Tags"
        return context


class SearchView(ListView):
    """Search questions by text, category, author, or tags"""
    model = Question
    template_name = "polls/search.html"
    context_object_name = "questions"
    paginate_by = 10
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Question.objects.filter(
                Q(question_text__icontains=query) |
                Q(extended__category__name__icontains=query) |
                Q(extended__author__name__icontains=query) |
                Q(extended__tags__name__icontains=query)
            ).distinct().select_related(
                'extended__category', 'extended__author'
            ).prefetch_related('extended__tags')
        return Question.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context.update({
            "query": query,
            "total_results": self.get_queryset().count() if query else 0,
        })
        return context


# Function-based view for voting (remains as function due to form processing)
def vote(request, question_id):
    """Handle voting submission"""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
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