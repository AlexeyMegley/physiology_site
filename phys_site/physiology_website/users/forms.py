from django import forms

from .models import Student, Teacher


class StudentCreationForm(forms.ModelForm):
    
    class Meta:
        model = Student
        fields = '__all__'


class TeacherCreationForm(forms.ModelForm):
    
    class Meta:
        model = Teacher
        fields = '__all__'
