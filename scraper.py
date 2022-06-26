import os
import requests
from bs4 import BeautifulSoup
import string
import csv
from urllib.parse import urlparse, urljoin
import re
import enchant
import time
import matplotlib.pyplot as plt




def cleanup(text):
    blacklist = [ 
'account',
'acronym',
'active',
'actions',
'add',
'address',
'after',
'align',
'alignment',
'animation',
'announcement',
'applet',
'are',
'area',
'arrow',
'article',	 
'aside',
'aspect',
'asset',
'audio',
'author',
'background',
'banner',
'bar',
'base',
'basic',
'before',
'big',
'block',
'blog',
'bleed',
'body',
'border',
'bottom',
'box',
'bullet',
'button',
'canvas',	 
'caption',
'card',
'carousel',
'cart',
'category',
'center',	 
'cite',
'close',
'code',	 	  
'collection',
'color',
'column',
'comment',
'commerce',
'compress',
'content',
'control',
'current',
'data',	 
'date',
'default',
'delimiter',
'description',
'design',
'details',	 
'dfn',	 
'dialog',	 	 
'doctype',
'document',
'domain',
'edit',
'element',	  
'embed',
'enable',
'event',
'excerpt',
'false',
'fade',
'field',	 	 
'figure',
'filter',
'fill',
'first',
'floating',
'flex',
'focus',
'follow',
'font',	 
'footer',
'foreground',
'form', 
'frame',	 
'function',
'fullscreen',
'gallery',
'global',
'gradient',
'grid',
'group',
'gutter',
'head',
'header',
'height',
'hover',	 
'html',
'http',
'icon',
'image',
'important',
'index',
'inner',
'input',
'item',
'knockout',
'label',
'layout',
'legend',
'less',
'light',
'linear',
'link',
'list',
'main', 
'map',
'margin',
'mark',
'mask',
'max',
'media',
'member',
'menu',
'meta',
'meter',
'min',
'modal',
'more',
'name',
'native',
'nested',
'next',	 
'null',
'object',	 
'opacity',
'open',
'optgroup',	 
'option',
'other',
'outline',
'output',
'overlap',
'overlay',
'page',
'pagination',
'parent',
'picture',
'placeholer',
'poster',
'price',
'primary',
'product',
'products',
'progress',	 
'quantity',
'quick',
'query',
'ranges',
'ratio',
'read',
'return',
'rgba',
'right',
'rollups',
'ruby',
'script',
'search',
'secondary',
'section',	 
'select',
'shadow',
'shape',
'side',
'simple',
'single',
'slide',
'small',
'social',
'solid',
'source',
'spacing',
'span',
'squarespace',
'stack',
'static',
'strike',
'stroke',
'strong',	 
'style',
'subtitle',
'subscription',
'summary',	 
'table',
'template',
'text',
'time',
'title',
'toggle',
'top',
'track',
'true',
'tweak',
'type',
'universal',
'user',
'value',
'value',
'variant',
'video',
'view',
'white',
'width',
'will',
'window',
'wrapper',
'www']	 
    text = text.strip()
    text = text.lower()
    for char in string.punctuation:
        text = text.replace(char, '')

    text = re.sub('\s+(a|an|and|the|is|this|not|by|to|if|of|on|in|has|within|with|our|your|any)(\s+)', '\2', text)

    output =  list(text.split(" "))
    output = list(filter(None, output))
    output = [x for x in output if not x.isdigit()]
    output = [x for x in output if not (x.isalnum() and not x.isalpha() and not x.isdigit())]

    d_us = enchant.Dict("en_US")
    d_uk = enchant.Dict("en_GB")
    output = [x for x in output if d_us.check(x) or d_uk.check(x)]
    output = [x for x in output if len(x)>2]
    output = [x for x in output if x not in blacklist]
    output = [x for x in output if not output.count(x)>15]

    return output 

def write_csv(output, title, url):
    a = urlparse(url)
    domain = a.netloc
    try:
       os.mkdir("./"+domain)
    except OSError as e:
        pass
    filename = './'+domain+'/'+'keywords'+'_'+domain+'_'+os.path.basename(a.path)+'.csv'
    with open(filename, mode='w') as keyword_file:
        keyword_writer = csv.writer(keyword_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')

        keyword_writer.writerow(['TITLE',  title])
        keyword_writer.writerow(['URL',  url])
        keyword_writer.writerow(['KEYWORD',  'COUNT'])
        b = []
        for word in output:
            occurrences = output.count(word)
            b.append([word, occurrences])
            keyword_writer.writerow([word, occurrences])
        print('csv created!')
        b.sort(key = lambda b: b[1])
        top = b[-10:]
        x = [i[0] for i in top]
        y = [i[1] for i in top]
        plt.bar(x, y, color='#4c649c')
        plt.suptitle('keywords'+'_'+domain+'_'+os.path.basename(a.path))
        plt.xticks(rotation='45', fontsize=5)

        plt.savefig('./'+domain+'/'+'keywords'+'_'+domain+'_'+os.path.basename(a.path)+'.png',dpi=400)
        print('bar chart created!')
   
total_urls_visited = 0
internal_urls = set()
external_urls = set()

def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url):
    urls = set()
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    time.sleep(5)
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            continue
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            continue
        if href in internal_urls:
            continue
        if domain_name not in href:
            if href not in external_urls:
                external_urls.add(href)
            continue
        urls.add(href)
        internal_urls.add(href)
    return urls
        
if __name__ == "__main__":
    url = str(input('enter url: '))
    links = get_all_website_links(url)
    print('found links:')
    for internal_link in internal_urls:
        try:
            print(internal_link)
            res = requests.get(internal_link)
            time.sleep(5)
            html_page = res.content
            soup = BeautifulSoup(html_page, 'html.parser')
            title = soup.title.string
            text = soup.find_all(text=True)
            output = cleanup(str(text))
            write_csv(output, title, internal_link)
        except:
            continue

            
    
        
    

