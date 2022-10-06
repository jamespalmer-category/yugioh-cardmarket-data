import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

def is_there_another_page(set_name, i):
    #turn this into a function where database and length of database are the outputs.

    cardmarket_result = requests.get('https://www.cardmarket.com/en/YuGiOh/Products/Singles/{}?sortBy=collectorsnumber_asc&site='.format(set_name) + str(i))
    src = cardmarket_result.content
    soup = BeautifulSoup(src, 'html.parser')
    card_price_info = soup.find_all(attrs = {'class':'col'})
    
    #get the data in lists
    names = []
    numbers = []
    rarities = []
    links = []

    for entry in card_price_info:
        if entry.find('a') != None:
            cardmarket_url = entry.find('a')
            if (cardmarket_url.attrs['href'] != 'https://www.facebook.com/CardmarketYugioh') and (cardmarket_url.attrs['href'] != '/en/YuGiOh/Policies/GeneralTermsAndConditions'):
                links.append('https://www.cardmarket.com/' + cardmarket_url.attrs['href'])


        if entry.find(attrs = {'class' : 'col-10 col-md-8 px-2 flex-column align-items-start justify-content-center'}) != None:
            name = entry.find(attrs = {'class' : 'col-10 col-md-8 px-2 flex-column align-items-start justify-content-center'})
            if name.text != 'Name':
                re_name = re.sub('\"','', name.text)
                re_name = re.sub(':','', re_name)
                re_name = re.sub('/','', re_name)
                re_name = re.sub('\?','', re_name)
                names.append(re_name)

        if entry.find(attrs = {'class' : 'col-md-2 d-none d-lg-flex has-content-centered'}) != None:
            number = entry.find(attrs = {'class' : 'col-md-2 d-none d-lg-flex has-content-centered'})
            if number.text != 'Number':
                numbers.append(number.text)


        if entry.find(attrs = {'class' : 'icon'}) != None:
            if 'title' in list(entry.find(attrs = {'class' : 'icon'}).attrs.keys()):
                rarity = entry.find(attrs = {'class' : 'icon'}).attrs['title']
                if rarity != 'Facebook - Cardmarket':
                    rarities.append(rarity)
    
    uk_links = []
    for link in links:
        link = link + '?sellerCountry=13'
        uk_links.append(link)

    page_set_content = pd.DataFrame({'Card Name': names, 'Card Number' : numbers, 'Rarity': rarities, 'Cardmarket Links': links, 'Cardmarket UK Links': uk_links})

    return (page_set_content, len(page_set_content))

def cardmarket_df(set_name):
    
    i = 1
    dfs = []
    
    while is_there_another_page(set_name, i)[1] == 20:
        
        dl_pair = is_there_another_page(set_name, i)
        dfs.append(dl_pair[0])
        
        if len(dfs) > 1:
            if dfs[-1].equals(dfs[-2]):
                return pd.concat(dfs[:-1], ignore_index = True)
        i = i+1
        
    else:
        dfs.append(is_there_another_page(set_name, i)[0])

    return pd.concat(dfs, ignore_index = True)