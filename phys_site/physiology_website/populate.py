from random import randint, choice, random
from datetime import datetime

from django_seed import Seed 
from django.contrib.auth.models import User

from users.models import *
from study.models import *
from tasks.models import *
from social_network.models import *


def random_string(length):
    res = ""
    for i in range(length):
        res += chr(65 + randint(0, 57))
    return res


seeder = Seed.seeder()


# Create 101000 users
# seeder.add_entity(User, 101000, {
#         'username': lambda x: 'User' + str(randint(1, 10000000000000)),
#         'email': lambda x: random_string(15) + '@gmail.com'
#   })

# # Create 10 countries
# seeder.add_entity(Country, 10)


# # Create 50 cities
# seeder.add_entity(City, 50)



# # Create 500 universities
# seeder.add_entity(University, 500)



# # Create 10000 groups
# seeder.add_entity(Group, 10000)



# # Create 5 domains
# seeder.add_entity(Domain, 5)



# Create 10 ranks
# Done...


# Create 100000 students
# seeder.add_entity(Student, 100000, {
#   'user': lambda x: users.pop(),
#   'last_lesson': lambda x: None,
#   'university': lambda x: choice(universities),
#   'group': lambda x: choice(groups)
#   })




# # Create 1000 teachers
# seeder.add_entity(Teacher, 1000, {
#   'user': lambda x: users.pop(),
#   'university': lambda x: choice(universities),
#   'domain': lambda x: choice(domains),
#   'degree': lambda x: choice([0,1,2]),
#   'title': lambda x: choice([0,1,2])
#   })




# # Create 2 subjects
# seeder.add_entity(Subject, 2)




# # Create 25 subsections
# seeder.add_entity(Subsection, 25)




# # Create 250 themes
# seeder.add_entity(Theme, 250)




# # Create 1000 tasks
# seeder.add_entity(Task, 1000)




# # Create 500 articles
# seeder.add_entity(Article, 500)




# # Create 250 videos
# seeder.add_entity(Video, 250)




# # Create 250 games
# seeder.add_entity(Game, 250)


# users = User.objects.all()

# tasks = [task for task in Task.objects.all()[500:]]

# tests = Test.objects.all()

# Create 500 tests
# seeder.add_entity(Test, 500, {
#   'task': lambda x: tasks.pop()
#   })


# Create 500 questions
# seeder.add_entity(Question, 250)
# seeder.add_entity(Question, 250, {
#   'task': lambda x: tasks.pop()
#   })

# seeder.add_entity(Question, 100000, {
#   'task': lambda x: None,
#     'test': lambda x: choice(tests)
#   })




# # Create 10000 explanations
# questions = Question.objects.all()
# authors = User.objects.all()

# seeder.add_entity(Explanation, 10000, {
#   'question': lambda x: choice(questions),
#   'author': lambda x: choice(authors)
#   })


from django.db import connection

# # Create 5000000 taskresults

# tasks = [task for task in Task.objects.all()] * 5000
# users = [user for user in User.objects.all()] * 50
# results = [random() for _ in range(5000000)]
# times = [datetime.now().strftime('%Y-%m-%d %H:%M:%S') for _ in range(5000000)]

# vals = zip(tasks, users, results, times)
# total_inserted = 0

# # (task, user, result, time)
# while True:
#     i = 0
#     query = 'INSERT INTO tasks_taskresult (task_id, user_id, result, "time") VALUES '
#     appendix = ""
#     for t, u, r, time in vals:
#         i += 1
#         appendix += "({}, {}, {}, '{}'),".format(t.pk, u.pk, r, time)
#         if i >= 10000:
#             appendix = appendix[:-1]
#             break
#     else:
#         break

#     full_query = query + appendix
#     with connection.cursor() as cursor:
#         cursor.execute(full_query)
    
#     total_inserted += 10000
#     print("{} records was inserted!".format(total_inserted))


# questions = [question for question in Question.objects.all()] * 50
# users = [user for user in User.objects.all()] * 50
# text_answers = [random_string(10) for _ in range(5000000)]
# bool_answers = [bool(randint(0,1)) for _ in range(5000000)]

# vals = zip(questions, users, text_answers, bool_answers)
# total_inserted = 0

# # # Create 5000000 useranswers

# # (question, user, result, time)
# while True:
#     i = 0
#     query = 'INSERT INTO tasks_useranswer (question_id, user_id, text_answer, bool_answer) VALUES '
#     appendix = ""
#     for q, u, t, b in vals:
#         i += 1
#         t, b = (t, 'null') if randint(0,1) else ('null', b)
#         appendix += "({}, {}, '{}', {}),".format(q.pk, u.pk, t, b)
#         if i >= 10000:
#             appendix = appendix[:-1]
#             break
#     else:
#         break

#     full_query = query + appendix
#     with connection.cursor() as cursor:
#         cursor.execute(full_query)
    
#     total_inserted += 10000
#     print("{} records was inserted!".format(total_inserted))

users = User.objects.all()
comments = Comment.objects.filter(parent__isnull=False)


# Create 10k upper comments/ 90 k lower
# seeder.add_entity(Comment, 90000, {
#     'author': lambda x: choice(users),
#     'parent': lambda x: choice(comments)
#     })



#Create events (90k)
seeder.add_entity(Event, 90000, {
    'time': lambda x: datetime.now(),
    'comment': lambda x: choice(comments)
    })


# Create notifications (90k)
seeder.add_entity(Notification, 90000, {
    'user': lambda x: choice(users),
    })




inserted = seeder.execute()
