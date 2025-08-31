function setCookie(name, value, days = 30) {
//    const expires = new Date();
//    expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
//    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
}

function getCookie(name) {
//    const nameEQ = name + "=";
//    const ca = document.cookie.split(';');
//    for (let i = 0; i < ca.length; i++) {
//        let c = ca[i];
//        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
//        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
//    }
    return null;
}

const OUTPUT_OPTIONS = {
    'en': [
        ['tai-han', '台文(全漢)'],
        ['tai-hanlo', '台文(漢羅)'],
        ['tai-lmj', '台文(全羅)'],
    ],
    'ja': [
        ['tai-han', '台文(全漢)'],
        ['tai-hanlo', '台文(漢羅)'],
        ['tai-lmj', '台文(全羅)'],
    ],
    'ko': [
        ['tai-han', '台文(全漢)'],
        ['tai-hanlo', '台文(漢羅)'],
        ['tai-lmj', '台文(全羅)'],
    ],
    'zh-tw': [
        ['tai-han', '台文(全漢)'],
        ['tai-hanlo', '台文(漢羅)'],
        ['tai-lmj', '台文(全羅)'],
    ],
    'zh-cn': [
        ['tai-han', '台文(全漢)'],
        ['tai-hanlo', '台文(漢羅)'],
        ['tai-lmj', '台文(全羅)'],
    ],
    'tai': [
        ['en', '英文'],
        ['ja', '日文'],
        ['ko', '韓文'],
        ['zh-tw', '中文(正體)'],
        ['zh-cn', '中文(簡體)'],
        ['tai-han', '台文(全漢)'],
        ['tai-hanlo', '台文(漢羅)'],
        ['tai-lmj', '台文(全羅)'],
    ],
    'classical': [['tai-lmj', '台語漢字音']]
};

function updateSelectOptions(selectElement, options, cookieName = null, defaultValue = null) {
    selectElement.innerHTML = '';
    options.forEach(([value, text]) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = text;
        selectElement.appendChild(option);
    });
    
    if (options.length > 0) {
        if (cookieName) {
            const savedValue = getCookie(cookieName);
            if (savedValue && options.some(([value]) => value === savedValue)) {
                selectElement.value = savedValue;
                return;
            }
        }
        if (defaultValue && options.some(([value]) => value === defaultValue)) {
            selectElement.value = defaultValue;
        } else {
            selectElement.value = options[0][0];
        }
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
    
    updateSelectOptions(outputFormatSelect, options, 'outputFormat', 'tai-han');
    setCookie('inputLang', selectedLang);
   if (options.length > 0) {
       setCookie('outputFormat', options[0][0]);
   }
}

// Function to get user's real IP address
async function getUserIP() {
    try {
        // Try multiple IP detection services for reliability
        const services = [
            'https://api.ipify.org?format=json',
            'https://ipapi.co/json/',
            'https://api.myip.com',
            'https://httpbin.org/ip'
        ];
        
        for (const service of services) {
            try {
                const response = await fetch(service, {
                    method: 'GET',
                    timeout: 5000
                });
                
                if (response.ok) {
                    const data = await response.json();
                    // Different services return IP in different formats
                    const ip = data.ip || data.query || data.origin;
                    if (ip && ip !== '127.0.0.1' && ip !== 'localhost') {
                        console.log(`IP detected from ${service}: ${ip}`);
                        return ip;
                    }
                }
            } catch (error) {
                console.warn(`Failed to get IP from ${service}:`, error);
                continue;
            }
        }
        
        // Fallback: try to get IP from WebRTC (local network IP)
        try {
            const rtc = new RTCPeerConnection({iceServers: []});
            rtc.createDataChannel('');
            rtc.createOffer().then(offer => rtc.setLocalDescription(offer));
            
            rtc.onicecandidate = (event) => {
                if (event.candidate) {
                    const ipMatch = event.candidate.candidate.match(/([0-9]{1,3}(\.[0-9]{1,3}){3})/);
                    if (ipMatch && ipMatch[1] !== '127.0.0.1') {
                        console.log(`IP detected from WebRTC: ${ipMatch[1]}`);
                        return ipMatch[1];
                    }
                }
            };
        } catch (error) {
            console.warn('WebRTC IP detection failed:', error);
        }
        
        console.warn('Could not detect user IP, using fallback');
        return '127.0.0.1'; // Fallback
    } catch (error) {
        console.error('Error getting user IP:', error);
        return '127.0.0.1'; // Fallback
    }
}

async function getAPIParams(inputLang, outputFormat, inputText, lmj = 'tailo') {
    const params = {
        mode: 'text',
        inp: inputText
    };
    
    // Get user's real IP address
    const userIP = await getUserIP();
    params.ip = userIP;
    
    function parseTaiFormat(formatStr, romType = 'tailo') {
        const lmjmod = {'tailo': 0, 'poj': 1, 'toj': 2}[romType] || 0;
        
        if (formatStr.startsWith('tai-hanlo')) {
            return [1, lmjmod, 1]; // hanjimod=1(正體), lmjmod=用戶選擇, outmod=0/1
        } else if (formatStr.startsWith('tai-lmj')) {
            return [1, lmjmod, 2]; // hanjimod=1(正體), lmjmod=0/1/2, outmod=2(全羅)
        } else { // tai-han
            return [1, lmjmod, 0];
        }
    }
    
    if (['en', 'ja', 'ko'].includes(inputLang)) {
        params.cmd = 'G2T';
        params.lang = inputLang;
        const [hanjimod, lmjmod, outmod] = parseTaiFormat(outputFormat, lmj);
        params.hanjimod = hanjimod;
        params.lmjmod = lmjmod;
        params.outmod = outmod;
    } else if (['zh-tw', 'zh-cn'].includes(inputLang)) {
        params.cmd = 'H2T';
        const [hanjimod, lmjmod, outmod] = parseTaiFormat(outputFormat, lmj);
        params.hanjimod = hanjimod;
        params.lmjmod = lmjmod;
        params.outmod = outmod;
    } else if (inputLang === 'tai') {
        if (['en', 'ja', 'ko'].includes(outputFormat)) {
            params.cmd = 'T2G';
            params.lang = outputFormat;
        } else if (['zh-tw', 'zh-cn'].includes(outputFormat)) {
            params.cmd = 'T2H';
            params.hanjimod = outputFormat === 'zh-tw' ? 1 : 2;
        } else if (outputFormat.startsWith('tai-')) {
            params.cmd = 'T2T';
            const [hanjimod, lmjmod, outmod] = parseTaiFormat(outputFormat, lmj);
            params.hanjimod = hanjimod;
            params.lmjmod = lmjmod;
            params.outmod = outmod;
        }
    } else if (inputLang === 'classical') {
        params.cmd = 'B2L';
        const [hanjimod, lmjmod, outmod] = parseTaiFormat(outputFormat, lmj);
        params.lmjmod = lmjmod;
    }
    
    return params;
}

window.updateOutputOptions = updateOutputOptions;
window.getAPIParams = getAPIParams;

document.addEventListener('DOMContentLoaded', function() {
    const savedInputLang = getCookie('inputLang');
    const inputLangSelect = document.getElementById('inputLangSelect');
    
    if (inputLangSelect) {
        if (savedInputLang && Object.keys(OUTPUT_OPTIONS).includes(savedInputLang)) {
            inputLangSelect.value = savedInputLang;
        } else {
            inputLangSelect.value = 'zh-tw';
        }
    }
    
    updateOutputOptions();
    
    if (inputLangSelect) {
        inputLangSelect.addEventListener('change', updateOutputOptions);
    }
    
    const outputFormatSelect = document.getElementById('outputFormatSelect');
    if (outputFormatSelect) {
        outputFormatSelect.addEventListener('change', function() {
            setCookie('outputFormat', this.value);
        });
    }
    
    const lmjSelect = document.getElementById('lmjSelect');
    if (lmjSelect) {
        const savedLmj = getCookie('lmjType');
        if (savedLmj) {
            lmjSelect.value = savedLmj;
        } else {
            lmjSelect.value = 'tailo';
        }
        
        lmjSelect.addEventListener('change', function() {
            setCookie('lmjType', this.value);
        });
    }
});
