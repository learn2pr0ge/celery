from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

#class SignUpForm(UserCreationForm):
#    email = forms.EmailField(label="Email")
#    first_name = forms.CharField(label="Имя")
#    last_name = forms.CharField(label="Фамилия")

#    class Meta:
#        model = User
#        fields = (
#            "username",
#            "first_name",
#            "last_name",
#            "email",
#            "password1",
#            "password2",
#        )

#добавление юзера в группу common_users




class CustomSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        common_users = Group.objects.get(name="authors")
        user.groups.add(common_users)
        return user