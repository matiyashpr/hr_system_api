from django.contrib import admin

from hr_system.models import Candidate, Recruiter, Category, Skills, User

admin.site.register(Candidate)
admin.site.register(Category)
admin.site.register(Skills)
admin.site.register(Recruiter)
admin.site.register(User)
