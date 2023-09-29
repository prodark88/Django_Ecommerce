from django import forms
from .models import Account , UserProfile


class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    confirm_password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = Account
        fields = ['first_name', 'last_name','email','phone_number','password', 'confirm_password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields ['first_name'].widget.attrs['placeholder']='Ingrese su nombre'
        self.fields ['last_name'].widget.attrs['placeholder']='Ingrese su apellido'
        self.fields ['email'].widget.attrs['placeholder']='Email'
        self.fields ['phone_number'].widget.attrs['placeholder']='Telefono'
        self.fields ['password'].widget.attrs['placeholder']='Ingrese contraseña'
        self.fields ['confirm_password'].widget.attrs['confirma_password']='Confirme contraseña'

        for field  in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

    def clean(self):
        cleanend_data = super(RegistrationForm,self).clean()
        password = cleanend_data.get('password')
        confirm_password = cleanend_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
            " las contraseñas no coincidens"
            )

#trabaja coan el modelo account
class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm ,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
#trabaja con el modelo userprofile
class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'invalid':('solo archivos de imagen')}, widget=forms.FileInput)
    class Meta: 
        model = UserProfile
        fields = ('address_line1', 'address_line2','city','state','country','profile_picture')


    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'