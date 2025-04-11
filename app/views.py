from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

from app.models import Question, Tag, Profile, Answer


def top_tags(request):
    return {'side_tags': Tag.objects.get_top()}

def top_users(request):
    return {'top_users': Profile.objects.get_top()}

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
    questions = Question.objects.all()
    page = paginate(questions, request, 20)
    return render(request, 'index.html',
                  context={'questions': page.object_list, 'page': page})

def popular(request):
    questions = Question.objects.get_popular()
    page = paginate(questions, request, 20)
    return render(request, 'popular.html',
                  context={'questions': page.object_list, 'page': page})

def question(request, question_id):
    question = Question.objects.get_question(question_id)
    answers = Answer.objects.get_by_question(question)
    page = paginate(answers, request, 30)
    return render(request, 'question.html',
                context={'question': question, 'answers': page.object_list, 'page': page})

def tag_questions(request, tag):
    questions = Question.objects.get_by_tag(tag)
    page = paginate(questions, request, 20)
    return render(request, 'tag.html',
                  context={'questions': page.object_list, 'tag': tag, 'page': page})

def create_question(request):
    return render(request, 'ask.html')

def login(request):
    return render(request, 'login.html')

def signup(request):
    return render(request, 'signup.html')

def settings(request):
    return render(request, 'settings.html')
