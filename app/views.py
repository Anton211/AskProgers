from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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
     'num_ans': i - 1
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

def popular_tags(request):
    return {'bar_tags': TAGS}

def paginate(objects_list, request, per_page):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(objects_list, per_page)
    try:
        page = paginator.page(page_num)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page

def index(request):
    questions_sort = sorted(QUESTIONS, key=lambda x: x['date'])
    page = paginate(questions_sort, request, 5)
    return render(request, 'index.html', context={'questions': page.object_list, 'page': page})

def popular(request):
    questions_sort = sorted(QUESTIONS, key=lambda x: (-x['rate'], x['date']))
    page = paginate(questions_sort, request, 5)
    return render(request, 'popular.html', context={'questions': page.object_list, 'page': page})

def question(request, question_id):
    answers_sort = sorted(ANSWERS[question_id - 1], key=lambda x: (-x['rate'], x['date']))
    page = paginate(answers_sort, request, 5)
    return render(request, 'question.html',
                context={'question': QUESTIONS[question_id - 1], 'answers': page.object_list, 'page': page})

def tag_questions(request, tag):
    if tag not in TAGS:
        return index(request)
    else:
        questions = [q for q in QUESTIONS if tag in q.get('tags', '')]
        questions_sort = sorted(questions, key=lambda x: (-x['rate'], x['date']))
        page = paginate(questions_sort, request, 5)
        return render(request, 'tag.html', context={'questions': page.object_list, 'tag': tag, 'page': page})

def create_question(request):
    return render(request, 'ask.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def settings(request):
    return render(request, 'settings.html')
