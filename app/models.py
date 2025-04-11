from django.contrib.auth.models import User

from app.managers import *


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='uploads/')
    rating = models.IntegerField(default=0)

    objects = ProfileManager()


class Tag(models.Model):
    name = models.CharField(max_length=50)
    count = models.PositiveIntegerField(default=0)

    objects = TagManager()

    def update_count(self):
        self.count += 1
        self.save(update_fields=['count'])


class Question(models.Model):
    title = models.CharField(max_length=500)
    content = models.CharField(max_length=5000)
    tags = models.ManyToManyField(Tag)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    # create_dt = models.DateTimeField(auto_now_add=True)
    create_dt = models.DateTimeField(auto_now_add=False)
    rating = models.IntegerField(default=0)
    num_answers = models.PositiveIntegerField(default=0)

    objects = QuestionManager()

    def update_count(self):
        self.num_answers += 1
        self.save(update_fields=['num_answers'])

    class Meta:
        ordering = ('-create_dt',)


class Answer(models.Model):
    content = models.CharField(max_length=5000)
    is_true = models.BooleanField(default=False)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # create_dt = models.DateTimeField(auto_now_add=True)
    create_dt = models.DateTimeField(auto_now_add=False)
    rating = models.IntegerField(default=0)
    objects = AnswerManager()


class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    is_like = models.BooleanField()

    class Meta:
        unique_together = ["question", "profile"]

    def update_question_rating(self, question_id):
        question = Question.objects.get(id=question_id)
        profile = Profile.objects.get(id=question.profile.id)
        if self.is_like:
            question.rating += 1
            profile.rating += 1
        else:
            question.rating -= 1
            profile.rating -= 1
        question.save(update_fields=['rating'])
        profile.save(update_fields=['rating'])


class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    is_like = models.BooleanField()

    class Meta:
        unique_together = ["answer", "profile"]

    def update_answer_rating(self, answer_id):
        answer = Answer.objects.get(id=answer_id)
        profile = Profile.objects.get(id=answer.profile.id)
        if self.is_like:
            answer.rating += 1
            profile.rating += 1
        else:
            answer.rating -= 1
            profile.rating -= 1
        answer.save(update_fields=['rating'])
        profile.save(update_fields=['rating'])