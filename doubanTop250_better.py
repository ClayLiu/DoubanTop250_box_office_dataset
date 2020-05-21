import re
import json
import tqdm
import requests
import pandas as pd 
from bs4 import BeautifulSoup

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Conection': 'keep-alive',
    'Cookie' : 'gr_user_id=7a537451-6766-434b-b6a8-a0bc369c42b5; douban-fav-remind=1; trc_cookie_storage=taboola%2520global%253Auser-id%3D7748545e-08c4-413b-9036-9d8e3a6cb01f-tuct17b293e; __gads=ID=7d5255a243a8e94d:T=1562131803:S=ALNI_MZyPlf2Pr_QmOQ9Y5ILFw4JmO6kLA; ll="118281"; bid=uzbNzCNKi20; __utma=30149280.970962883.1589989526.1589989526.1589989526.1; __utmb=30149280.1.10.1589989526; __utmc=30149280; __utmz=30149280.1589989526.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; dbcl2="217041533:zQyArd2BMeo"; ck=_jkA; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1589989548%2C%22https%3A%2F%2Fopen.weixin.qq.com%2Fconnect%2Fqrconnect%3Fappid%3Dwxd9c1c6bbd5d59980%26redirect_uri%3Dhttps%253A%252F%252Fwww.douban.com%252Faccounts%252Fconnect%252Fwechat%252Fcallback%26response_type%3Dcode%26scope%3Dsnsapi_login%26state%3DuzbNzCNKi20%252523douban-web%252523https%25253A%252F%252Fmovie.douban.com%252Ftop250%25253Fstart%25253D100%252526filter%25253D%22%5D; _pk_id.100001.4cf6=aa3e77e5e70fe62a.1589989548.1.1589989606.1589989548.; _pk_ses.100001.4cf6=*; __utma=223695111.383783329.1589989548.1589989548.1589989548.1; __utmb=223695111.0.10.1589989548; __utmc=223695111; __utmz=223695111.1589989548.1.1.utmcsr=open.weixin.qq.com|utmccn=(referral)|utmcmd=referral|utmcct=/connect/qrconnect; push_noty_num=0; push_doumail_num=0'
}

url_search = 'http://www.endata.com.cn/API/GetData.ashx'

def get_movie_box_office(imdb_str : str) -> dict:
    box_office = {
        'Domestic' : '',
        'International' : '',
        'Worldwide' : ''
    }
    pattern = re.compile('(\w{1,})')

    url = 'https://www.boxofficemojo.com/title/{}/?ref_=bo_se_r_1'.format(imdb_str)
    r = requests.get(url, headers = headers)
    html = r.content.decode('utf-8')
    bs = BeautifulSoup(html, 'lxml')
    
    h1 = bs.find('h1', attrs = {'class' : 'a-size-extra-large'})
    enname = h1.text if h1 else ''
    
    big_div = bs.find('div', attrs = {'class' : 'a-section a-spacing-none mojo-performance-summary'})

    divs = big_div.find_all('div', attrs = {'class' : 'a-section a-spacing-none'})
    
    for single_div in divs:
        type_span = single_div.find('span')
        type_str = pattern.search(type_span.text).group(0)
        if type_str in box_office.keys():
            money_span = single_div.find('span', attrs = {'class' : 'money'})
            money = money_span.text if money_span else '获取失败'

            box_office[type_str] = money
    
    box_office['English name'] = enname[:-7]
    return box_office

def get_movie_enname(movie_imdb_link : str) -> str:
    r = requests.get(movie_imdb_link, headers = headers)
    html = r.content.decode('utf-8')
    bs = BeautifulSoup(html, 'lxml')

    div = bs.find('div', attrs = {'class' : 'title_wrapper'})
    h1 = div.find('h1')

    if h1:
        movie_enname = h1.text
        movie_enname = movie_enname[:-7]
    else:
        movie_enname = ''
    
    return movie_enname

def get_movie_link_in_page(page : int):
    page_url = 'https://movie.douban.com/top250?start={}&filter='.format((page - 1) * 25)
    r = requests.get(page_url, headers = headers)
    html = r.content.decode('utf-8')
    bs = BeautifulSoup(html, 'lxml')
    # print(html)
    ol = bs.find('ol', attrs = {'class' : 'grid_view'})
    li = ol.find_all('li')

    movie_link_list = []
    for single_movie in li:
        div_hd = single_movie.find('div', attrs = {'class' : 'hd'})
        a = div_hd.find('a')
        href = a['href']
        movie_link_list.append(href)
    
    return movie_link_list

def deal_one_movie(movie_link : str) -> dict:
    r = requests.get(movie_link, headers = headers)
    html = r.content.decode('utf-8')
    bs = BeautifulSoup(html, 'lxml')

    movie_name_span = bs.find('span', attrs = {'property' : 'v:itemreviewed'})
    movie_name = movie_name_span.text if movie_name_span else '获取失败'
    print(movie_name)

    year_span = bs.find('span', attrs = {'class' : 'year'})
    year = year_span.text if year_span else '获取失败'
    year = year[1:-1]

    big_div = bs.find('div', attrs = {'class' : 'subjectwrap clearfix'})

    star_tag = big_div.find('strong', attrs = {'class' : 'll rating_num'})
    star = star_tag.text if star_tag else '获取失败'
    
    vote_tag = big_div.find('span', attrs = {'property' : 'v:votes'})
    vote_num = vote_tag.text if vote_tag else '获取失败'

    info_div = big_div.find('div', attrs = {'id' : 'info'})
    
    span = info_div.find_all('span')

    director_span = span[0].find('span', attrs = {'class' : 'attrs'})
    scriptwriter_span = span[3].find('span', attrs = {'class' : 'attrs'})

    director_a = director_span.find_all('a')
    director_list = []
    for single_director in director_a:
        director_list.append(single_director.text)
    director_list_str = '/'.join(director_list)

    if scriptwriter_span:
        scriptwriter_a = scriptwriter_span.find_all('a')
        scriptwriter_list = []
        for single_scriptwriter in scriptwriter_a:
            scriptwriter_list.append(single_scriptwriter.text)
        scriptwriter_list_str = '/'.join(scriptwriter_list)
    else:
        scriptwriter_list_str = ''

    imdb_link_a_tag = big_div.find_all('a', attrs = {'target' : '_blank'})
    for single_imdb_link_a_tag in imdb_link_a_tag:
        if single_imdb_link_a_tag.text[:2] == 'tt':
            imdb_str = single_imdb_link_a_tag.text
        

    actor_list_tag_span = info_div.find('span', attrs = {'class' : 'actor'})
    if actor_list_tag_span:
        actor_list_tag = actor_list_tag_span.find('span', attrs = {'class' : 'attrs'})
        actor_list_a = actor_list_tag.find_all('a')
    
        actor_list = []
        for single_actor_a in actor_list_a:
            actor_list.append(single_actor_a.text)
        actor_list_str = '/'.join(actor_list)
    else:
        actor_list_str = ''

    length_span = big_div.find('span', attrs = {'property' : 'v:runtime'})
    length = length_span.text if length_span else ''

    type_span = big_div.find_all('span', attrs = {'property' : 'v:genre'})
    type_list = []
    for single_type in type_span:
        type_list.append(single_type.text)
    type_list_str = '/'.join(type_list)

    # 超级耗时函数
    box_office = get_movie_box_office(imdb_str)
    # print(box_office)

    out_dict = {
        'movie name' : movie_name,
        'star' : star,
        'year' : year,
        'length' : length,
        'vote num' : vote_num,
        'director' : director_list_str,
        'scriptwriter' : scriptwriter_list_str,
        'actor' : actor_list_str,
        'type' : type_list_str,
        'imdb str' : imdb_str
    }
    out_dict.update(box_office)
    return out_dict


page_total = 10
for i in range(5, page_total + 1):
    print(i)

    df = pd.DataFrame(columns=[
        'movie name',
        'English name',
        'star',
        'year',
        'length',
        'vote num',
        'director',
        'scriptwriter',
        'type',
        'actor',
        'Domestic',
        'International',
        'Worldwide',
        'imdb str'
    ])
    movie_link_list = get_movie_link_in_page(i)
    for movie_link in movie_link_list:
        temp_dict = deal_one_movie(movie_link)
        # print(temp_dict)
        df = df.append(temp_dict, ignore_index = True)

    df.to_csv('doubanTop250better_part{}.csv'.format(i))

print('done')