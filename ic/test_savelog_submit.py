import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','moduloparsons.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth import get_user_model
from parsons.models import Problem, UserLog, Language
User = get_user_model()
user, created = User.objects.get_or_create(username='testuser')
user.set_password('pass')
user.save()
client = Client()
print('login', client.login(username='testuser', password='pass'))
prob = Problem.objects.filter(question_type='P').first()
print('problem', prob)
if prob is None:
    print('no Parsons problem found')
else:
    data = {
        'problem': prob.id,
        'solution': '',
        'solution_lines': 0,
        'console': '',
        'outcome': 'P',
        'seconds_in_code': 0,
        'seconds_to_begin': 0,
        'seconds_in_page': 0,
        'csrfmiddlewaretoken': 'dummy'
    }
    resp = client.post('/parsons/savelog/', data)
    print('status', resp.status_code)
    print('content', resp.content.decode('utf-8'))
    print('Language count', Language.objects.count())
    print('UserLog count', UserLog.objects.count())
    if UserLog.objects.exists():
        print('first log', UserLog.objects.first())
