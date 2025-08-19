from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import os


class Command(BaseCommand):
    help = 'Demonstrate Django migration operations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo',
            choices=['show', 'rollback', 'forward', 'fake', 'sql'],
            help='Type of migration demo to run',
        )

    def handle(self, *args, **options):
        demo_type = options.get('demo')
        
        if demo_type == 'show':
            self.show_migrations()
        elif demo_type == 'rollback':
            self.demo_rollback()
        elif demo_type == 'forward':
            self.demo_forward()
        elif demo_type == 'fake':
            self.demo_fake()
        elif demo_type == 'sql':
            self.show_sql()
        else:
            self.show_all_demos()

    def show_migrations(self):
        """Show current migration status"""
        self.stdout.write(self.style.SUCCESS('=== CURRENT MIGRATION STATUS ==='))
        call_command('showmigrations', 'polls')

    def demo_rollback(self):
        """Demo migration rollback"""
        self.stdout.write(self.style.WARNING('=== MIGRATION ROLLBACK DEMO ==='))
        
        self.stdout.write('Current migration status:')
        call_command('showmigrations', 'polls')
        
        self.stdout.write('\nRolling back to migration 0002...')
        call_command('migrate', 'polls', '0002')
        
        self.stdout.write('Migration status after rollback:')
        call_command('showmigrations', 'polls')
        
        self.stdout.write('\nMigrating forward again...')
        call_command('migrate', 'polls')
        
        self.stdout.write('Final migration status:')
        call_command('showmigrations', 'polls')

    def demo_forward(self):
        """Demo forward migration"""
        self.stdout.write(self.style.WARNING('=== FORWARD MIGRATION DEMO ==='))
        
        self.stdout.write('Applying specific migration:')
        call_command('migrate', 'polls', '0003')
        call_command('showmigrations', 'polls')
        
        self.stdout.write('\nApplying all migrations:')
        call_command('migrate', 'polls')
        call_command('showmigrations', 'polls')

    def demo_fake(self):
        """Demo fake migration"""
        self.stdout.write(self.style.WARNING('=== FAKE MIGRATION DEMO ==='))
        self.stdout.write('WARNING: This is for demonstration only!')
        
        # Fake unapply
        self.stdout.write('\nFake unapplying last migration:')
        call_command('migrate', 'polls', '0003', fake=True)
        call_command('showmigrations', 'polls')
        
        # Fake apply
        self.stdout.write('\nFake applying migration back:')
        call_command('migrate', 'polls', '0004', fake=True)
        call_command('showmigrations', 'polls')

    def show_sql(self):
        """Show SQL for migrations"""
        self.stdout.write(self.style.WARNING('=== MIGRATION SQL DEMO ==='))
        
        self.stdout.write('SQL for migration 0003:')
        try:
            call_command('sqlmigrate', 'polls', '0003')
        except Exception as e:
            self.stdout.write(f'Error: {e}')
        
        self.stdout.write('\nSQL for migration 0004:')
        try:
            call_command('sqlmigrate', 'polls', '0004')
        except Exception as e:
            self.stdout.write(f'Error: {e}')

    def show_all_demos(self):
        """Show all available demos"""
        self.stdout.write(self.style.SUCCESS('=== MIGRATION DEMO COMMANDS ==='))
        self.stdout.write('Available demo options:')
        self.stdout.write('  --demo show     : Show current migration status')
        self.stdout.write('  --demo rollback : Demo rollback and forward migration')
        self.stdout.write('  --demo forward  : Demo forward migration')
        self.stdout.write('  --demo fake     : Demo fake migration operations')
        self.stdout.write('  --demo sql      : Show SQL for migrations')
        
        self.stdout.write('\nUseful migration commands:')
        self.stdout.write('  python manage.py makemigrations [app_name]')
        self.stdout.write('  python manage.py migrate [app_name] [migration_name]')
        self.stdout.write('  python manage.py showmigrations [app_name]')
        self.stdout.write('  python manage.py sqlmigrate app_name migration_name')
        self.stdout.write('  python manage.py migrate app_name migration_name --fake')
        self.stdout.write('  python manage.py migrate app_name zero  # Rollback all')
        
        self.stdout.write('\nMigration file locations:')
        migrations_dir = os.path.join('polls', 'migrations')
        self.stdout.write(f'  {migrations_dir}/')
        
        if os.path.exists(migrations_dir):
            for file in os.listdir(migrations_dir):
                if file.endswith('.py') and not file.startswith('__'):
                    self.stdout.write(f'    {file}')
        
        self.stdout.write('\nCurrent database tables:')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE 'polls_%'
                ORDER BY name;
            """)
            tables = cursor.fetchall()
            for table in tables:
                self.stdout.write(f'  {table[0]}')

        # Show current migration status
        self.stdout.write('\nCurrent migration status:')
        call_command('showmigrations', 'polls')
