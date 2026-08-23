from django.forms import ModelForm
from django.utils.translation import gettext as _
from .models import UserLog


class UserLogForm(ModelForm):
    class Meta:
        model = UserLog
        exclude = ['timestamp', 'user', 'user_class']