import glob
import requests
if glob.glob("config.py"):
    import config
else:
    import github_config as config
import lxml, os
from bs4 import BeautifulSoup as bs
import pause
from deep_translator import GoogleTranslator
from novelupdates_release import page_linktonu
from wordpress_post import posting, posting_test
from requests.auth import HTTPBasicAuth

count = 0
user_agent = {'User-Agent': 'Mozilla/5.0'}

def page_translate(url):
    novel = requests.get(url, headers=user_agent)
    novel.raise_for_status()
    novel.encoding = "GBK"
    novelSoup = bs(novel.text, "html.parser")
    novel_content = novelSoup.find("div", {"class": "readcontent"})
    novel_content = novel_content.get_text(strip=True, separator='\n')
    novel_content = novel_content.replace('AD4', '').replace('\\n', '\n').replace('\x1a', '')

    text = '[unedited]' + '\n'
    for content in novel_content.split("\n"):
        try:
            translated = GoogleTranslator(source='auto', target='en').translate(content)
            text = text + '\n' + translated
        except Exception as e:
            e = str(e)
            if "can only concatenate str" in e:
                pass
            elif "otherwise it cannot be translated" in e:
                text = text + '\n' + content
            else:
                print(e)
                pass
    return text

def header_name(url):
    novel = requests.get(url, headers=user_agent)
    novel.raise_for_status()
    novel.encoding = "GBK"
    novelSoup = bs(novel.text, "html.parser")
    heading = novelSoup.find("li", {"class": "active"})
    heading = heading.get_text(strip=True, separator='\n')  
    header = ''
    for content in heading.split(" "):
        try:
            translated = GoogleTranslator(source='auto', target='en').translate(content)
            if header == '':
                header = translated
            else:
                header = header + " " + translated
            if header[-1] == ")":
                
                header = header.split(" ")
                heading = ''
                for i in header:
                    if heading == '':
                        heading = i
                    else:
                        heading = heading + " " + i
                header = heading
        except Exception as e:
            print(e)
    [header.replace(i, '') for i in config.special]
    return header


def page_publishandlink(df):
    novel = requests.get(config.url, headers=user_agent)
    novel.raise_for_status()
    novel.encoding = "GBK"
    novelSoup = bs(novel.text, "html.parser")
    page_lst = []
    novel_link = novelSoup.findAll('dd')
    for dd in novel_link:
        page_lst.append(dd.find('a')['href'])
    # print(page_lst)
    for page in sorted(page_lst):
        url = config.url + str(page)
        print(url)
        try:
            heading = header_name(url)
            print(heading)
            test = posting_test(heading, df)
            print(test)
            if test == "Need to be posted":
                content = page_translate(url)                    
                # whoops, I forgot to publish it!
                publish_id = posting(heading, content)
                #also need to put it on NU
                # print(page_linktonu(config.novel_link + publish_id, 'c' + str(df.shape[0] + 1)))
                dct = {"name": heading, "post_id": publish_id,
                       "link_id": url, "wp_link": config.novel_link + publish_id}
                df = df.append(dct, ignore_index=True)
                df.to_csv('published.csv', mode='a')
                print(df)
                pause.days(7)
        except Exception as e:
            print("Error in Publishing: " + str(e))
            exit()
    return df
