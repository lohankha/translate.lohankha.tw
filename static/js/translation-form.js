const OUTPUT_OPTIONS = {
    'en': [['tai-han', '台文(漢字)'], ['tai-lmj', '台文(羅馬字)']],
    'ja': [['tai-han', '台文(漢字)'], ['tai-lmj', '台文(羅馬字)']],
    'ko': [['tai-han', '台文(漢字)'], ['tai-lmj', '台文(羅馬字)']],
    'zh-tw': [['tai-han', '台文(漢字)'], ['tai-lmj', '台文(羅馬字)']],
    'zh-cn': [['tai-han', '台文(漢字)'], ['tai-lmj', '台文(羅馬字)']],
    'tai-han': [['en', '英文'], ['ja', '日文'], ['ko', '韓文'], ['zh-tw', '中文(正體)'], ['zh-cn', '中文(簡體)'], ['tai-lmj', '台文(羅馬字)']],
    'tai-lmj': [['en', '英文'], ['ja', '日文'], ['ko', '韓文'], ['zh-tw', '中文(正體)'], ['zh-cn', '中文(簡體)'], ['tai-han', '台文(漢字)']],
    'classical': [['tai-lmj', '台語漢字音']]
};

function updateSelectOptions(selectElement, options) {
    selectElement.innerHTML = '';
    options.forEach(([value, text]) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = text;
        selectElement.appendChild(option);
    });
    
    if (options.length > 0) {
        selectElement.value = options[0][0];
    }
}

function getAPIParams(inputLang, outputFormat, inputText) {
    const params = {
        mode: 'text',
        inp: inputText
    };
    
    if (['en', 'ja', 'ko'].includes(inputLang)) {
        params.cmd = 'G2T';
        params.lang = inputLang;
        if (outputFormat === 'tai-han') {
            params.hanjimod = 1;
            params.outmod = 1;
        } else { // tai-lmj
            params.outmod = 2;
        }
    } else if (['zh-tw', 'zh-cn'].includes(inputLang)) {
        params.cmd = 'H2T';
        if (outputFormat === 'tai-han') {
            params.hanjimod = 1;
            params.outmod = 1;
        } else { // tai-lmj
            params.outmod = 2;
        }
    } else if (inputLang === 'tai-han') {
        if (['en', 'ja', 'ko'].includes(outputFormat)) {
            params.cmd = 'T2G';
            params.lang = outputFormat;
        } else if (['zh-tw', 'zh-cn'].includes(outputFormat)) {
            params.cmd = 'T2H';
            params.hanjimod = outputFormat === 'zh-tw' ? 1 : 2;
        } else if (outputFormat === 'tai-lmj') {
            params.cmd = 'H2L';
        }
    } else if (inputLang === 'tai-lmj') {
        if (['en', 'ja', 'ko'].includes(outputFormat)) {
            params.cmd = 'T2G';
            params.lang = outputFormat;
        } else if (['zh-tw', 'zh-cn'].includes(outputFormat)) {
            params.cmd = 'T2H';
            params.hanjimod = outputFormat === 'zh-tw' ? 1 : 2;
        } else if (outputFormat === 'tai-han') {
            params.cmd = 'L2H';
            params.hanjimod = 1;
        }
    } else if (inputLang === 'classical') {
        params.cmd = 'B2L';
    }
    
    return params;
}

document.addEventListener('DOMContentLoaded', function() {
    updateOutputOptions();
    
    const inputLangSelect = document.getElementById('inputLangSelect');
    if (inputLangSelect) {
        inputLangSelect.addEventListener('change', updateOutputOptions);
    }
});
