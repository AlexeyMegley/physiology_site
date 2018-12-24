from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Task(models.Model):
    
    complexity_choices = ((0, 'Простое задание'), (1, 'Средняя сложность'), (2, 'Сложное задание'),)

    name = models.CharField(max_length=255)
    is_mandatory = models.BooleanField(default=True)
    points = models.FloatField()
    threshold = models.FloatField()
    max_attempts = models.PositiveIntegerField(default=1000)
    complexity = models.IntegerField(choices=complexity_choices, default=0)

    def is_test(self):
        pass

    def is_question(self):
        pass

    def best_attempt_for(self, user):
        """ Get best result of this user """
        return self.taskresult_set.aggregate(models.Max('result')).get('result__max', 0)

    def is_passed_by(self, user):
        """ Get current status for this user """
        return self.best_attempt_for(user) >= self.threshold

    def attempts_remain(self, user):
        """ Get remaining attempts for this user """
        return self.max_attempts - self.taskresult_set.filter(models.Q(user=user)).count()

    def __str__(self):
        return self.name.capitalize()


class Test(models.Model):
    
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    multianswers = models.BooleanField(default=False)
    size = models.PositiveIntegerField(null=True, blank=True)

    def get_questions_chunk(self):
        pass

    def question_amount(self):
        pass

    def __str__(self):
        return 'Test' + str(self.pk)


class QuestionManager(models.Manager):

    def most_problematic(self, number, user=None, theme=None):

        """ Get most problematic questions with selected filters """

        assert number > 0 and isinstance(number, int), "Number should be an integer greater than zero"

        pass


class Question(models.Model):

    task = models.OneToOneField(Task, on_delete=models.CASCADE, null=True, blank=True, related_name='question_task')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, null=True, blank=True, related_name='question_tests')
    description = models.TextField(blank=False, null=False)
    text_answer = models.TextField(blank=True, null=True)
    bool_answer = models.BooleanField(blank=True, null=True)
    objects = QuestionManager()

    def save(self, *args, **kwargs):
        """ Check that at least one of task/test and text_answer/bool_answer is not empty """
        assert self.task or self.test, "Either task or test should be not empty!"
        assert self.text_answer or (self.bool_answer is not None), "Question should have answer!"
        super().save(*args, **kwargs)

    def __str__(self):
        pass


class Explanation(models.Model):

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=False, null=False)

    def __str__(self):
        return 'Question' + str(self.pk)


class UserAnswer(models.Model):
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    bool_answer = models.BooleanField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        """ Check that at least one of two answer fields is not empty """
        assert self.text_answer or (self.bool_answer is not None)
        super(self, UserAnswer).save(*args, **kwargs)

    def is_correct(self):
        pass

    def __str__(self):
        return 'UserAnswer' + str(self.pk)


class Article(models.Model):
    
    title = models.TextField(blank=False)
    text = models.TextField(blank=False)
    references = models.TextField(blank=True)

    """ """

    def __str__(self):
        return self.title.capitalize()


class Video(models.Model):
    
    name = models.CharField(max_length=255)
    link = models.TextField(validators=[URLValidator()])

    """ """

    def __str__(self):
        return self.name.capitalize()


class Game(models.Model):

    name = models.CharField(max_length=255)
    task = models.ForeignKey(Task, blank=True, null=True, on_delete=models.SET_NULL)
    rules = models.TextField(blank=True, null=True)

    """ """

    def __str__(self):
        return self.name.capitalize()


class TaskResult(models.Model):
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    result = models.FloatField(validators=[MaxValueValidator(1)])
    time = models.DateTimeField(auto_now_add=True)

    """ """

    def __str__(self):
        return "{}, задание '{}', результат: {:6.2f}%".format(self.user.get_full_name(), self.task, self.result * 100)


@receiver(post_save, sender=TaskResult)
def fix_user_score(sender, instance, created, **kwargs):

    """ Check if task was passed and update user score """

    # check if object wasn't created
    if not created:
        return

    # check if task wasn't solved before
    best_previous_result = TaskResult.objects.exclude(pk=instance.pk) \
                                             .filter(models.Q(task=instance.task) & models.Q(user=instance.user)) \
                                             .aggregate(models.Max('result')) \
                                             .get('result', 0)

    if best_previous_result >= instance.task.threshold:
        return

    # add points to user
    if instance.result > instance.task.threshold:
        instance.user.student.total_score += instance.task.points
        instance.user.student.save()
