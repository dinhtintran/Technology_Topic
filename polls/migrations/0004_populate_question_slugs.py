from django.db import migrations
from django.utils.text import slugify


def populate_question_slugs(apps, schema_editor):
    """
    Populate slug field for existing questions
    """
    Question = apps.get_model('polls', 'Question')
    for question in Question.objects.all():
        if not question.slug:
            base_slug = slugify(question.question_text)
            slug = base_slug
            counter = 1
            
            # Ensure unique slug
            while Question.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            question.slug = slug
            question.save()


def reverse_populate_question_slugs(apps, schema_editor):
    """
    Reverse function - clear all slugs
    """
    Question = apps.get_model('polls', 'Question')
    Question.objects.update(slug=None)


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_add_question_fields'),
    ]

    operations = [
        migrations.RunPython(
            populate_question_slugs,
            reverse_populate_question_slugs,
            atomic=True,
        ),
    ]
