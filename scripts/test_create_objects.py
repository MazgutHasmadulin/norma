"""
Script to create sample objects and exercise key web views via Django test client.
Run with: python manage.py shell -c "exec(open('scripts/test_create_objects.py').read())"
"""

from django.contrib.auth import get_user_model
from django.test import Client
from norma.models import Project, Folder, TestCase

User = get_user_model()
user, created = User.objects.get_or_create(username='testuser')
if created:
    user.set_password('password')
    user.save()

# Remove any existing test project
Project.objects.filter(name='Test Project').delete()

project = Project.objects.create(name='Test Project', description='Auto created project', author=user)
print('Project created', project.pk)

root = Folder.objects.create(name='RootFolder', project=project, author=user)
child = Folder.objects.create(name='ChildFolder', project=project, parent_folder=root, author=user)
grandchild = Folder.objects.create(name='GrandChild', project=project, parent_folder=child, author=user)
print('Folders:', root.pk, child.pk, grandchild.pk)

tc = TestCase.objects.create(title='TC Auto', description='Auto test case', expected_result='ok', steps=[{"action": "Auto step", "expected_result": "OK"}], author=user, project=project, folder=grandchild)
print('TestCase', tc.pk, 'full path:', tc.get_full_path())

c = Client()
c.force_login(user)

r = c.get('/projects/', HTTP_HOST='127.0.0.1')
print('/projects/ status', r.status_code)

r2 = c.get(f'/projects/{project.pk}/', HTTP_HOST='127.0.0.1')
print(f'/projects/{project.pk}/ status', r2.status_code)

r3 = c.get(f'/projects/{project.pk}/folders/{child.pk}/', HTTP_HOST='127.0.0.1')
print(f'/projects/{project.pk}/folders/{child.pk}/ status', r3.status_code)

r4 = c.get(f'/projects/{project.pk}/folders/{grandchild.pk}/', HTTP_HOST='127.0.0.1')
print(f'/projects/{project.pk}/folders/{grandchild.pk}/ status', r4.status_code)

print('Project detail contains project name?', (str(project.name) in r2.content.decode('utf-8')))
print('Folder detail contains folder name?', (str(child.name) in r3.content.decode('utf-8')))

print('All done')
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
from django.contrib.auth import get_user_model
from norma.models import Project, Folder, TestCase
User = get_user_model()

print('Django OK, user model:', User)

# Create or get user
user, created = User.objects.get_or_create(username='testuser')
if created:
    user.set_password('testpass')
    user.save()
    print('Created user testuser')
else:
    print('User testuser exists')

# Create project
proj, created = Project.objects.get_or_create(name='Test Project', defaults={'description':'Auto-created project', 'author': user})
if created:
    print('Created project id=', proj.pk)
else:
    print('Project exists id=', proj.pk)

# Create root folder
root_folder, created = Folder.objects.get_or_create(name='Root Folder', project=proj, parent_folder=None, defaults={'author': user})
print('Root folder id=', root_folder.pk)

# Create nested folder
nested, created = Folder.objects.get_or_create(name='Nested Folder', project=proj, parent_folder=root_folder, defaults={'author': user})
print('Nested folder id=', nested.pk, 'level=', nested.level)

# Create testcase in nested
tc1, created = TestCase.objects.get_or_create(title='Nested Case 1', project=proj, folder=nested, defaults={'description':'desc','steps':[], 'expected_result':'ok','author':user})
print('TestCase nested id=', tc1.pk)

# Create testcase in root
tc2, created = TestCase.objects.get_or_create(title='Root Case 1', project=proj, folder=None, defaults={'description':'desc','steps':[], 'expected_result':'ok','author':user})
print('TestCase root id=', tc2.pk)

print('All done')
