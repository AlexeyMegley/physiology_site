from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import Subject, Subsection, Theme


def index(request):
	user = request.user.pk
	subsections = [subject.subsections.all() for subject in Subject.objects.all()]
	return render(request, 'study/index.html', {'subsections': subsections, 'user_id': user})


def show_subsection(request, pk):
	try:
	    subsection = Subsection.objects.get(pk=pk)
	except Subsection.DoesNotExist:
		return Http404('Данного раздела не существует')
	return render(request, 'study/section.html', {'subsection': subsection})


def show_theme(request, pk):
	try:
		theme = Theme.objects.get(pk=pk)
	except Theme.DoesNotExist:
		return Http404('Данной темы не существует')
	return render(request, 'study/theme.html', {})
