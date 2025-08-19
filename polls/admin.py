from django.contrib import admin

from .models import Choice, Question, Category, Tag, Author, QuestionExtended


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionExtendedInline(admin.StackedInline):
    model = QuestionExtended
    extra = 0


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Date information", {"fields": ["pub_date"], "classes": ["collapse"]}),
    ]
    inlines = [ChoiceInline, QuestionExtendedInline]
    list_display = ["question_text", "pub_date", "was_published_recently"]
    list_filter = ["pub_date"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']
    search_fields = ['name']


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email']


@admin.register(QuestionExtended)
class QuestionExtendedAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'author', 'difficulty_level', 'is_featured', 'view_count']
    list_filter = ['difficulty_level', 'is_featured', 'category', 'author']
    filter_horizontal = ['tags']


admin.site.register(Question, QuestionAdmin)