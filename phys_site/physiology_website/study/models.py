from django.db import models, connection

# Correct sql table for running tests

class Subject(models.Model):
    
    name = models.CharField(max_length=255, unique=True)
    subsections = models.ManyToManyField('Subsection', blank=True)

    def students_ranks(self):
        """ Get ranks of all students grouped by this subject """
        with connection.cursor() as cursor:
            cursor.execute(
                '''
                WITH tasks_in_subject AS (
                    SELECT TR.user_id, SUM(TT.points) as total
                    FROM study_subject SS JOIN study_subject_subsections SSS ON SSS.subject_id=SS.id
                              JOIN study_subsection_themes SST ON SST.subsection_id=SSS.subsection_id
                              JOIN study_theme_tasks STT ON SST.theme_id=STT.theme_id
                              JOIN tasks_task TT ON STT.task_id=TT.id
                              JOIN tasks_taskresult TR ON TT.id=TR.task_id
                    WHERE SS.id=%s AND TR.result >= TT.threshold GROUP BY TR.user_id
                    )

                SELECT user_id, rank() OVER (ORDER BY total DESC) FROM tasks_in_subject;
                ''', [self.pk])
            result = cursor.fetchall()

        return result

    def __str__(self):
        return self.name.capitalize()


class Subsection(models.Model):
    
    name = models.CharField(max_length=255, unique=True)
    themes = models.ManyToManyField('Theme', blank=True)

    def __str__(self):
        return self.name.capitalize()


class Theme(models.Model):
    
    name = models.CharField(max_length=255)
    tasks = models.ManyToManyField('tasks.Task', blank=True)
    videos = models.ManyToManyField('tasks.Video', blank=True)
    articles = models.ManyToManyField('tasks.Article', blank=True)
    games = models.ManyToManyField('tasks.Game', blank=True)
    root_comments = models.ManyToManyField('social_network.Comment', blank=True)
    
    def total_points(self):
        """ Get total points, that could be gained by completing all tasks """
        return self.tasks.aggregate(models.Sum('points')).get('points__sum', 0)

    def __str__(self):
        return self.name.capitalize()
