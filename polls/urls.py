from django.urls import path

from . import views

app_name = "polls"
urlpatterns = [
    # Function-based views
    path("", views.index, name="index"),
    path("<int:question_id>/", views.detail, name="detail"),
    path("<int:question_id>/results/", views.results, name="results"),
    path("<int:question_id>/vote/", views.vote, name="vote"),
    
    # Extended views for new features
    path("categories/", views.category_list, name="category_list"),
    path("category/<int:category_id>/", views.category_detail, name="category_detail"),
    path("authors/", views.author_list, name="author_list"),
    path("author/<int:author_id>/", views.author_detail, name="author_detail"),
    path("tags/", views.tag_list, name="tag_list"),
    path("search/", views.search, name="search"),
]