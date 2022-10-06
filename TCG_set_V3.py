import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import os

#Get the set page from https://yugipedia.com/wiki/Yugipedia
class TCG_set:
    def __init__(self, url):
        #Gives us url, set content df, number of cards, set name.
        
        #Getting the url we put in
        self.url = url
        result = requests.get(url)
        src = result.content
        soup = BeautifulSoup(src, 'html.parser')
        
        #Getting the name of the set
        set_name = soup.find('h1')
        self.set_name = set_name.text
        
        #Getting the content of the set
        card_info_headers = soup.find_all(attrs = {'class':'set-list'})

        #getting the name of each table column - not convinced we need this
        #col_name = []
        #headers = card_info_headers.find_all('th')
        #for header in headers:
        #    col_name.append(header.text)

        #getting the name of each table column - get the number of headers
        col_name = []
        headers = card_info_headers[0].find_all('th')

        #split table data into the four/five categories from the title above
        card_number = []
        card_name = []
        card_rarity = []
        card_category = []
        
        
        if len(headers) == 4:
            table_data = []
            for table in card_info_headers:
                indiv_table = table.find_all('td')
                table_data = table_data + indiv_table
            for i in range(0,len(table_data)):
                if (i % 4 == 0):
                    card_number.append(table_data[i].text)
                elif (i % 4 == 1):

                    #get rid of the quote marks around the name/ in the name/ other punctuation marks.

                    name = table_data[i].text[1:len(table_data[i].text)-1]
                    name = re.sub('\"','', name)
                    name = re.sub('/', '', name)
                    name = re.sub(':','', name)

                    card_name.append(name)

                elif (i % 4 == 2):
                    card_rarity.append(table_data[i].text)
                else:
                    card_category.append(table_data[i].text)

            set_content = pd.DataFrame({"Set Number" : card_number, "Name": card_name, "Rarity": card_rarity, "Category": card_category}) 
            self.set_content_yugipedia = set_content.sort_values('Set Number', ignore_index = True)

        elif len(headers) == 5:
            card_print = []
            table_data = []
            for table in card_info_headers:
                indiv_table = table.find_all('td')
                table_data = table_data + indiv_table
            for i in range(0,len(table_data)):
                if (i % 5 == 0):
                    card_number.append(table_data[i].text)
                elif (i % 5 == 1):

                    #get rid of the quote marks around the name

                    name = table_data[i].text[1:len(table_data[i].text)-1]
                    name = re.sub('\"','', name)
                    name = re.sub('/', '', name)

                    card_name.append(name)

                elif (i % 5 == 2):
                    card_rarity.append(table_data[i].text)
                elif (i % 5 == 3):
                    card_category.append(table_data[i].text)
                else:
                    card_print.append(table_data[i].text)

            set_content = pd.DataFrame({"Set Number" : card_number, "Name": card_name, "Rarity": card_rarity, "Category": card_category, "Print" : card_print}) 
            self.set_content_yugipedia = set_content.sort_values('Set Number', ignore_index = True)

        elif len(headers) == 6:
            card_print = []
            card_quantity = []
            table_data = []
            for table in card_info_headers:
                indiv_table = table.find_all('td')
                table_data = table_data + indiv_table
            for i in range(0,len(table_data)):
                if (i % 6 == 0):
                    card_number.append(table_data[i].text)
                elif (i % 6 == 1):

                    #get rid of the quote marks around the name

                    name = table_data[i].text[1:len(table_data[i].text)-1]
                    name = re.sub('\"','', name)
                    name = re.sub('/', '', name)

                    card_name.append(name)

                elif (i % 6 == 2):
                    card_rarity.append(table_data[i].text)
                elif (i % 6 == 3):
                    card_category.append(table_data[i].text)
                elif (i % 6 == 4):
                    card_print.append(table_data[i].text)
                else:
                    card_quantity.append(table_data[i].text)

            set_content = pd.DataFrame({"Set Number" : card_number, "Name": card_name, "Rarity": card_rarity, "Category": card_category, "Print" : card_print, "Quantity" : card_quantity}) 
            self.set_content_yugipedia = set_content.sort_values('Set Number', ignore_index = True)

        #Set code - looking at 2nd item in the list to circumvent an issue on the Battle of Chaos page.
        if len(card_number) > 1:
            self.set_code = card_number[1][0:4]
        else:
            self.set_code = card_number[0][0:4]
        
        #Getting the number of cards
        self.set_card_number = len(set_content)
        
        #Clean the name to put into a cardmarket url.
        re_set_name = self.set_name.replace(' ', '-')
        re_set_name = re.sub('\'','', re_set_name)
        re_set_name = re.sub(':','', re_set_name)
        re_set_name = re.sub('-\(set\)', '', re_set_name)
        #Number of index pages
        if (self.set_code[0:3] == 'LDS') or self.set_code == 'DLCS':
            no_of_pages = 12
        elif self.set_code == 'YCSW':
            no_of_pages = 2
            re_set_name = 'YuGiOh-Championship-Series-Prize-Cards'
        elif self.set_code == 'LED9':
            re_set_name = 'Legendary-Duelists-9'
            no_of_pages = 3
        elif self.set_code == 'GFP2':
            re_set_name = '2022-Ghosts-From-the-Past'
            no_of_pages = 10
        elif self.set_code == 'OPTP':
            re_set_name = 'Trials-of-the-Pharaoh-Promos'
            no_of_pages = 1
        elif self.set_code == 'HAC1':
            no_of_pages = 15
        elif self.set_code == 'LART':
            no_of_pages = 3
            re_set_name = 'Lost-Art-Promos'
        elif self.set_code == 'MP20':
            no_of_pages = (self.set_card_number // 20) + 1
            re_set_name = re_set_name + '-Mega-Pack'
        else:
            no_of_pages = (self.set_card_number // 20) + 1
        #Getting cardmarket index
        names = []
        numbers = []
        rarities = []
        links = []

        for i in range(1, no_of_pages+1):
            cardmarket_result = requests.get('https://www.cardmarket.com/en/YuGiOh/Products/Singles/{}?sortBy=collectorsnumber_asc&site='.format(re_set_name) + str(i))
            src = cardmarket_result.content
            soup = BeautifulSoup(src, 'html.parser')
            card_price_info = soup.find_all(attrs = {'class':'col'})
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

        cardmarket_set_content = pd.DataFrame({'Card Name': names, 'Card Number' : numbers, 'Rarity': rarities, 'Cardmarket Links': links, 'Cardmarket UK Links': uk_links}) 
        self.cardmarket_set_content = cardmarket_set_content
        
        
    #Quick function to get the set content printed as a .csv file
    def content_to_csv(self):
        self.set_content_yugipedia.to_csv('{} yugipedia.csv'.format(self.set_name))
        self.cardmarket_set_content.to_csv('{} cardmarket.csv'.format(self.set_name))
        
    #This function gets us the price data for the last two weeks for each card in the set
    def cardmarket_price_last_30_days(self, set_number):
        df = self.cardmarket_set_content.iloc[:]
        
        #Make the directory for the set price data if it doesn't exist
        if not os.path.exists('Cardmarket data\{}'.format(self.set_code)):
            os.makedirs('Cardmarket data\{}'.format(self.set_code))
        else:
            print("Already have Cardmarket data\{}".format(self.set_code))
        
        latest_date = []
        latest_price = []
        for j in range(set_number,len(df)):

            #Parsing the site for the data from the chart (last two weeks of avg sale price in Euros)
            url = list(df['Cardmarket UK Links'])[j]
            result = requests.get(url)
            src = result.content
            soup = BeautifulSoup(src, 'html.parser')
            card_price_info = soup.find_all(attrs = {'class':'chart-init-script'})

            #Getting the info we want from the parsing
            if card_price_info != []:

                info = str(card_price_info[0])
                i = 0
                chart_data = []
                info_2 = info
                while i < len(info):
                    m = info_2.find(r"[")
                    n = info_2.find(r"]")
                    i = i + n + 2
                    chart_data.append(info_2[m+1:n])
                    info_2 = info[i:]

                #Dates data
                chart_data_dates = chart_data[0].split(',')
                for i in range(0, len(chart_data_dates)):
                    chart_data_dates[i] = re.sub(r'\"', '', chart_data_dates[i])
                latest_date.append(chart_data_dates[-1])

                #Getting Price Data
                chart_data_price = chart_data[1].split(',')
                chart_data_price = chart_data_price[1:]
                chart_data_price[0] = chart_data_price[0][8:]
                for i in range(0, len(chart_data_price)):
                    chart_data_price[i] = re.sub(r'\"', '', chart_data_price[i])
                    chart_data_price[i] = float(chart_data_price[i])

                latest_price.append(chart_data_price[-1])

                date_avg_price_dict = {chart_data_dates[i] :chart_data_price[i] for i in range(0, len(chart_data_price))}
                df_prices = pd.DataFrame({'Date': chart_data_dates, 'Price (Euros)': chart_data_price})
            
                #take the price data and puts it in a CSV
            
                df_prices.to_csv('Cardmarket data\{}\{} {} price.csv'.format(self.set_code, self.set_code + '-' + df['Card Number'][j], list(df['Card Name'])[j]))
            
            else:
                print('No chart data for {} {}'.format(self.set_code + '-' + df['Card Number'][j], list(df['Card Name'])[j]))