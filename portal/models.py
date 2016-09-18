from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class School(models.Model):
    admin_user = models.OneToOneField(User, on_delete=models.CASCADE,
                                      related_name='admin_school')
    name = models.CharField(max_length=255)
    email_handle = models.CharField(max_length=255)

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='professor')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

class Course(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    course_number = models.CharField(max_length=255)
    course_name = models.CharField(max_length=255)

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='student')
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    ta_courses = models.ManyToManyField(Course, related_name='tas')

    def __unicode__(self):
        return self.user.username

class Stream(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    streamer = models.ForeignKey(Student, on_delete=models.CASCADE)
    stream_key = models.CharField(max_length=255)
    is_active = models.BooleanField()
