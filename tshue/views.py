import datetime as dt
import json
import os
import socket

import requests
from django.http import (FileResponse, HttpResponse, HttpResponseRedirect,
                         JsonResponse, StreamingHttpResponse)
from django.shortcuts import render
from django.template import RequestContext
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import (InputModForm, LmjModForm, OutputModForm, SearchForm,
                    SearchImikForm, SearchTermForm, TranslationAPIHelper,
                    UploadFileForm)
from .models import WikiData


@csrf_exempt
@require_http_methods(["POST"])
def translation_proxy(request):
    """
    Proxy endpoint for translation API to handle CORS issues
    """
    try:
        # Get form data from request
        input_lang = request.POST.get('input_lang')
        output_format = request.POST.get('output_format') 
        input_text = request.POST.get('key')  # Frontend sends 'key' parameter
        lmj = request.POST.get('lmj', 'tailo')  # Default to tailo
        user_ip = request.POST.get('ip')  # Get IP from frontend

        if not all([input_lang, output_format, input_text]):
            missing = []
            if not input_lang: missing.append('input_lang')
            if not output_format: missing.append('output_format')
            if not input_text: missing.append('input_text')
            
            error_msg = f'Missing required parameters: {", ".join(missing)}'
            
            return JsonResponse({
                'success': False,
                'error': error_msg
            }, status=400)
        
        # Generate API parameters using helper
        api_params = TranslationAPIHelper.get_api_params(input_lang, output_format, input_text, lmj)
        
        # Use IP from frontend if provided, otherwise fallback to server detection
        if user_ip and user_ip != '127.0.0.1':
            api_params['ip'] = user_ip
            print(f"DEBUG: Using frontend IP: {user_ip}")
        else:
            # Fallback to server IP detection
            client_ip = getClientIP(request)
            api_params['ip'] = client_ip
            print(f"DEBUG: Using server-detected IP: {client_ip}")
        
        print(f"DEBUG: Generated API parameters: {api_params}")
        
        # Make request to translation API
        api_url = 'http://lohankha.tw:10999'
        response = requests.post(
            api_url,
            data=api_params,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )

        if response.status_code == 200:
            # Parse the API response
            try:
                result_data = response.json()
                
                return JsonResponse({
                    'success': True,
                    'result': result_data
                })
            except json.JSONDecodeError:
                error_msg = 'Invalid JSON response from translation API'
                
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=500)
        else:
            error_msg = f'API request failed with status {response.status_code}'
            
            return JsonResponse({
                'success': False,
                'error': error_msg,
                'details': response.text[:200]
            }, status=response.status_code)
            
    except requests.RequestException as e:
        error_msg = f'Network error: {str(e)}'
        print(f"DEBUG: Network error: {str(e)}")
        
        return JsonResponse({
            'success': False,
            'error': error_msg
        }, status=500)
    except Exception as e:
        error_msg = f'Server error: {str(e)}'
        print(f"DEBUG: Server error: {str(e)}")
        
        return JsonResponse({
            'success': False,
            'error': error_msg
        }, status=500)

def getClientIP(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
       ip = x_forwarded_for.split(',')[0]
    else:
       ip = request.META.get('REMOTE_ADDR')
    return ip

def index(request):
    form = SearchForm(request.POST or None)
    if form.is_valid():
        key = form.cleaned_data['key']
    else:
        key = ''

    input_form = InputModForm(request.POST or None)
    if input_form.is_valid():
        input_lang = input_form.cleaned_data['input_lang']
    else:
        input_lang = 'zh-tw' # defult

    output_form = OutputModForm(input_lang=input_lang, data=request.POST or None)
    if output_form.is_valid():
        output_format = output_form.cleaned_data['output_format']
    else:
        # default output format based on input language
        output_options = TranslationAPIHelper.get_output_options(input_lang)
        output_format = output_options[0][0] if output_options else 'tai-han'

    lmj_form = LmjModForm(request.POST or None)
    if lmj_form.is_valid():
        lmj = lmj_form.cleaned_data['lmj']
    else:
        lmj = 'tailo' # default

    lines = []
    api_params = {}
    client_ip = getClientIP(request)
    
    if key and input_lang and output_format:
        # generate API parameters based on input language and output format
        api_params = TranslationAPIHelper.get_api_params(input_lang, output_format, key, lmj)
        
        try:
            # TODO: use new API parameters format
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("localhost", 9999))
            # SETIP
            isStart = False
            isSent = False
            output = b""
            buf = ''
            while True:
                if not isStart:
                    response = sock.recv(1024).decode()
                    if response == "$ ":
                        isStart = True
                    continue
                else:
                    if not isSent:
                        string = "SETIP %s" % client_ip
                        sock.sendall(string.encode())
                        isSent = True
                    else:
                        response = sock.recv(1024)
                        output += response
                        try:
                            if "DONE" in response.decode():
                                break
                        except:
                            pass
            for line in output.decode().split('\n'):
                if line.startswith('DONE'):
                    buf = line[4:]
                    break

            # TRANSLATE
            isStart = False
            isSent = False
            output = b""
            while True:
                if not isStart:
                    if buf == '$ ':
                        buf = ''
                        isStart = True
                    else:
                        response = sock.recv(1024).decode()
                        if response == "$ ":
                            isStart = True
                    continue
                else:
                    if not isSent:
                        # TODO: use new API parameters format
                        cmd = api_params.get('cmd', 'H2T')
                        lang = api_params.get('lang', '')
                        hanjimod = api_params.get('hanjimod', 1)
                        lmjmod_param = api_params.get('lmjmod', 0)
                        outmod = api_params.get('outmod', 1)
                        
                        # old format handling
                        if cmd == 'H2T':
                            hanmod = '1' if input_lang == 'zh-tw' else '0'
                        elif cmd == 'G2T':
                            hanmod = lang
                        else:
                            hanmod = '0'
                        
                        lmjmod = str(lmjmod_param)
                        
                        string = "TRANSLATE%s%s0 %s" % (hanmod, lmjmod, key.replace('\r\n', '\n'))
                        sock.sendall(string.encode())
                        isSent = True
                    else:
                        response = sock.recv(1024)
                        output += response
                        try:
                            if "DONE" in response.decode():
                                break
                        except:
                            pass
            for line in output.decode().split('\n'):
                if line.startswith('DONE'):
                    break
                lines.append(line)
            sock.close()
            
            output_text = '\n'.join(lines)
            
        except Exception as e:
            error_msg = f"Translation error: {str(e)}"
            print(f"Translation error: {e}")

    context = {
        'trans': {'lines': lines},
        'form': form,
        'input_form': input_form,
        'output_form': output_form,
        'lmj_form': lmj_form,
        'api_params': api_params, # debug
        'input_lang': input_lang,
        'output_format': output_format,
        'lmj': lmj,
    }
    return render(request, 'index.html', context)

def terms(request):
    form = SearchTermForm(request.POST or None)
    if form.is_valid():
        key = form.cleaned_data['key']
        form = SearchTermForm()
    else:
        key = ''

    if key:
        wd = WikiData.objects.filter(en__contains=key)[:20]
    else:
        wd = []

    context = {
        'wd': wd,
        'form': form
    }
    return render(request, 'terms.html', context)

def imik(request):
    form = SearchImikForm(request.POST or None)
    if form.is_valid():
        key = form.cleaned_data['key']
        form = SearchImikForm()
    else:
        key = ''

    lines = []
    if key:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 10999))
        isStart = False
        isSent = False
        output = b""
        while True:
            if not isStart:
                response = sock.recv(1024).decode()
                if response == "$ ":
                    isStart = True
                continue
            else:
                if not isSent:
                    string = "TRANSLATE %s" % (key.replace('\r\n', '\n'))
                    sock.sendall(string.encode())
                    isSent = True
                else:
                    response = sock.recv(1024)
                    output += response
                    try:
                        if "DONE" in response.decode():
                            break
                    except:
                        pass
        for line in output.decode().split('\n'):
            if line.startswith('DONE'):
                break
            lines.append(line)
        sock.close()

    context = {
        'trans': {'lines': lines},
        'form': form,
    }
    return render(request, 'imik.html', context)

def isTimestamp(line):
    if "-->" not in line:
        return False
    if [c for c in line if c not in "0123456789:, -->"]:
        return False
    return True

def isSRT(filename):
    f = open(filename, encoding='utf8')
    isUtf8 = True
    try:
        f.read(2)
    except:
        isUtf8 = False
    f.close()

    if isUtf8:
        f = open(filename, encoding='utf8')
    else:
        f = open(filename, encoding='utf16')

    offset = 0
    buf2 = None
    buf = ''
    ret = True
    for i, line in enumerate(f):
        line = line.rstrip()
        if i == 0:
            pass
        elif i - offset > 25:    # limitation of single subtitle
            ret = False
            break
        elif len(line) > 100:    # limitation of single line
            ret = False
            break
        elif isTimestamp(line) and buf2 == '' and not [c for c in buf if c not in "0123456789"]:    # a new timestamp
            offset = i
        else:    # normal line
            pass

        buf2 = buf
        buf = line
    f.close()

    return ret

def getRenderedHTTP(uid, api_params, filename, ip):
    """
    Process SRT file using HTTP API - upload entire file instead of line-by-line
    """
    print(f"DEBUG: Starting subtitle translation for file: {filename}")
    print(f"DEBUG: API parameters: {api_params}")
    print(f"DEBUG: Client IP: {ip}")
    
    fn = "/tmp/%s" % uid
    api_url = 'http://lohankha.tw:10999'
    print(f"DEBUG: Using API URL: {api_url}")
    
    try:
        # Upload the entire SRT file to the API
        with open(fn, 'rb') as f:
            files = {'file': (filename, f, 'text/plain')}
            
            # Remove 'inp' from api_params since we're uploading a file
            upload_params = api_params.copy()
            if 'inp' in upload_params:
                del upload_params['inp']
            
            print(f"DEBUG: Making HTTP request with params: {upload_params}")
            print(f"DEBUG: Uploading file: {filename}")
            
            response = requests.post(
                api_url,
                data=upload_params,
                files=files,
                timeout=120  # Longer timeout for file upload
            )
            
            print(f"DEBUG: HTTP response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result_data = response.json()
                    print(f"DEBUG: API response data: {result_data}")
                    
                    # Check if API returned an error
                    if result_data.get('status') == 'error':
                        error_msg = result_data.get('message', 'Unknown error')
                        print(f"DEBUG: API returned error: {error_msg}")
                        raise Exception(f"Translation API error: {error_msg}")
                    
                    # Get translated content
                    translated_content = result_data.get('ret', '')
                    if not translated_content:
                        raise Exception("No translated content returned from API")
                    
                    print(f"DEBUG: Translation successful, content length: {len(translated_content)}")
                    
                    # Yield the translated content
                    for line in translated_content.splitlines():
                        yield line.encode() + b'\r\n'
                        
                except json.JSONDecodeError as e:
                    print(f"DEBUG: JSON decode error: {e}")
                    print(f"DEBUG: Raw response: {response.text[:500]}")
                    raise Exception("Invalid JSON response from translation API")
            else:
                print(f"DEBUG: API request failed with status {response.status_code}")
                print(f"DEBUG: Error response: {response.text[:500]}")
                raise Exception(f"API request failed with status {response.status_code}")
                
    except Exception as e:
        print(f"DEBUG: Translation error: {e}")
        # If translation fails, return original file content
        print("DEBUG: Returning original file content due to error")
        try:
            # Try UTF-8 first
            with open(fn, 'r', encoding='utf8') as f:
                for line in f:
                    yield line.encode()
        except UnicodeDecodeError:
            # If UTF-8 fails, try UTF-16
            try:
                with open(fn, 'r', encoding='utf16') as f:
                    for line in f:
                        yield line.encode()
            except UnicodeDecodeError:
                # If UTF-16 also fails, try other encodings
                for encoding in ['gbk', 'big5', 'latin1']:
                    try:
                        with open(fn, 'r', encoding=encoding) as f:
                            for line in f:
                                yield line.encode()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    # If all encodings fail, return error message
                    yield f"Error: Unable to read file with any supported encoding".encode()
    
    print(f"DEBUG: Subtitle translation completed.")

def getRendered(uid, sock, hanmod, lmjmod, outmod, filename, ip):
    fn = "/tmp/%s" % uid
    fn2 = "/tmp/%s.out" % uid
    f = open(fn, encoding='utf8')
    isUtf8 = True
    try:
        f.read(2)
    except:
        isUtf8 = False
    f.close()

    if isUtf8:
        f = open(fn, encoding='utf8')
    else:
        f = open(fn, encoding='utf16')
    ff = open(fn2, "w", encoding='utf8')

    tic = dt.datetime.now()
    buf = ''
    for line in f:
        line = line.replace('\r\n', '\n').rstrip()
        if not [c for c in line if c not in "0123456789 ->,:"]:
            print(line, file=ff)
            yield line.encode() + b'\r\n'
            continue

        isStart = False
        isSent = False
        output = b""
        while True:
            if not isStart:
                if buf == '$ ':
                    buf = ""
                    isStart = True
                else:
                    response = sock.recv(1024).decode()
                    if response == "$ ":
                        isStart = True
                continue
            else:
                if not isSent:
                    string = "TRANSRT%s%s%s %s" % (hanmod, lmjmod, outmod, line)
                    sock.sendall(string.encode())
                    isSent = True
                else:
                    response = sock.recv(1024)
                    output += response
                    try:
                        if "DONE" in response.decode():
                            break
                    except:
                        pass
        for li in output.decode().split('\n'):
            if li.startswith('DONE'):
                buf = li[4:]
                break
            print(li, file=ff)
            yield li.encode() + b'\r\n'
    ff.close()
    f.close()



    string = "QUIT"
    sock.sendall(string.encode())
    sock.close()

def subtitle(request):
    input_form = InputModForm(request.POST or None)
    if input_form.is_valid():
        input_lang = input_form.cleaned_data['input_lang']
    else:
        input_lang = 'zh-tw'

    output_form = OutputModForm(input_lang=input_lang, data=request.POST or None)
    if output_form.is_valid():
        output_format = output_form.cleaned_data['output_format']
    else:
        output_options = TranslationAPIHelper.get_output_options(input_lang)
        output_format = output_options[0][0] if output_options else 'tai-han'

    lmj_form = LmjModForm(request.POST or None)
    if lmj_form.is_valid():
        lmj = lmj_form.cleaned_data['lmj']
    else:
        lmj = 'tailo'  # default
        # Set initial value for the form
        lmj_form.fields['lmj'].initial = lmj

    outmodform = OutputModForm(input_lang=input_lang, data=request.POST or None)
    if outmodform.is_valid():
        outmod = outmodform.cleaned_data['output_format']
    else:
        outmod = '0'

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            import random
            import uuid
            uid = "%s" % uuid.uuid4()

            import socket
            import urllib.parse
            the_file = request.FILES["file"]
            with open("/tmp/%s" % uid, "wb+") as f:
                for chunk in the_file.chunks():
                    f.write(chunk)

            ip = getClientIP(request)
            try:
                ret = isSRT("/tmp/%s" % uid)
            except:
                ret = False
            if ret:
                # Use HTTP API instead of socket connection
                try:
                    # generate API parameters based on input language and output format
                    api_params = TranslationAPIHelper.get_api_params(input_lang, output_format, "dummy", lmj)
                    # Use srt mode for subtitle file translation
                    api_params['mode'] = 'srt'
                    api_params['ip'] = ip
                    
                    # Process SRT file using HTTP API
                    response = StreamingHttpResponse(getRenderedHTTP(uid, api_params, the_file.name, ip))
                    response['Content-Disposition'] = "attachment; filename*=UTF-8''%s" % urllib.parse.quote(the_file.name)
                    return response
                except Exception as e:
                    return HttpResponse(f'translation service error: {str(e)}')
            else:

                return HttpResponse('file format error!')
        return HttpResponse('error!')

    else:
        form = UploadFileForm()

    context = {
        'form': form,
        'input_form': input_form,
        'output_form': output_form,
        'lmj_form': lmj_form,
        'outmodform': outmodform,
    }
    return render(request, "subtitle.html", context)
