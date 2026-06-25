from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import User

user = get_user_model()

class EmailUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label= 'Пароль',
        widget= forms.PasswordInput(attrs= {
            'placeholder': 'Введи пароль',
            'class': 'input-field'
        })
    )
    password2 = forms.CharField(
        label= 'Підтверди пароль',
        widget= forms.PasswordInput(attrs= {
            'placeholder': 'Повтори пароль',
            'class': 'input-field'
        })
    )
    # 
    class Meta:
        model = user
        fields = ('email',)
        widgets = {
            'email': forms.EmailInput(attrs= {
                'placeholder': 'you@example.com',
                'class': 'input-field'
            })
        }
    # 
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email= email).exists():
            raise forms.ValidationError('Користувач з таким email вже існує')
        return email
    # 
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Паролі не співпадають')
        return cleaned_data
    # 
    def save(self, commit= True): # якщо commit= True створити запис у БД
        user : User = super().save(commit= False) # але спочатку створи об'єкт користувача
        user.username = ''
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user   
    
class EmailAuthenticatedForm(AuthenticationForm):
    username = forms.EmailField(
        label= 'Електронна пошта',
        widget= forms.EmailInput(attrs= {
            'placeholder': 'you@example.com',
            "autofocus": True,
            "autocomplete": "email",
            'class': 'input-field'
        })
    )
    password = forms.CharField(
        label= 'Пароль',
        widget= forms.PasswordInput(attrs= {
            'placeholder': 'Введи пароль',
            "autocomplete": "current-password",
            'class': 'input-field'
        })
    )
    error_messages = {
        'invalid_login': 'Невірний логін або пароль',
        'inactive': 'Цей акаунт неактивний'
    }
    # 
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user_cache = authenticate(
                request= self.request,
                username= email,
                password= password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code= 'invalid_login'
                )
            else:
                self.confirm_login_allowed(self.user_cache)
                
        return self.cleaned_data
    
    
    
    
    
    
    