from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http.response import HttpResponse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string
from forms import *

def home(request):
    context = {}
    if request.user.is_authenticated():
        if hasattr(request.user, 'admin_school'):
            context['school'] = request.user.admin_school.name
            context['professors'] = Professor.objects.filter(
                school=request.user.admin_school, is_active=True)
            context['professors_awaiting_approval'] = Professor.objects.filter(
                school=request.user.admin_school, is_active=False)
            context['recommendations'] = (CourseRecommendation.objects
                .filter(school=request.user.admin_school)
                .order_by('-num_recommendations'))
            return render(request, 'portal/school_admin_index.html', context)
        elif hasattr(request.user, 'professor'):
            context['school'] = request.user.professor.school.name
            context['courses'] = Course.objects.filter(
                professor=request.user.professor)
            return render(request, 'portal/professor_index.html', context)
        elif hasattr(request.user, 'student'):
            context['school'] = request.user.student.school.name
            streams = Stream.objects.filter(
                is_active=True, course__school=request.user.student.school)
            streams = streams.filter(
                Q(course__roster__in=[request.user.student])
              | Q(course__roster=None))
            subscription_streams = Stream.objects.filter(
                is_active=True, course__school=request.user.student.school,
                course__in=request.user.student.subscriptions.all())
            context['streams'] = streams
            context['subscription_streams'] = subscription_streams
            return render(request, 'portal/index.html', context)
    else:
        context['signup_form'] = SignupForm()
        context['login_form'] = LoginForm()
        return render(request, 'portal/landing_page.html', context)

def about(request):
    context = {}
    return render(request, 'portal/about.html', context)
    
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
        if cd['is_professor']:
            professor = Professor(user=user, school=school, is_active=False)
            professor.save()
            context['signup_form'] = SignupForm()
            context['login_form'] = LoginForm()
            context['professor_signed_up'] = True
            return render(request, 'portal/landing_page.html', context)
        else:
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
        elif hasattr(user, 'professor') and not user.professor.is_active:
            context['professor_inactive'] = True
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
        if (Stream.objects.filter(
            is_active=True, course=course, streamer=student).first()):
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

def activate_professor(request, professor_id):
    professor = get_object_or_404(Professor, pk=professor_id)
    if (request.user.is_authenticated()
        and professor.school == request.user.admin_school):
        context = {}
        professor.is_active = True
        professor.save()
        context['notification'] = (
            "Professor account for %s has been activated." 
            % professor.user.username)
        context['professors'] = Professor.objects.filter(
            school=request.user.admin_school, is_active=True)
        context['professors_awaiting_approval'] = Professor.objects.filter(
            school=request.user.admin_school, is_active=False)
        return render(request, 'portal/school_admin_index.html', context)
    else:
        raise Http404

def delete_professor(request, professor_id):
    professor = get_object_or_404(Professor, pk=professor_id)
    if (request.user.is_authenticated()
        and professor.school == request.user.admin_school):
        context = {}
        context['notification'] = (
            "Professor account for %s has been activated." 
            % professor.user.username)
        professor.delete()
        context['professors'] = Professor.objects.filter(
            school=request.user.admin_school, is_active=True)
        context['professors_awaiting_approval'] = Professor.objects.filter(
            school=request.user.admin_school, is_active=False)
        return render(request, 'portal/school_admin_index.html', context)
    else:
        raise Http404

def add_course(request):
    context = {}
    if (request.user.is_authenticated() and hasattr(request.user, 'professor')):
        if request.method == 'GET':
            form = CourseForm()
            form.fields['tas'].queryset = (
                Student.objects.filter(school=request.user.professor.school))            
            form.fields['roster'].queryset = (
                Student.objects.filter(school=request.user.professor.school))            
            context['form'] = form
            return render(request, 'portal/add_course.html', context)
        elif request.method == 'POST':
            form = CourseForm(request.POST)
            form.fields['tas'].queryset = (
                Student.objects.filter(school=request.user.professor.school))            
            form.fields['roster'].queryset = (
                Student.objects.filter(school=request.user.professor.school))            
            if not form.is_valid():
                context['form'] = form
                return render(request, 'portal/add_course.html', context)
            cd = form.cleaned_data
            course = form.save(commit=False)
            course.professor = request.user.professor
            course.school = request.user.professor.school
            course.save()
            for ta in cd['tas']:
                course.tas.add(ta)
            for student in cd['roster']:
                course.roster.add(student)
            course.save()
            return redirect(reverse('home'))
        else:
            raise Http404
    else:
        raise Http404

def edit_course(request, course_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    context['course'] = course
    if (request.user.is_authenticated() and hasattr(request.user, 'professor')
        and course.professor == request.user.professor):
        if request.method == 'GET':
            form = CourseForm(instance=course)
            form.fields['tas'].queryset = (
                Student.objects.filter(school=request.user.professor.school))
            form.fields['tas'].initial = course.tas.all()            
            form.fields['roster'].queryset = (
                Student.objects.filter(school=request.user.professor.school))
            form.fields['roster'].initial = course.roster.all()            
            context['form'] = form
            return render(request, 'portal/edit_course.html', context)
        elif request.method == 'POST':
            form = CourseForm(request.POST, instance=course)
            form.fields['tas'].queryset = (
                Student.objects.filter(school=request.user.professor.school))            
            form.fields['roster'].queryset = (
                Student.objects.filter(school=request.user.professor.school))
            if not form.is_valid():
                context['form'] = form
                return render(request, 'portal/edit_course.html', context)
            cd = form.cleaned_data
            course = form.save()
            course.tas.clear()
            course.roster.clear()
            for ta in cd['tas']:
                course.tas.add(ta)
            for student in cd['roster']:
                course.roster.add(student)
            course.save()
            form.fields['tas'].initial = course.tas.all()            
            form.fields['roster'].initial = course.roster.all()            
            context['course_saved'] = True
            context['form'] = form
            return render(request, 'portal/edit_course.html', context)
        else:
            raise Http404
    else:
        raise Http404

def courses(request):
    context = {}
    if (request.user.is_authenticated() and hasattr(request.user, 'student')):
        courses = Course.objects.filter(school=request.user.student.school)
        courses = courses.filter(
            Q(roster__in=[request.user.student])
          | Q(roster=None))
        course_list = []
        for course in courses:
            if course in request.user.student.subscriptions.all():
                course_list.append((course, True))
            else:
                course_list.append((course, False))
        context['courses'] = course_list
        context['school'] = request.user.student.school.name
        return render(request, 'portal/courses.html', context)
    else:
        raise Http404

def subscription(request, course_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    context['course'] = course
    if (request.user.is_authenticated() and hasattr(request.user, 'student')
        and course.school == request.user.student.school):
        if course in request.user.student.subscriptions.all():
            request.user.student.subscriptions.remove(course)
        else:
            request.user.student.subscriptions.add(course)
        return redirect(reverse('courses'))
    else:
        raise Http404

def recommend(request):
    context = {}
    if (request.user.is_authenticated() and hasattr(request.user, 'student')):
        if request.method == 'GET':
            context['form'] = CourseRecommendationForm()
            return render(request, 'portal/recommend.html', context)
        elif request.method == 'POST':
            form = CourseRecommendationForm(request.POST)
            if not form.is_valid():
                context['form'] = form
                return render(request, 'portal/recommend.html', context)
            else:
                course_num = form.cleaned_data['course_num']
                if (CourseRecommendation.objects
                    .filter(course_number=course_num,
                        school=request.user.student.school)
                    .exists()):
                    rec = CourseRecommendation.objects.get(
                        course_number=course_num,
                        school=request.user.student.school)
                    rec.num_recommendations = rec.num_recommendations + 1
                    rec.save()
                else:
                    rec = CourseRecommendation.objects.create(
                        course_number=course_num,
                        num_recommendations=1,
                        school=request.user.student.school)
                context['notification'] = "Thank you for your recommendation."
                context['form'] = CourseRecommendationForm
                return render(request, 'portal/recommend.html', context)
        else:
            raise Http404
    else:
        raise Http404
















