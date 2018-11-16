from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Task(models.Model):
    
    name = models.CharField(max_length=255)
    is_mandatory = models.BooleanField(default=True)
    points = models.FloatField()
    threshold = models.FloatField()
    max_attempts = models.PositiveIntegerField(default=1000)

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
