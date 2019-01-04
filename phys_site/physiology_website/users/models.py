from django.db import models
from django.contrib.auth.models import User
from django.db.models.expressions import Window
from django.db.models.functions import Rank

from social_network.models import Notification, Comment
from study.models import Subject


class Student(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey('Group', null=True, blank=True, on_delete=models.SET_NULL)
    last_lesson = models.ForeignKey('study.Theme', null=True, blank=True, on_delete=models.SET_NULL)
    favorite_subjects = models.ManyToManyField('study.Subsection', blank=True)
    total_score = models.FloatField(default=0)

    class Meta:
        indexes = [
           models.Index(fields=['group']),
        ]
        
    def points_by_subjects(self):

        """ Get points for different subjects """

        result = Subject.objects.raw(
            '''
            WITH solved_tasks as (SELECT TR.id FROM tasks_taskresult TR JOIN tasks_task T ON TR.task_id=T.id
                                  WHERE TR.user_id=%s AND TR.result >= T.threshold)

            SELECT 1 as id, SS.name, SUM(TT.points) as total 
            FROM study_subject SS JOIN study_subject_subsections SSS ON SSS.subject_id=SS.id
                                  JOIN study_subsection_themes SST ON SST.subsection_id=SSS.subsection_id
                                  JOIN study_theme_tasks STT ON SST.theme_id=STT.theme_id
                                  JOIN tasks_task TT ON STT.task_id=TT.id
                                  JOIN tasks_taskresult TR ON TT.id=TR.task_id
            WHERE TR.id IN (SELECT id FROM solved_tasks) GROUP BY SS.name
            ''', [self.user_id])

        return result
        
    def global_rank(self):
        """ Get rank amidst all students """
        result = Student.objects.raw(
            '''
              SELECT id, rank FROM (SELECT id, rank() OVER (ORDER BY total_score DESC) 
              FROM users_student) R WHERE id=%s
            ''', [self.pk])[0]

        return result.rank

    def subject_rank(self, subject):
        """ Get rank amidst all students grouped by subject """
        result = subject.students_ranks()
        rank = 1
        for row in result:
            rank += 1
            if row[0] == self.user.pk:
                return row[1]
        return rank
    
    def notifications(self):
        """ Get student notifictions """
        return Notification.objects.filter(user=self.user)
    
    def comments(self):
        """ Get student comments """
        return Comment.objects.filter(user=self.user)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


class Teacher(models.Model):

    degreee_choices = ((0, 'Не указано'), (1, 'Кандидат наук'), (2, 'Доктор наук'))
    title_choices = ((0, 'Не указано'), (1, 'Доцент'), (2, 'Профессор'))

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    university = models.ForeignKey('University', on_delete=models.CASCADE)
    domain = models.ForeignKey('Domain', on_delete=models.CASCADE)
    degree = models.IntegerField(choices=degreee_choices, default=0)
    title = models.IntegerField(choices=title_choices, default=0)
    favorite_subjects = models.ManyToManyField('study.Subject', blank=True)
    tracked_groups = models.ManyToManyField('Group', blank=True)
    
    def tracked_students(self):
        """ Get all students from tracked groups """
        return Student.objects.filter(models.Q(group__university=self.university) & models.Q(group__in=self.tracked_groups.all()))
    
    def __str__(self):
        return self.user.first_name.capitalize() + ' ' + self.user.last_name.capitalize()


class Country(models.Model):

    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name.capitalize()


class City(models.Model):

    country = models.ForeignKey('Country', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']
        unique_together = (('country', 'name'), )

    def __str__(self):
        return "{}, {}".format(self.name.capitalize(), self.country)


class Domain(models.Model):

    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class University(models.Model):
    
    city = models.ForeignKey('City', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']
    
    def total_score(self):
        """ Get total university score """
        return sum(group.total_score() for group in self.group_set.all())
    
    def global_rank(self):

        """ Get university rank """

        result = Student.objects.raw(
            '''
                SELECT id, rank FROM 

                (
                  SELECT id, university_id, total, rank() OVER (ORDER BY total DESC) FROM

                  (
                    SELECT 1 as id, university_id, SUM(total_score) as total 
                           FROM users_student US JOIN users_group UG ON US.group_id=UG.id
                           GROUP BY university_id
                  ) universities_scores

                ) university_ranks

                WHERE university_id=%s

            ''', [self.pk])[0]

        return result.rank

    def __str__(self):
        return self.name


class Group(models.Model):

    university = models.ForeignKey('University', on_delete=models.CASCADE)
    number = models.CharField(max_length=20)

    class Meta:
        ordering = ['number']
        unique_together = (("university", "number"), )
    
    def students(self):
        """ Get all students from this group """
        return self.student_set.all()
    
    def total_score(self):
        """ Get total group score """
        return self.student_set.aggregate(models.Sum('total_score')).get('total_score__sum', 0)
    
    def global_rank(self):

        """ Get group rank in its university """

        result = Student.objects.raw(
            '''
                SELECT id, group_id, rank FROM 

                (
                    SELECT id, group_id, rank() OVER (ORDER BY T.points DESC) FROM 

                    (
                      SELECT 1 as id, group_id, SUM(total_score) as points 
                      FROM users_student
                      GROUP BY group_id
                    ) T

                ) rank_table

                WHERE group_id=%s
                
            ''', [self.pk])[0]

        return result.rank

    def __str__(self):
        return self.number


class Rank(models.Model):

    threshold = models.PositiveIntegerField()
    rank = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['threshold']

    def __str__(self):
        return self.rank.capitalize()


""" ============================ Managers class here =============================== """

