import requests
from bs4 import BeautifulSoup

url = 'http://www.nytimes.com'
proxies = {
    "http": "http://ASIA-PACIFIC\jerry_chen7:Dell09020@proxy.tpe.apac.dell.com:80",
    "https": "https://ASIA-PACIFIC\jerry_chen7:Dell09020@proxy.tpe.apac.dell.com:80",
}

if __name__ == '__main__':
    r = requests.get(url, proxies=proxies)
    with open('New_YorK_Time.html', 'wb') as fd:
       for chunk in r.iter_content(chunk_size=128):
           fd.write(chunk)
    soup = BeautifulSoup(open('New_YorK_Time.html', 'rb'), 'html.parser')
    for story_heading in soup.find_all(class_='story-heading'):
        if story_heading.a:
            print(story_heading.a.text.replace("\n", " ").strip() )
        else:
            print(story_heading.contents[0].strip())
