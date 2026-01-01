from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import random
import re

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
]

class TeaParser():
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': random.choice(USER_AGENTS)})
    
    def tea_cart_parser(self, url):
        response = self.session.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        carts_links = set()

        for cart in soup.select('.catalog-item__title a[href]'):
            link =  cart.get('href')
            if link:
                absolute_link = urljoin(url, link)
                carts_links.add(absolute_link)

        return list(carts_links)

    def tea_parser(self, url):
        response = self.session.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')

        tea_data = {
            'name': self.get_name(soup),
            'tea_type': self.get_type(soup),
            'making_time': self.get_making_time(soup),
            'temperature': self.get_temperature(soup),
            'tastes': self.get_taste(soup),
            'price': self.get_price(soup),
        }

        return tea_data
    
    def get_name(self, soup):
        name = soup.find(id='product_name')
        return name.text.strip() if name else ""
    
    def get_type(self, soup):
        html_tag = soup.find('span', class_='option__label', string='Вид')

        if html_tag:
            parent_row = html_tag.find_parent('tr')
            if parent_row:
                kind_link = parent_row.find('a', class_='option__value')
                if kind_link:
                    tea_type = kind_link.text.strip().lower()
                    return tea_type
                
    def get_making_time(self, soup):
        time_element = soup.select_one('.keep__rule-time')
        if not time_element:
            return 0
        
        time_str = time_element.text.strip().lower()
        time_str = re.sub(r'[^\d\.\-–]', '', time_str)
        time_str = re.sub(r'[–—]', '-', time_str)
        
        if not time_str or time_str.lower() == 'none':
            return 0
        
        try:
            if '-' in time_str:
                parts = time_str.split('-')
                numbers = [float(p.strip()) for p in parts if p.strip()]
                if len(numbers) >= 2:
                    avg = sum(numbers) / len(numbers)
                    return int(round(avg))
                elif len(numbers) == 1:
                    return int(round(numbers[0]))
                else:
                    return 0
            else:
                return int(round(float(time_str)))
        except (ValueError, TypeError):
            return 0

        
    def get_temperature(self, soup):
        html_tag = soup.find_all('div', class_='keep-rule')
        
        for block in html_tag:
            label_element = block.select_one('.keep-rule__label')
            if not label_element:
                continue
                
            label_text = label_element.text.strip().lower()

            if any(word in label_text for word in ['температура', 'temp', 'градус', '°c']):
                value_element = block.select_one('.keep-rule__value')
                if value_element:
                    temp_str = value_element.text.strip()
                    numbers = re.findall(r'\d+', temp_str)
                    
                    if len(numbers) >= 2:
                        avg = (int(numbers[0]) + int(numbers[1])) / 2
                        result = int(round(avg))
                        return result
                    elif len(numbers) == 1:
                        result = int(numbers[0])
                        return result
        return 0
        
    def get_taste(self, soup):
        taste_list = set()
        
        html_tag = soup.find('span', class_='option__label', string='Вкус')
        
        if html_tag:
            parent_row = html_tag.find_parent('tr')
            if parent_row:
                taste_links = parent_row.find_all('a', class_='option__value-item')
                
                for link in taste_links:
                    taste_text = link.text.strip().lower()
                    taste_text = taste_text.rstrip(',')
                    if taste_text:
                        taste_list.add(taste_text)
        
        return list(taste_list)
        
    def get_price(self, soup):
        price_element = soup.select_one('.catalog-card__price-value')
        if price_element:
            price_text = price_element.text.strip()
            numbers = re.findall(r'\d+', price_text)
            return int(numbers[0]) if numbers else 0
        return 0 
    
    def  get_additive(self, url):
        response = self.session.get(url, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')

        additives_list = []

        filter_group = soup.find('div', class_='conteiner_INGREDIENTS')

        if filter_group:
            additive_links = filter_group.find_all('a')
            for link in additive_links:
                additive_name = link.text.strip().lower()
                if additive_name:
                    additives_list.append(additive_name)

        unique_additives = list(set(additives_list))
        return unique_additives

