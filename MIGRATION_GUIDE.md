# Django Migration Guide

## Tổng quan về Django Migrations

Django migrations là cách Django theo dõi và áp dụng các thay đổi vào database schema.

## Các lệnh Migration cơ bản

### 1. Tạo Migration
```bash
# Tạo migration cho tất cả apps
python manage.py makemigrations

# Tạo migration cho app cụ thể
python manage.py makemigrations polls

# Tạo migration với tên cụ thể
python manage.py makemigrations polls --name add_question_fields

# Tạo empty migration
python manage.py makemigrations polls --empty --name custom_migration
```

### 2. Áp dụng Migration
```bash
# Áp dụng tất cả migrations chưa được áp dụng
python manage.py migrate

# Áp dụng migration cho app cụ thể
python manage.py migrate polls

# Áp dụng đến migration cụ thể
python manage.py migrate polls 0003

# Rollback về migration trước đó
python manage.py migrate polls 0002

# Rollback tất cả migrations của app
python manage.py migrate polls zero
```

### 3. Xem trạng thái Migration
```bash
# Xem trạng thái tất cả migrations
python manage.py showmigrations

# Xem trạng thái migration của app cụ thể
python manage.py showmigrations polls

# Xem SQL sẽ được thực thi
python manage.py sqlmigrate polls 0003
```

### 4. Fake Migration
```bash
# Fake apply migration (mark as applied without running)
python manage.py migrate polls 0003 --fake

# Fake unapply migration (mark as not applied without running)
python manage.py migrate polls 0002 --fake
```

## Các loại Migration Operations

### 1. Field Operations
```python
# Thêm field
migrations.AddField(
    model_name='question',
    name='is_active',
    field=models.BooleanField(default=True),
)

# Xóa field
migrations.RemoveField(
    model_name='question',
    name='old_field',
)

# Thay đổi field
migrations.AlterField(
    model_name='question',
    name='question_text',
    field=models.CharField(max_length=300),
)

# Đổi tên field
migrations.RenameField(
    model_name='question',
    old_name='old_name',
    new_name='new_name',
)
```

### 2. Model Operations
```python
# Tạo model
migrations.CreateModel(
    name='NewModel',
    fields=[
        ('id', models.AutoField(primary_key=True)),
        ('name', models.CharField(max_length=100)),
    ],
)

# Xóa model
migrations.DeleteModel(name='OldModel')

# Đổi tên model
migrations.RenameModel(
    old_name='OldModel',
    new_name='NewModel',
)

# Thay đổi Meta options
migrations.AlterModelOptions(
    name='question',
    options={'ordering': ['-pub_date']},
)
```

### 3. Data Migrations
```python
def populate_data(apps, schema_editor):
    Question = apps.get_model('polls', 'Question')
    for question in Question.objects.all():
        # Logic to populate data
        pass

def reverse_populate_data(apps, schema_editor):
    # Reverse logic
    pass

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(
            populate_data,
            reverse_populate_data,
            atomic=True,
        ),
    ]
```

### 4. Raw SQL Migration
```python
migrations.RunSQL(
    "UPDATE polls_question SET is_active = 1;",
    reverse_sql="UPDATE polls_question SET is_active = 0;",
)
```

## Best Practices

### 1. Migration Naming
- Sử dụng tên mô tả: `--name add_user_profile`
- Tránh tên generic: `--name auto_migration`

### 2. Data Migration Safety
- Luôn cung cấp reverse function
- Sử dụng `atomic=True` cho data migrations
- Test trên dữ liệu thực trước khi deploy

### 3. Rollback Strategy
- Luôn backup database trước khi migrate
- Test rollback trên staging environment
- Kiểm tra dependencies giữa các migrations

### 4. Performance Considerations
- Thêm index cho large tables:
```python
migrations.RunSQL(
    "CREATE INDEX idx_question_pub_date ON polls_question(pub_date);",
    reverse_sql="DROP INDEX idx_question_pub_date;",
)
```

- Sử dụng `db_index=True` cho fields thường xuyên query

## Migration Workflow trong Team

### 1. Development
```bash
# Developer A tạo migration
git checkout -b feature/add-user-profile
python manage.py makemigrations
git add polls/migrations/0005_add_user_profile.py
git commit -m "Add user profile migration"
```

### 2. Merge Conflicts
Nếu có conflict migration numbers:
```bash
# Merge latest main
git checkout main
git pull origin main
git checkout feature/add-user-profile
git merge main

# Nếu có conflict migration numbers, rename migration
python manage.py makemigrations --merge
```

### 3. Production Deployment
```bash
# Backup database
pg_dump mydb > backup.sql

# Apply migrations
python manage.py migrate

# Verify
python manage.py showmigrations
```

## Troubleshooting

### 1. Migration Conflicts
```bash
# Tạo merge migration
python manage.py makemigrations --merge

# Hoặc reset migrations (cẩn thận!)
python manage.py migrate polls zero
rm polls/migrations/0003_*.py
python manage.py makemigrations polls
python manage.py migrate polls
```

### 2. Fake Migration Fixes
```bash
# Nếu migration đã được áp dụng manually
python manage.py migrate polls 0003 --fake

# Nếu cần reset migration state
python manage.py migrate polls 0002 --fake
python manage.py migrate polls 0003
```

### 3. Data Loss Prevention
- Luôn tạo migration để thêm field trước khi xóa field cũ
- Sử dụng 3-step migration cho thay đổi lớn:
  1. Thêm field mới
  2. Migrate dữ liệu từ field cũ sang field mới  
  3. Xóa field cũ

## Migration Files trong Project này

### 0001_initial.py
- Tạo models Question và Choice ban đầu

### 0002_author_category_tag_questionextended.py  
- Thêm models Author, Category, Tag, QuestionExtended
- Tạo relationships giữa các models

### 0003_add_question_fields.py
- Thêm fields: updated_at, is_active, slug vào Question

### 0004_populate_question_slugs.py
- Data migration để populate slug cho các Question hiện có
- Có reverse function để clear slugs
