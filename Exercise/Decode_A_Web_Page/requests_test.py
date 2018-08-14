import requests
import json
#json.dumps()  : python transfer to json
#json.loads()  : json transfer to python
#
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
from requests_oauthlib import OAuth1
from requests import Request, Session


def try_get():
    r = requests.get('https://api.github.com/user', auth=('user', 'pass'))
    print(r.text)
    print(r.status_code)
    r = requests.get('https://api.github.com/user')
    print(r.text)
    #    print(r.json)
    print(r.status_code)
    print(r.headers)
    r = requests.get('https://api.github.com/events')
    print(r.text)

def try_url():
    payload = {'key1': 'value1', 'key2': 'value2'}
    r = requests.get('http://httpbin.org/get', params=payload)
    print(r.url)
    payload = {'key1': 'value1', 'key2': ['value2', 'value3']}
    r = requests.get('http://httpbin.org/get', params=payload)
    print(r.url)

def try_practicepython():
    r = requests.get('http://www.practicepython.org/')
    print(r.url)
    print(r.text)
    print(r.status_code)

def save_raw_stream_as_a_file():
    r = requests.get('http://www.practicepython.org/', stream=True)
    with open('proacticepython.txt', 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
def save_cnn():
    url ='http://edition.cnn.com/2017/02/08/studentnews/ten-content-thurs/index.html'
    r = requests.get(url, stream=True)
    with open('cnn.txt', 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

def custom_headers():
    url = 'https://api.github.com/some/endpoint'
    headers = {'user-agent': 'my-app/0.0.1'}
    r = requests.get(url, headers=headers)
    print(r.headers)
    r = requests.get(url)
    print(r.text)
    print(r.headers)

def Send_form_encoded_data():
    payload = {'key1': 'value1', 'key2': 'value2'}
    r = requests.post("http://httpbin.org/post", data=payload)
    print(r.text)
    print("*"*100)
    r = requests.get("http://httpbin.org/post")
    print(r.text)

def post_multipart_files():
    url = 'http://httpbin.org/post'
    files = {'file': open('proacticepython.txt', 'rb')}
    r = requests.post(url, files=files)
    print(r.text)

def cookies():
    url = 'http://example.com/some/cookie/setting/url'
    r = requests.get(url)
#    print(r.text)
    print(r.cookies)

def send_cookie():
    url = 'http://httpbin.org/cookies'
    cookies = dict(cookies_are='working')

    r = requests.get(url, cookies=cookies)
    print(r.text)

def try_auth():
    r = requests.get('https://api.github.com/user', auth=HTTPBasicAuth('user', 'pass'))
    print(r.status_code)
# HTTPBasicAuth can be skip
    r = requests.get('https://api.github.com/user', auth=('user', 'pass'))
    print(r.status_code)

def try_digestAuth():
    url = 'http://httpbin.org/digest-auth/auth/user/pass'
    r = requests.get(url, auth=HTTPDigestAuth('user', 'pass'))
    print(r.status_code)

def try_oauth():
    # fail
    url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    auth = OAuth1('YOUR_APP_KEY', 'YOUR_APP_SECRET','USER_OAUTH_TOKEN', 'USER_OAUTH_TOKEN_SECRET')
    r = requests.get(url, auth=auth)
    print(r.status_code)

def try_session():
    s = requests.Session()
    s.get('http://httpbin.org/cookies/set/sessioncookie/123456789')
    r = s.get('http://httpbin.org/cookies')
    print(r.text)

def try_prepare():
    s = Session()

    req = Request('POST', url, data=data, headers=headers)
    prepped = req.prepare()

    # do something with prepped.body
    prepped.body = 'No, I want exactly this as the body.'

    # do something with prepped.headers
    del prepped.headers['Content-Type']

    resp = s.send(prepped,
                  stream=stream,
                  verify=verify,
                  proxies=proxies,
                  cert=cert,
                  timeout=timeout
                  )

    print(resp.status_code)

def streaming_uploads():
    with open('cnn.txt', 'rb') as f:
        r= requests.post('http://some.url/streamed', data=f)
    print(r.request.headers)

def gen():
    yield b'a'
    yield b'b'

def chunk_ended_requests():
    requests.post('http://some.url/chunked', data=gen())

#callback_function
def print_url(r, *args, **kwargs):
    print(r.url)

def event_hooks():
    requests.get('http://httpbin.org', hooks=dict(response=print_url))

def try_proxies():
    proxies = {
        'http': 'http://ASIA-PACIFIC\jerry_chen7:Dell09018@proxy.tpe.apac.dell.com:80',
        'https': 'https://ASIA-PACIFIC\jerry_chen7:Dell09018@proxy.tpe.apac.dell.com:80',
    }

    requests.get('http://example.org', proxies=proxies)

def try_socks():
    proxies = {
        'http': 'socks5://ASIA-PACIFIC\jerry_chen7:Dell09018@proxy.tpe.apac.dell.com:80',
        'https': 'socks5://ASIA-PACIFIC\jerry_chen7:Dell09018@proxy.tpe.apac.dell.com:80',
    }
    requests.get('http://example.org', proxies=proxies)

def verbs_get():
    r = requests.get(
        'https://api.github.com/repos/kennethreitz/requests/git/commits/a050faf084662f3a352dd1a941f2c7c9f886d4ad')
    if r.status_code == requests.codes.ok:
        print(r.headers['content-type'])

    commit_data = r.json()
    print(commit_data)
    print(commit_data.keys())
    print(commit_data[u'committer'])
    print(commit_data[u'message'])

def verbs_post():
    r = requests.get('https://api.github.com/repos/kennethreitz/requests/issues/482')
    print(r.status_code)

    issue = json.loads(r.text)
    print(issue[u'title'])
    print(issue[u'comments'])

    r = requests.get(r.url + u'/comments')
    print(r.status_code)
    comments = r.json()
    print(comments[9])
    print(comments[9].keys())
    print(comments[9][u'body'])
    print(comments[9][u'updated_at'])
    print(comments[9][u'user'][u'login'])

    body = json.dumps({u"body": u"Sounds great! I'll get right on it!"})
    url = u"https://api.github.com/repos/kennethreitz/requests/issues/482/comments"
    auth = HTTPBasicAuth('jerry2613@gmail.com', 'jerry2joan')
    r = requests.post(url=url, data=body, auth=auth)
    print(r.status_code)
    r = requests.patch(url=url, data=body, auth=auth)
    print(r.status_code)

def link_headers():
    url = 'https://api.github.com/users/kennethreitz/repos?page=1&per_page=10'
    r = requests.head(url=url)
    print(r.headers['link'])
    print(r.links["next"])
    print(r.links["last"])

if __name__ == '__main__':
#    r = requests.get('https://api.github.com/events', stream=True)
#    try_practicepython()
#    save_raw_stream_as_a_file()
#    custom_headers()
#    Send_form_encoded_data()
#    post_multipart_files()
#    cookies()
#    send_cookie()
#    try_auth()
#    try_digestAuth()
#    try_oauth()
#    save_cnn()
#    try_session()
#    try_prepare()
#    r = requests.get('https://requestb.in')
#    r = requests.get('https://github.com')
#    print(r.status_code)
#    streaming_uploads()
#    chunk_ended_requests()
#    event_hooks()
#    try_proxies()
#    try_socks()
#    verbs_get()
#    verbs_post()
    link_headers()