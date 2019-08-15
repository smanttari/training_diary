from django import forms
from treenipaivakirja.models import harjoitus,tehot,laji,tehoalue
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm, UserCreationForm



class HarjoitusForm(forms.ModelForm):

    kesto_h = forms.IntegerField(label='h',min_value=0,required=False,widget=forms.NumberInput({'placeholder': 'h'}))
    kesto_min = forms.IntegerField(label='min',min_value=0,max_value=59,required=False,widget=forms.NumberInput({'placeholder': 'min'}))

    vauhti_min = forms.IntegerField(label='min',min_value=0,required=False,widget=forms.NumberInput({'placeholder': 'min'}))
    vauhti_s = forms.IntegerField(label='s',min_value=0,max_value=59,required=False,widget=forms.NumberInput({'placeholder': 's'}))

    class Meta:
        model = harjoitus
        widgets = {
            'vuorokaudenaika': forms.RadioSelect,
            'kommentti': forms.Textarea(attrs={'rows': 3}),
        }
        fields = [
            'pvm',
            'vuorokaudenaika',
            'laji_fk',
            'kesto_h',
            'kesto_min',
            'keskisyke',
            'matka',
            'vauhti_min',
            'vauhti_s',
            'vauhti_km_h',
            'vauhti_min_km',
            'nousu',
            'kalorit',
            'tuntuma',
            'kommentti'
            ]
    
    # filter laji choises dynamically according to current user
    # https://simpleisbetterthancomplex.com/questions/2017/03/22/how-to-dynamically-filter-modelchoices-queryset-in-a-modelform.html
    def __init__(self, user, *args, **kwargs):
        super(HarjoitusForm, self).__init__(*args, **kwargs)
        self.fields['laji_fk'].queryset = laji.objects.filter(user=user)


class LajiForm(forms.ModelForm):
    class Meta:
        model = laji
        fields = [
            'laji',
            'laji_nimi',
            'laji_ryhma'
            ]


class TehotForm(forms.ModelForm):

    nro = forms.IntegerField(min_value=0)
    kesto_h = forms.IntegerField(label='Kesto (h)',min_value=0,required=False,widget=forms.NumberInput({'placeholder': 'h'}))
    kesto_min = forms.IntegerField(label='Kesto (min)',min_value=0,max_value=59,required=False,widget=forms.NumberInput({'placeholder': 'min'}))
    vauhti_min = forms.IntegerField(label='Vauhti (min)',min_value=0,required=False,widget=forms.NumberInput({'placeholder': 'min'}))
    vauhti_s = forms.IntegerField(label='Vauhti (s)',min_value=0,max_value=59,required=False,widget=forms.NumberInput({'placeholder': 's'}))

    class Meta:
        model = tehot
        fields = [
            'nro',
            'teho',
            'kesto_h',
            'kesto_min',
            'kesto',
            'keskisyke',
            'maksimisyke',
            'matka',
            'vauhti_min',
            'vauhti_s',
            'vauhti_min_km',
            'vauhti_km_h'
            ]


class TehoalueForm(forms.ModelForm):
    class Meta:
        model = tehoalue
        fields = [
            'jarj_nro',
            'teho',
            'alaraja',
            'ylaraja'
            ]


class UserForm(UserChangeForm):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name', 
            'email', 
            'password'
            ]


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=False, label='Etunimi')
    last_name = forms.CharField(required=False, label='Sukunimi')
    email = forms.EmailField(required=False, label='Sähköposti')

    class Meta:
        model = User
        fields = [
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'password1', 
            'password2'
        ]