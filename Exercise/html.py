import requests

if __name__ == '__main__':
    r = requests.get('https://api.github.com/user')
    print(r.text)
    print(r.status_code)
    print(r.request.headers)
    print(r.headers)
    print(r.headers['Server'])
    print(r.encoding)
    print(r.json)
    r = requests.get('https://api.github.com/events')
    print(r.text)
   