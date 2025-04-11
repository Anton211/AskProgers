from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Case, When, IntegerField, F, Sum, Avg, Value
from django.utils import timezone
from django.db import transaction

from app.models import Tag, Profile, Answer, Question, QuestionLike, AnswerLike
from faker import Faker
from tqdm import tqdm
import random
from itertools import product
import os


class Command(BaseCommand):
    help = 'Fills the database with data'

    def add_arguments(self, parser):
        parser.add_argument('rate', type=float)

    def handle(self, *args, **options):
        rate = options['rate']
        if 0 < rate <= 1:
            folder_path = 'uploads'
            keep_files = ['man.png', 'woman.png']

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path) and filename not in keep_files:
                    os.remove(file_path)

            with connection.cursor() as cursor:
                cursor.execute(f"TRUNCATE TABLE app_tag RESTART IDENTITY CASCADE")
                cursor.execute(f"TRUNCATE TABLE auth_user RESTART IDENTITY CASCADE")
                cursor.execute(f"TRUNCATE TABLE app_profile RESTART IDENTITY CASCADE")
                cursor.execute(f"TRUNCATE TABLE app_question RESTART IDENTITY CASCADE")
                cursor.execute(f"TRUNCATE TABLE app_answer RESTART IDENTITY CASCADE")
                cursor.execute(f"TRUNCATE TABLE app_questionlike RESTART IDENTITY CASCADE")
                cursor.execute(f"TRUNCATE TABLE app_answerlike RESTART IDENTITY CASCADE")

            faker = Faker(['it_IT', 'en_US', 'ru_RU'])

            num_users = int(rate * 10000)
            num_questions = num_users * 10
            num_ans = num_users * 100
            num_tags = num_users
            num_likes = num_users * 200

            Tag.objects.bulk_create([
                Tag(name=faker.word()+str(i)) for i in range(num_tags)
            ])
            self.stdout.write(self.style.SUCCESS('Filling Tags is done'))

            User.objects.bulk_create([
                User(username=faker.word()+str(i),
                     email=faker.unique.email(),
                     password=faker.password(), first_name=faker.first_name(),
                     date_joined=timezone.make_aware(faker.date_time_this_century()))
                for i in range(num_users)
            ])
            self.stdout.write(self.style.SUCCESS('Filling Users is done'))

            Profile.objects.bulk_create([
                Profile(user_id=i+1,
                        avatar=File(open(f"uploads/{['man', 'woman'][random.randint(0, 1)]}.png", 'rb'), name=f'ava_{i}.png'))
                for i in range(num_users)
            ])
            self.stdout.write(self.style.SUCCESS('Filling Profiles is done'))

            for j in tqdm(range(5)):
                batch = num_questions // 5
                questions = [
                    Question(title=faker.sentence(nb_words=10), content=faker.text(max_nb_chars=300),
                             profile_id=random.randint(1, num_users),
                             create_dt=timezone.make_aware(faker.date_time_this_century()))
                    for _ in range(batch)
                ]

                Question.objects.bulk_create(questions)

                qtags = set([])
                i = j * batch + 1
                while len(qtags) < batch:
                    tids = random.sample(range(1, num_tags), 3)
                    for t in tids:
                        qtags.add((i, t))
                    i += 1

                Question.tags.through.objects.bulk_create([
                    Question.tags.through(question_id=qid, tag_id=tid)
                    for qid, tid in qtags
                ])

            tags_count = Question.tags.through.objects.values('tag_id').annotate(count=Count('id'))
            cases = []
            for item in tags_count:
                cases.append(When(id=item['tag_id'], then=item['count']))

            Tag.objects.update(
                count=Case(
                    *cases,
                    default=0,
                    output_field=IntegerField()
                )
            )

            self.stdout.write(self.style.SUCCESS('Filling Questions is done'))
            del questions

            for _ in tqdm(range(50)):
                batch = num_ans // 50
                answers = [
                    Answer(content=faker.text(max_nb_chars=300), is_true=faker.boolean(10),
                           profile_id=random.randint(1, num_users),
                           question_id = random.randint(1, num_questions),
                           create_dt=timezone.make_aware(faker.date_time_this_century()))
                    for _ in range(batch)
                ]
                Answer.objects.bulk_create(answers)

            qa_count = Answer.objects.values('question_id').annotate(count=Count('id'))
            with transaction.atomic():
                for item in qa_count:
                    Question.objects.filter(id=item['question_id']).update(num_answers=item['count'])

            self.stdout.write(self.style.SUCCESS('Filling Answers is done'))
            del qa_count

            from itertools import product

            user_size = num_users // 100
            question_size = num_questions // 100
            ans_size = num_ans // 100
            for i in tqdm(range(100)):
                used_qpairs = random.sample(list(product(range(i*user_size+1, (i+1)*user_size),
                                                         range(i*question_size+1, (i+1)*question_size))),
                                            num_likes // 200)

                used_apairs = random.sample(list(product(range(i * user_size + 1, (i + 1) * user_size),
                                                         range(i * ans_size + 1, (i + 1) * ans_size))),
                                            num_likes // 200)

                QuestionLike.objects.bulk_create([
                    QuestionLike(question_id=qid, profile_id=uid,
                                     is_like=faker.boolean(60))
                    for uid, qid in used_qpairs
                    ])

                AnswerLike.objects.bulk_create([
                    AnswerLike(answer_id=aid, profile_id=uid,
                               is_like=faker.boolean(60))
                    for uid, aid in used_apairs
                ])

                del used_apairs, used_qpairs

            alikes_rate = AnswerLike.objects.values('answer_id') \
                .annotate(rating=Sum(Case(When(is_like=True, then=1),
                                                 When(is_like=False, then=-1)))) \
                .values('answer_id', 'rating')
            with transaction.atomic():
                for item in alikes_rate:
                    Answer.objects.filter(id=item['answer_id']).update(rating=item['rating'])

            qlikes_rate = QuestionLike.objects.values('question_id') \
                .annotate(rating=Sum(Case(When(is_like=True, then=1),
                                                 When(is_like=False, then=-1)))) \
                .values('question_id', 'rating')
            with transaction.atomic():
                for item in qlikes_rate:
                    Question.objects.filter(id=item['question_id']).update(rating=item['rating'])

            qrates = Question.objects.values('profile_id').annotate(rating=Sum('rating'))
            arates = Answer.objects.values('profile_id').annotate(rating=Sum('rating'))
            from collections import defaultdict

            rating_dict = defaultdict(int)

            for item in qrates:
                rating_dict[item['profile_id']] += item['rating']

            for item in arates:
                rating_dict[item['profile_id']] += item['rating']

            with transaction.atomic():
                for profile_id, rating in rating_dict.items():
                    Profile.objects.filter(id=profile_id).update(rating=rating)

            self.stdout.write(self.style.SUCCESS('Filling Likes is done'))

            self.stdout.write(self.style.SUCCESS('Filling database is done'))

        else:
            raise ValueError('Rate must be between 0 and 1')
