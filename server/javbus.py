import requests
from bs4 import BeautifulSoup

HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7',
    'referer': 'https://www.javbus6.pw/',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
}


def get_html(url):
    try:
        r = requests.get(url)
        return r.text
    except Exception as err:
        print(err)
        return ''


def get_url(bangou):
    base_url = 'https://www.javbus6.pw/'
    return base_url + bangou


def get_pics(bangou):
    url = get_url(bangou)
    html = get_html(url)
    soup = BeautifulSoup(html, 'html5lib')

    # 预览图的DOM结构：<a href=full><div><img src=thumb></div></a>
    # 预览图的class='sample-box'
    samples = soup.find_all(class_='sample-box')

    pics = []
    for sample in samples:
        pic = {}
        pic['full'] = sample['href']
        pic['thumb'] = sample.find('img')['src']
        pic['title'] = sample.find('img')['title']
        pics.append(pic)
    return pics


if __name__ == '__main__':
    print(get_pics('MIDE-535'))
    print(get_pics('KDKJ-065'))