from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    # Class-based views
    path("", views.IndexView.as_view(), name="index"),
    path("<int:question_id>/", views.QuestionDetailView.as_view(), name="detail"),
    path("<int:question_id>/results/", views.QuestionResultsView.as_view(), name="results"),
    
    # Extended class-based views
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("category/<int:category_id>/", views.CategoryDetailView.as_view(), name="category_detail"),
    path("authors/", views.AuthorListView.as_view(), name="author_list"),
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    path("search/", views.SearchView.as_view(), name="search"),
    
    # Function-based view for form processing
    path("<int:question_id>/vote/", views.vote, name="vote"),
]