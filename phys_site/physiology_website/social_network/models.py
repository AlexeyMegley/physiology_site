from django.db import models
from django.contrib.auth.models import User


class Comment(models.Model):

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    posted_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL)
    
    def childs(self):
        """ Get child comments """
        return self.comment_set.all()

    def delete(self):
        
        """ Delete comment text and author if there are child comments else delete comment """

        if self.childs().count():
            self.author = None
            self.text = "Комментарий был удален"
            self.save()
            return

        super().delete()

    def is_related(self, other_comment):
        """ Check if this comment is a parent of other or if they share common parent """
        return other_comment == self.parent or other_comment.parent in (self, self.parent)

    def __str__(self):
        return "Комментарий '{}' от {}".format(self.author or 'Удаленный пользователь', self.posted_at.strftime('%Y-%m-%d %H:%M:%S'))


class Event(models.Model):
    
    time = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(Comment, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return 'Event {}'.format(self.pk)


class Notification(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    """ """

    def __str__(self):
        return "Уведомление пользователю {}".format(self.user)
