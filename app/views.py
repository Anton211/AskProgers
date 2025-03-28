from django.shortcuts import render


TAGS = ['Python', 'Django', 'Flask', 'FastApi', 'C++']
PHOTOS = ['man', 'woman']
QUESTIONS = [
    {'id': i,
     'username': f'User{i}',
     'photo': f'/img/{PHOTOS[i % 2]}.png',
     'title': f'Question {i}',
     'content': f'Text of question {i}' * i,
     'date': '16 Мая 2025 16:45',
     'tags': [TAGS[i % len(TAGS)], TAGS[(i + 1) % len(TAGS)], TAGS[(i + 2) % len(TAGS)]],
     'rate': (-1) ** (i % 2) * i * 10,
     'num_ans': i
     } for i in range(1, 31)
]

ANSWERS = [
    [{'username': f'User{i}',
         'photo': f'/img/{PHOTOS[i % 2]}.png',
         'content': f'Text of answer {i}' * i,
         'true': True if i % 2 == 0 else False,
         'rate': (-1) ** (i % 2) * i * 10,
         'date': '16 Мая 2025 16:45'
         } for i in range(QUESTIONS[j]['num_ans'])
    ] for j in range(len(QUESTIONS))
]

def index(request):
    return render(request, 'index.html', context={'questions': QUESTIONS})

def popular(request):
    questions_sort = sorted(QUESTIONS, key=lambda x: -x['rate'])
    return render(request, 'popular.html', context={'questions': questions_sort})

def question(request, question_id):
    return render(request, 'question.html',
                context={'question': QUESTIONS[question_id - 1], 'answers': ANSWERS[question_id - 1]})