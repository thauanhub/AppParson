from django.forms import ModelForm
from django.utils.translation import gettext as _
from .models import UserLog


class UserLogForm(ModelForm):
    class Meta:
        model = UserLog
        exclude = ['timestamp', 'user', 'error_type', 'user_class']