from django.test import TestCase
from django.contrib.auth.models import User
from users.models import *
from study.models import *
from tasks.models import *
from social_network import *


class TestModels(TestCase):

    def setUp(self):

        # Create 2 users
        self.user1 = User.objects.create_user('alice', 'nfnvrbveiei@gmail.com', 'alicepassword')
        self.user2 = User.objects.create_user('alex', 'fhghhghgh@gmail.com', 'alexpassword')

        self.country = Country.objects.create(name='Russia')

        self.city = City.objects.create(country=self.country, name='Saint-Petersburg')

        self.uni1 = University.objects.create(city=self.city, name='North-West State Medical University')
        self.uni2 = University.objects.create(city=self.city, name='State Medical University of Pavlov')

        self.group1 = Group.objects.create(university=self.uni1, number='523')
        self.group2 = Group.objects.create(university=self.uni2, number='621')

        # Create 2 students from 2 different universities
        self.student1 = Student.objects.create(user=self.user1, university=self.uni1, group=self.group1)
        self.student2 = Student.objects.create(user=self.user2, university=self.uni2, group=self.group2)

        # Create 3 comments
        self.comment1 = Comment.objects.create(author=self.user1, text="Root comment")
        self.comment2 = Comment.objects.create(author=self.user2, text="First child comment", parent=self.comment1)
        self.comment3 = Comment.objects.create(author=self.user1, text="Second child comment", parent=self.comment1)

        # Create 2 tasks
        self.task1 = Task.objects.create(name='Correspondance', is_mandatory=True, points=8, threshold=0.8)
        self.task2 = Task.objects.create(name='Multiple answer test', is_mandatory=True, points=12, threshold=0.8)

        # Create 2 themes
        self.theme1 = Theme.objects.create(name='Physiology of heart muscle')
        self.theme2 = Theme.objects.create(name='Sympatholitics')

        self.theme1.tasks.add(self.task1)
        self.theme2.tasks.add(self.task2)

        self.theme1.root_comments.add(self.comment1)

        # Create 2 subsections
        self.subsect1 = Subsection.objects.create(name='Physiology of cardiovascular system')
        self.subsect2 = Subsection.objects.create(name='Adrenomimethics and adrenoblockators')

        self.subsect1.themes.add(self.theme1)
        self.subsect2.themes.add(self.theme2)

        # Create 2 subjects
        self.subject1 = Subject.objects.create(name='Physiology')
        self.subject2 = Subject.objects.create(name='Pharmacology')

        self.subject1.subsections.add(self.subsect1)
        self.subject2.subsections.add(self.subsect2)

        # Create teacher
        self.domain = Domain.objects.create(name='Physiology')
        self.user3 = User.objects.create_user('Ms Williams', 'jfhhfehfnwer@gmail.com', 'teacherpass')
        self.teacher = Teacher.objects.create(user=self.user3, university=self.uni1, domain=self.domain, degree=1, title=1)

        self.teacher.tracked_groups.add(self.group1)
        self.teacher.tracked_groups.add(self.group2)

    def test_points_by_subjects(self):
        # Get student, test that all points is equal to zero
        assert self.student1.total_score == 0, "Student total score is not equal to zero"

        # Create one TaskResult
        tr1 = TaskResult.objects.create(task=self.task1, user=self.user1, result=1)

        # Check that student's points were changed
        assert self.student1.total_score > 0, "Student score wasn't increased"

    def test_global_rank(self):

        # Add 2 TaskResult's (in the different subjects) to second user
        tr1 = TaskResult.objects.create(task=self.task1, user=self.user2, result=1)
        tr2 = TaskResult.objects.create(task=self.task2, user=self.user2, result=1)

        # Check that he is number 1 in rating now
        rank1 = self.student1.global_rank()
        rank2 = self.student2.global_rank()
        assert rank2 < rank1, "Rank2 expected 1, actual {}. Rank1 expected 2, actual {}".format(rank2, rank1)

    def test_subject_rank(self):

        tr1 = TaskResult.objects.create(task=self.task1, user=self.user1, result=1)

        tr2 = TaskResult.objects.create(task=self.task1, user=self.user2, result=1)
        tr3 = TaskResult.objects.create(task=self.task2, user=self.user2, result=1)

        # Check that user number 2 is higher in subject number 2 than first student
        rank1 = self.student1.subject_rank(self.subject2)
        rank2 = self.student2.subject_rank(self.subject2)
        assert rank2 < rank1, '''
                                 Rank1 - expected 2, actual {}. 
                                 Rank2 - expected 1, actual {}.
                                 Subject1 = {}, subject2 = {}.
                                 Student1 points = {}, student2 points = {}
                              '''.format(rank1, rank2, self.subject1, self.subject2,
                                         [row for row in self.student1.points_by_subjects()], 
                                         [row for row in self.student2.points_by_subjects()])

        # Check that users have equal rank in the firts subject
        rank1 = self.student1.subject_rank(self.subject1)
        rank2 = self.student2.subject_rank(self.subject1)
        assert rank1 == rank2, '''Rank1 - expected 1, actual {}. Rank2 - expected 1, actual {}'''.format(rank1, rank2)

    def test_tracked_students(self):
        # Check that both students are tracked 
        assert all(filter(lambda stud: stud in self.teacher.tracked_students(), (self.student1, self.student2))), \
               "Not all students are presented in tracked_students"

    def test_uni_total_score(self):
        # Check that scores of universities are equal to the scores of the students
        assert self.uni1.total_score() == self.student1.total_score, "Score uni1 != score student1"
        assert self.uni2.total_score() == self.student2.total_score, "Score uni2 != score student2"

    def test_uni_global_rank(self):
        # Check that global ranks of the universities are equal to the global ranks of the students
        assert self.uni1.global_rank() == self.student1.global_rank(), "Rank uni1 != rank student1"
        assert self.uni2.global_rank() == self.student2.global_rank(), "Rank uni2 != rank student2"        

    def test_group_total_score(self):
        # Check that global ranks of the groups are equal to the global ranks of the students
        assert self.group1.total_score() == self.student1.total_score, "Score group1 != score student1"
        assert self.group2.total_score() == self.student2.total_score, "Score group2 != score student2"

    def test_group_global_rank(self):
        # Check that global rank of the groups are equal to 1 since it's only one group in the university
        assert self.group1.global_rank() == 1, "Rank of the group1 is not equal to 1"
        assert self.group2.global_rank() == 1, "Rank of the group1 is not equal to 1"

    def test_comments(self):

        # Check that child comment is actually in the childs
        assert self.comment2 in self.comment1.childs(), "{} not in {}".format(self.comment2, self.comment1.childs())

        # Check that it's related to the parent
        assert self.comment2.is_related(self.comment1), "Comment2 is not related to it's parent"

        # Check that 2nd and 3rd are related with each other
        assert self.comment2.is_related(self.comment3), "Comment2 is not related to it's brother"
