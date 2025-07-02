const OUTPUT_OPTIONS = {
    'en': [
        ['tai-han-tc-0', '台文(全漢)'],
        ['tai-han-tc-1', '台文(漢羅)'],
        ['tai-lmj-tc-tailo', '台文(台羅)'],
        ['tai-lmj-tc-poj', '台文(白話字)'],
        ['tai-lmj-tc-tw', '台文(台灣字)'],
    ],
    'ja': [
        ['tai-han-tc-0', '台文(全漢)'],
        ['tai-han-tc-1', '台文(漢羅)'],
        ['tai-lmj-tc-tailo', '台文(台羅)'],
        ['tai-lmj-tc-poj', '台文(白話字)'],
        ['tai-lmj-tc-tw', '台文(台灣字)'],
    ],
    'ko': [
        ['tai-han-tc-0', '台文(全漢)'],
        ['tai-han-tc-1', '台文(漢羅)'],
        ['tai-lmj-tc-tailo', '台文(台羅)'],
        ['tai-lmj-tc-poj', '台文(白話字)'],
        ['tai-lmj-tc-tw', '台文(台灣字)'],
    ],
    'zh-tw': [
        ['tai-han-tc-0', '台文(全漢)'],
        ['tai-han-tc-1', '台文(漢羅)'],
        ['tai-lmj-tc-tailo', '台文(台羅)'],
        ['tai-lmj-tc-poj', '台文(白話字)'],
        ['tai-lmj-tc-tw', '台文(台灣字)'],
    ],
    'zh-cn': [
        ['tai-han-tc-0', '台文(全漢)'],
        ['tai-han-tc-1', '台文(漢羅)'],
        ['tai-lmj-tc-tailo', '台文(台羅)'],
        ['tai-lmj-tc-poj', '台文(白話字)'],
        ['tai-lmj-tc-tw', '台文(台灣字)'],
    ],
    'tai-han-tc-0': [
        ['en', '英文'], ['ja', '日文'], ['ko', '韓文'], 
        ['zh-tw', '中文(正體)'], ['zh-cn', '中文(簡體)'], 
        ['tai-han-tc-1', '台文(漢羅)'], 
        ['tai-lmj-tc-tailo', '台文(台羅)'], 
        ['tai-lmj-tc-poj', '台文(白話字)'], 
        ['tai-lmj-tc-tw', '台文(台灣字)']
    ],
    'tai-han-tc-1': [
        ['en', '英文'], ['ja', '日文'], ['ko', '韓文'], 
        ['zh-tw', '中文(正體)'], ['zh-cn', '中文(簡體)'], 
        ['tai-han-tc-0', '台文(全漢)'], 
        ['tai-lmj-tc-tailo', '台文(台羅)'], 
        ['tai-lmj-tc-poj', '台文(白話字)'], 
        ['tai-lmj-tc-tw', '台文(台灣字)']
    ],
    'tai-lmj-tc-tailo': [
        ['en', '英文'], ['ja', '日文'], ['ko', '韓文'], 
        ['zh-tw', '中文(正體)'], ['zh-cn', '中文(簡體)'], 
        ['tai-han-tc-0', '台文(全漢)'], 
        ['tai-han-tc-1', '台文(漢羅)'], 
        ['tai-lmj-tc-poj', '台文(白話字)'], 
        ['tai-lmj-tc-tw', '台文(台灣字)']
    ],
    'tai-lmj-tc-poj': [
        ['en', '英文'], ['ja', '日文'], ['ko', '韓文'], 
        ['zh-tw', '中文(正體)'], ['zh-cn', '中文(簡體)'], 
        ['tai-han-tc-0', '台文(全漢)'], 
        ['tai-han-tc-1', '台文(漢羅)'], 
        ['tai-lmj-tc-tailo', '台文(台羅)'], 
        ['tai-lmj-tc-tw', '台文(台灣字)']
    ],
    'tai-lmj-tc-tw': [
        ['en', '英文'], ['ja', '日文'], ['ko', '韓文'], 
        ['zh-tw', '中文(正體)'], ['zh-cn', '中文(簡體)'], 
        ['tai-han-tc-0', '台文(全漢)'], 
        ['tai-han-tc-1', '台文(漢羅)'], 
        ['tai-lmj-tc-tailo', '台文(台羅)'], 
        ['tai-lmj-tc-poj', '台文(白話字)']
    ],
    'classical': [['tai-lmj-tailo', '台語漢字音(台羅)']]
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

function updateOutputOptions() {
    const inputLangSelect = document.getElementById('inputLangSelect');
    const outputFormatSelect = document.getElementById('outputFormatSelect');
    
    if (!inputLangSelect || !outputFormatSelect) {
        return;
    }
    
    const selectedLang = inputLangSelect.value;
    const options = OUTPUT_OPTIONS[selectedLang] || [];
    
    updateSelectOptions(outputFormatSelect, options);
}

function getAPIParams(inputLang, outputFormat, inputText) {
    const params = {
        mode: 'text',
        inp: inputText
    };
    
    function parseTaiFormat(formatStr) {
        if (formatStr.startsWith('tai-han-tc-')) {
            const outmod = formatStr.split('-').pop();
            return [1, 0, parseInt(outmod)]; // hanjimod=1(正體), lmjmod=0(台羅), outmod=0/1
        } else if (formatStr.startsWith('tai-lmj-tc-')) {
            const lmjType = formatStr.split('-').pop();
            const lmjmod = {'tailo': 0, 'poj': 1, 'tw': 2}[lmjType] || 0;
            return [1, lmjmod, 2]; // hanjimod=1(正體), lmjmod=0/1/2, outmod=2(全羅)
        } else {
            return [1, 0, 0];
        }
    }
    
    if (['en', 'ja', 'ko'].includes(inputLang)) {
        params.cmd = 'G2T';
        params.lang = inputLang;
        const [hanjimod, lmjmod, outmod] = parseTaiFormat(outputFormat);
        params.hanjimod = hanjimod;
        params.outmod = outmod;
    } else if (['zh-tw', 'zh-cn'].includes(inputLang)) {
        params.cmd = 'H2T';
        const [hanjimod, lmjmod, outmod] = parseTaiFormat(outputFormat);
        params.hanjimod = hanjimod;
        params.outmod = outmod;
    } else if (inputLang.startsWith('tai-')) {
        if (['en', 'ja', 'ko'].includes(outputFormat)) {
            params.cmd = 'T2G';
            params.lang = outputFormat;
        } else if (['zh-tw', 'zh-cn'].includes(outputFormat)) {
            params.cmd = 'T2H';
            params.hanjimod = outputFormat === 'zh-tw' ? 1 : 2;
        } else if (outputFormat.startsWith('tai-')) {
            // 台文轉台文
            params.cmd = 'T2T';
            const [hanjimod, lmjmod, outmod] = parseTaiFormat(outputFormat);
            params.hanjimod = hanjimod;
            params.outmod = outmod;
        }
    } else if (inputLang === 'classical') {
        params.cmd = 'B2L';
    }
    
    return params;
}

window.updateOutputOptions = updateOutputOptions;
window.getAPIParams = getAPIParams;

document.addEventListener('DOMContentLoaded', function() {
    updateOutputOptions();
    
    const inputLangSelect = document.getElementById('inputLangSelect');
    if (inputLangSelect) {
        inputLangSelect.addEventListener('change', updateOutputOptions);
    }
});
