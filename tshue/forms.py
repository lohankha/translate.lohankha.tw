from django import forms

from .models import WikiData

class WikiDataForm(forms.ModelForm):
    class Meta:
        model = WikiData
        fields = '__all__'

class SearchForm(forms.Form):
    key = forms.CharField(widget=forms.Textarea(attrs={"rows":"5", "maxlength":"500", "placeholder":"請佇遮輸入華語！(限500字元)"}))
    class Meta:
        labels = {
            'key': '',
        }

class HanModForm(forms.Form):
    CHOICES = [
        ('0', '全漢'),
        ('1', '漢羅'),
    ]
    hanmod = forms.ChoiceField(
        label="漢字選項",
        widget=forms.RadioSelect,
        choices=CHOICES, 
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hanmod'].initial = '0'

class LmjModForm(forms.Form):
    CHOICES = [
        ('0', '台羅'),
        ('1', '白話字(POJ)'),
        ('2', '無hyphen白話字(TOJ)'),
    ]
    lmjmod = forms.ChoiceField(
        label="羅馬字選項",
        widget=forms.RadioSelect,
        choices=CHOICES, 
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lmjmod'].initial = '0'

class OutModForm(forms.Form):
    CHOICES = [
        ('0', '漢字'),
        ('1', '羅馬字'),
    ]
    outmod = forms.ChoiceField(
        label="輸出",
        widget=forms.RadioSelect,
        choices=CHOICES, 
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['outmod'].initial = '0'

class SearchTermForm(forms.Form):
    key = forms.CharField()

class UploadFileForm(forms.Form):
    file = forms.FileField(
                label='揀一个檔案'
            )

class SearchImikForm(forms.Form):
    key = forms.CharField()

