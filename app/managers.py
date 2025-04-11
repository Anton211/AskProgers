from django.db import models
from django.http import Http404
from django.shortcuts import get_object_or_404


class QuestionManager(models.Manager):
    def get_popular(self):
        return self.order_by('-rating')

    def get_by_tag(self, tag):
        questions = self.filter(tags__name=tag)
        if questions:
            return questions.order_by('-rating')
        else:
            raise Http404('Указанного тэга не существует')

    def get_question(self, question_id):
        return get_object_or_404(self, id=question_id)

class AnswerManager(models.Manager):
    def get_by_question(self, question):
        return self.filter(question__id=question.id).order_by('-rating', '-create_dt')

class TagManager(models.Manager):
    def get_top(self):
        return self.order_by('-count')[:20]

class ProfileManager(models.Manager):
    def get_top(self):
        return self.order_by('-rating')[:5]