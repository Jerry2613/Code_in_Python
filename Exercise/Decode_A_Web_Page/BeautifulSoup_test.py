from bs4 import BeautifulSoup
from bs4 import CData

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""


def parse_cnn():
    with open('cnn.txt', 'rb') as CNN:
        soup = BeautifulSoup(CNN, 'html.parser')
        print(soup.prettify())
        print('===' * 100)
        print(soup.get_text())


def extracting_all_urls(soup, key):
    for link in soup.find_all(key):
        print(link.get('href'))


def try_comment():
    markup = "<b><!--Hey, buddy. Want to buy a used parser?--></b>"
    soup = BeautifulSoup(markup, 'html.parser')
    comment = soup.b.string
    print(type(comment))
    print(comment)
    print(soup.prettify())


def try_cdata():
    markup = "<b><!--Hey, buddy. Want to buy a used parser?--></b>"
    soup = BeautifulSoup(markup, 'html.parser')
    comment = soup.b.string
    cdata = CData("A CDATA block")
    comment.replace_with(cdata)
    print('*'*50, 'Try_Cdata', '*'*50)
    print(type(comment))
    print(comment)
    print(soup.prettify())

if __name__ == '__main__':
#   parse_cnn()
    soup = BeautifulSoup(html_doc, 'html.parser')
    print(soup.prettify())
    print('*'*100)
#    print(soup.title)
#    print(soup.title.name)
#    print(soup.title.string)
#    print(soup.title.parent)
#    print(soup.title.parent.name)
#    print(soup.title.parent.string)
#    print(soup.p)
#    print(soup.p['class'])
#    print(soup.a)
#    for sibling in soup.a.next_siblings:
#        print(sibling)
#    for sibling in soup.a.previous_siblings:
#        print(sibling)
#    print(soup.find_all('a'))
#    print(soup.find(id = "link3"))
#    extracting_all_urls(soup, 'a')
#    print(soup.get_text())
#    print(type(soup.a))
#    print(type(soup.body))
#    print(soup.body.get_text())
#    print(soup.a.name)
#    print(soup.a.attrs)
#    print(soup.a['href'])
#    print(soup.a.get('class'))
#    soup.a['class']="newClass"
#    print(soup.a.get('class'))
#    print(soup.a.attrs)
#    print(type(soup.a.string))
#    print(soup.a.string)
#    print(soup.a.string.replace_with("No longer bold"))
#    print(soup.a.string)
#    try_comment()
#    try_cdata()