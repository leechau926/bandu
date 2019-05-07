import requests
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0'
}

def get_page_max(url):
    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html, 'lxml')
    area = soup.find(attrs={'class': 'cl_page'})
    page_max = int(re.findall('=(\d+)$', area.find(attrs={'class': 'last'}).a['href'])[0])
    print(page_max)
    return page_max

def get_book_down(book_id):
    down_url = 'https://www.bandubook.com/book/download/' + str(book_id) + '.html'
    html = requests.get(down_url, headers=headers).content
    soup = BeautifulSoup(html, 'lxml')
    if soup.find(attrs={'class': 'fa fa-cloud-download'}):
        cloud = soup.find(attrs={'class': 'fa fa-cloud-download'})
        book_panurl = re.findall("\'(.*?)\'", cloud.next_sibling['onclick'])[0]
        if len(soup.find(attrs={'class': 'links_middle'}).find_all('li')) == 2:
            book_passwd = re.findall('：(\w+)', soup.find(attrs={'class': 'links_middle'}).find_all('li')[1].string)[0]
        else:
            book_passwd = ''
        downinfo = {
            'panurl': book_panurl,
            'passwd': book_passwd
        }
    else:
        downinfo = {
            'panurl': '',
            'passwd': ''
        }
    return downinfo


def get_book_info(url):
    html = requests.get(url, headers=headers).content
    soup = BeautifulSoup(html, 'lxml')
    contents = soup.find_all(attrs={'class': 'recent-info'})
    for cont in contents:
        title = cont.find('h3').string.replace("'", "`")
        author = cont.find('h5').string
        description = cont.select('div')[1].string.strip()
        book_id = int(re.findall('(\d+)\.html', cont.a['href'])[0])
        book_url = 'https://www.bandubook.com/book/' + str(book_id) + '.html'
        downinfo = get_book_down(book_id)
        book_downurl = downinfo['panurl']
        book_passwd = downinfo['passwd']
        info_sql = """INSERT INTO book_info (title, author, description, book_id, book_url, book_downurl, book_passwd)
        VALUES ('%s', '%s', '%s', '%d', '%s', '%s', '%s');\n""" % (title, author, description, book_id, book_url, book_downurl, book_passwd)
        with open('book_url.sql', 'a', encoding='utf-8') as f:
            f.write(info_sql)
        print('%s saved!' % title)

if __name__ == '__main__':
    index_url = 'https://www.bandubook.com/tag/%E5%8E%86%E5%8F%B2.html'
    page_max = get_page_max(index_url)
    for i in range(1, page_max + 1):
        page_url = index_url + '?page=' + str(i)
        get_book_info(page_url)
        print('Page %d/%d saved!' % (i, page_max))
        print('***************************************')
