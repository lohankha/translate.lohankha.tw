from django import forms

from .models import WikiData


class TranslationAPIHelper:
    
    OUTPUT_OPTIONS = {
        'en': [('tai-han', '台文(漢字)'), ('tai-lmj', '台文(羅馬字)')],
        'ja': [('tai-han', '台文(漢字)'), ('tai-lmj', '台文(羅馬字)')],
        'ko': [('tai-han', '台文(漢字)'), ('tai-lmj', '台文(羅馬字)')],
        'zh-tw': [('tai-han', '台文(漢字)'), ('tai-lmj', '台文(羅馬字)')],
        'zh-cn': [('tai-han', '台文(漢字)'), ('tai-lmj', '台文(羅馬字)')],
        'tai-han': [('en', '英文'), ('ja', '日文'), ('ko', '韓文'), ('zh-tw', '中文(正體)'), ('zh-cn', '中文(簡體)'), ('tai-lmj', '台文(羅馬字)')],
        'tai-lmj': [('en', '英文'), ('ja', '日文'), ('ko', '韓文'), ('zh-tw', '中文(正體)'), ('zh-cn', '中文(簡體)'), ('tai-han', '台文(漢字)')],
        'classical': [('tai-lmj', '台語漢字音')],
    }
    
    @staticmethod
    def get_api_params(input_lang, output_format, input_text):
        params = {
            'mode': 'text',
            'inp': input_text,
        }
        
        if input_lang in ['en', 'ja', 'ko']:
            params['cmd'] = 'G2T'
            params['lang'] = input_lang
            if output_format == 'tai-han':
                params['hanjimod'] = 1
                params['outmod'] = 1
            else:  # tai-lmj
                params['outmod'] = 2
                
        elif input_lang in ['zh-tw', 'zh-cn']:
            params['cmd'] = 'H2T'
            if output_format == 'tai-han':
                params['hanjimod'] = 1
                params['outmod'] = 1
            else:  # tai-lmj
                params['outmod'] = 2
                
        elif input_lang == 'tai-han':
            if output_format in ['en', 'ja', 'ko']:
                params['cmd'] = 'T2G'
                params['lang'] = output_format
            elif output_format in ['zh-tw', 'zh-cn']:
                params['cmd'] = 'T2H'
                params['hanjimod'] = 1 if output_format == 'zh-tw' else 2
            elif output_format == 'tai-lmj':
                params['cmd'] = 'H2L'
                
        elif input_lang == 'tai-lmj':
            if output_format in ['en', 'ja', 'ko']:
                params['cmd'] = 'T2G'
                params['lang'] = output_format
            elif output_format in ['zh-tw', 'zh-cn']:
                params['cmd'] = 'T2H'
                params['hanjimod'] = 1 if output_format == 'zh-tw' else 2
            elif output_format == 'tai-han':
                params['cmd'] = 'L2H'
                params['hanjimod'] = 1
                
        elif input_lang == 'classical':
            params['cmd'] = 'B2L'
            
        return params
    
    @staticmethod
    def get_output_options(input_lang):
        return TranslationAPIHelper.OUTPUT_OPTIONS.get(input_lang, [])

class WikiDataForm(forms.ModelForm):
    class Meta:
        model = WikiData
        fields = '__all__'

class SearchForm(forms.Form):
    key = forms.CharField(
        label="請佇遮輸入華語！(限500字元)",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "請佇遮輸入華語！(限500字元)",
            "id": "floatingTextarea",
            "rows": "5",
            "maxlength": "500",
            "style": "height: 150px;",
        })
    )

class InputModForm(forms.Form):
    input_lang = forms.ChoiceField(
        label="輸入",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'inputLangSelect',
            'aria-label': '輸入',
            'onchange': 'updateOutputOptions()',
            }),
        choices=[
            ('en', '英文'),
            ('ja', '日文'),
            ('ko', '韓文'),
            ('zh-tw', '中文(正體)'),
            ('zh-cn', '中文(簡體)'),
            ('tai-han', '台文(漢字)'),
            ('tai-lmj', '台文(羅馬字)'),
            ('classical', '文言文'),
        ], 
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['input_lang'].initial = 'zh-tw'  # 預設為中文(正體)

class OutputModForm(forms.Form):
    output_format = forms.ChoiceField(
        label="輸出",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'outputFormatSelect',
            'aria-label': '輸出',
            }),
        choices=[], 
    )

    def __init__(self, input_lang='zh-tw', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['output_format'].choices = TranslationAPIHelper.get_output_options(input_lang)
        if self.fields['output_format'].choices:
            self.fields['output_format'].initial = self.fields['output_format'].choices[0][0]
    
    def update_choices(self, input_lang):
        self.fields['output_format'].choices = TranslationAPIHelper.get_output_options(input_lang)
class SearchTermForm(forms.Form):
    key = forms.CharField()

class UploadFileForm(forms.Form):
    file = forms.FileField(
                label='揀一个檔案'
            )

class SearchImikForm(forms.Form):
    key = forms.CharField()

