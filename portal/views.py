from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string
from forms import *

def home(request):
    context = {}
    if request.user.is_authenticated():
        context['school'] = request.user.student.school.name
        context['streams'] = Stream.objects.filter(is_active=True)
        return render(request, 'portal/index.html', context)
    else:
        context['signup_form'] = SignupForm()
        context['login_form'] = LoginForm()
        return render(request, 'portal/landing_page.html', context)

def signup(request):
    if request.method == 'POST':
        context = {}
        form = SignupForm(request.POST)
        if not form.is_valid():
            context['signup_form'] = form
            context['login_form'] = LoginForm()
            return render(request, 'portal/landing_page.html', context)
        cd = form.cleaned_data
        user = form.save()
        school = School.objects.get(email_handle=cd['username'].split('@')[1])
        student = Student(user=user, school=school)
        student.save()
        login_user = authenticate(username=cd['username'],
                                  password=cd['password1'])
        login(request, login_user)
        return redirect(reverse('home'))
    else:
        raise Http404

def login_path(request):
    if request.method == 'POST':
        context = {}
        form = LoginForm(request.POST)
        if not form.is_valid():
            context['signup_form'] = SignupForm()
            context['login_form'] = form
            return render(request, 'portal/landing_page.html', context)
        user = authenticate(username=form.cleaned_data['email'],
                            password=form.cleaned_data['password'])
        if user is None:
            context['no_user_found'] = True
            context['signup_form'] = SignupForm()
            context['login_form'] = form
            return render(request, 'portal/landing_page.html', context)
        else:
            login(request, user)
        return redirect(reverse('home'))
    else:
        raise Http404

def logout_path(request):
    logout(request)
    return redirect(reverse('home'))

def stream(request):
    if request.user.is_authenticated():
        context = {}
        context['courses'] = request.user.student.ta_courses.all()
        return render(request, 'portal/stream.html', context)
    else:
        raise Http404

def stream_course(request, course_id):
    if request.user.is_authenticated():
        context = {}
        course = get_object_or_404(Course, pk=course_id)
        student = request.user.student
        if course not in student.ta_courses.all():
            raise Http404
        key = get_random_string(length=32)
        while Stream.objects.filter(stream_key=key).first() is not None:
            key = get_random_string(length=32)
        stream = Stream(
            course=course, streamer=student, is_active=True,
            stream_key=key)
        stream.save()
        context['stream'] = stream
        return render(request, 'portal/stream_course.html', context)
    else:
        raise Http404

def view_stream(request, stream_id):
    if request.user.is_authenticated():
        context = {}
        stream = get_object_or_404(Stream, pk=stream_id)
        if stream.course.school != request.user.student.school:
            raise Http404
        if not stream.is_active:
            return redirect(reverse('home'))
        context['stream'] = stream
        return render(request, 'portal/view_course.html', context)
    else:
        raise Http404

def end_stream(request, stream_id):
    if request.user.is_authenticated():
        context = {}
        stream = get_object_or_404(Stream, pk=stream_id)
        if stream.streamer != request.user.student:
            raise Http404
        stream.is_active = False
        stream.save()
        return HttpResponse('')
    else:
        raise Http404


























