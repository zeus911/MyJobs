from django.contrib import admin
from django import forms

from mydashboard.models import (
    DashboardModule,
    CompanyUser,
)
from myjobs.models import User


admin.site.register(CompanyUser)
