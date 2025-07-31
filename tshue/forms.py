from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import WikiData


class TranslationAPIHelper:
    
    OUTPUT_OPTIONS = {
        'en': [
            ('tai-han', '漢羅'),
            ('tai-lmj', '全羅'),
            ('ja', '日文'), 
            ('ko', '韓文'), 
            ('tai', '台文'), 
            ('zh-tw', '中文(正體)'), 
            ('zh-cn', '中文(簡體)'), 
        ],
        'ja': [
            ('tai-han', '漢羅'),
            ('tai-lmj', '全羅'),
        ],
        'ko': [
            ('tai-han', '漢羅'),
            ('tai-lmj', '全羅'),
        ],
        'zh-tw': [
            ('tai-han', '漢羅'),
            ('tai-lmj', '全羅'),
        ],
        'zh-cn': [
            ('tai-han', '漢羅'),
            ('tai-lmj', '全羅'),
        ],
        'tai': [
            ('en', '英文'), 
            ('ja', '日文'), 
            ('ko', '韓文'), 
            ('tai-han', '漢羅'),
            ('tai-lmj', '全羅'),
            ('zh-tw', '中文(正體)'), 
            ('zh-cn', '中文(簡體)'), 
        ],
        'classical': [('tai-lmj-tailo', '台語漢字音(台羅)')],
    }
    
    @staticmethod
    def get_api_params(input_lang, output_format, input_text, lmj='tailo'):
        params = {
            'mode': 'text',
            'inp': input_text,
        }
        
        def parse_tai_format(format_str, rom_type='tailo'):
            lmjmod = {'tailo': 0, 'poj': 1, 'toj': 2}.get(rom_type, 0)
            if format_str.startswith('tai-han-tc-'):
                outmod = format_str.split('-')[-1]
                return 1, lmjmod, int(outmod)  # hanjimod=1(正體), lmjmod=用戶選擇, outmod=0/1
            elif format_str.startswith('tai-lmj-tc-'):
                return 1, lmjmod, 2  # hanjimod=1(正體), lmjmod=用戶選擇, outmod=2(全羅)
            else:
                return 1, lmjmod, 0
        
        if input_lang in ['en', 'ja', 'ko']:
            params['cmd'] = 'G2T'
            params['lang'] = input_lang
            hanjimod, lmjmod, outmod = parse_tai_format(output_format, lmj)
            params['hanjimod'] = hanjimod
            params['lmjmod'] = lmjmod
            params['outmod'] = outmod
                
        elif input_lang in ['zh-tw', 'zh-cn']:
            params['cmd'] = 'H2T'
            hanjimod, lmjmod, outmod = parse_tai_format(output_format, lmj)
            params['hanjimod'] = hanjimod
            params['lmjmod'] = lmjmod
            params['outmod'] = outmod
                
        elif input_lang == 'tai':
            if output_format in ['en', 'ja', 'ko']:
                params['cmd'] = 'T2G'
                params['lang'] = output_format
            elif output_format in ['zh-tw', 'zh-cn']:
                params['cmd'] = 'T2H'
                params['hanjimod'] = 1 if output_format == 'zh-tw' else 2
            elif output_format.startswith('tai-'):
                params['cmd'] = 'T2T'
                hanjimod, lmjmod, outmod = parse_tai_format(output_format, lmj)
                params['hanjimod'] = hanjimod
                params['lmjmod'] = lmjmod
                params['outmod'] = outmod
                
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
        label="請佇遮輸入文字！",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "請佇遮輸入文字！",
            "id": "floatingTextarea",
            "rows": "5",
            "maxlength": "500",
            "style": "height: 150px; resize: none;",
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
            ('tai', '台文'),
            ('classical', '文言文'),
        ], 
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['input_lang'].initial = 'zh-tw'

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

class LmjModForm(forms.Form):
    lmj = forms.ChoiceField(
        label="羅馬字",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'lmjSelect',
            'aria-label': '羅馬字',
            }),
        choices=[
            ('tailo', '台羅'),
            ('poj', '白話字'),
            ('toj', '台灣字'),
        ], 
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['lmj'].initial = 'tailo'

class SearchTermForm(forms.Form):
    key = forms.CharField()

class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='揀一个檔案',
    )

class SearchImikForm(forms.Form):
    key = forms.CharField()

