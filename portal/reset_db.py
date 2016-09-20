from portal.models import *

<<<<<<< HEAD
cmu_admin = User.objects.create(username='cmuadmin@andrew.cmu.edu', password='carnegie123')
=======
cmu_admin = User.objects.create(username='cmu_admin@andrew.cmu.edu', password='carnegie123')
>>>>>>> 9894cc0a4f6817b2a4407b02e9b120f5b90b7062
cmu_admin.set_password('carnegie123')
cmu_admin.save()
cmu = School.objects.create(name="Carnegie Mellon University", email_handle="andrew.cmu.edu", admin_user=cmu_admin)

prof1_user = User.objects.create(username='prof1@andrew.cmu.edu', password='carnegie123')
prof1_user.set_password('carnegie123')
prof1_user.save()
prof1 = Professor.objects.create(user=prof1_user, school=cmu)

course1 = Course.objects.create(school=cmu, professor=prof1, course_number='67373', course_name = 'Software Development Project')

renzo_user = User.objects.create(username='mrbautis@andrew.cmu.edu', password='carnegie123')
renzo_user.set_password('carnegie123')
renzo_user.save()
renzo = Student.objects.create(user=renzo_user, school=cmu)
renzo.ta_courses.add(course1)

