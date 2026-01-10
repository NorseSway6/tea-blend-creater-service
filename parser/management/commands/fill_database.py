import json
import logging
from pathlib import Path
from django.core.management.base import BaseCommand
from parser.tea_parser import TeaParser
from main_functionality.models import *
import time
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class Command(BaseCommand):

    def handle(self, *args, **options):
        parser = TeaParser()

        base_url = "https://www.chay.info/catalog/chay/"
        url_list = ["chernyy-chay/", "zelenyy-chay/", "belyy-chay/", "zheltyy-chay/", "ulun/", "pu-er/"]

        for url in url_list:
            catalog_url = urljoin(base_url, url)
            
            tea_cart_urls = parser.tea_cart_parser(catalog_url)
            
            logger.info(f"find {len(tea_cart_urls)} urls")
            
            for i, cart_url in enumerate(tea_cart_urls[:5], 1):
                try:
                    logger.info(f"parsing: [{i}/{len(tea_cart_urls)}]")
                    
                    tea_data = parser.tea_parser(cart_url)
                    
                    if not tea_data or not tea_data.get('name'):
                        logger.warning("skip: no data")
                        continue

                    tea_name = tea_data.get('name', '').lower()
                    if any(keyword in tea_name for keyword in ['сет', 'подписке', 'упаковка', 'набор', "сфера"]):
                        continue
                    
                    tea, _ = BaseTea.objects.update_or_create(
                        name = tea_name,
                        tea_type = tea_data.get('tea_type', ''),
                        making_time = tea_data.get('making_time', 0),
                        temperature = tea_data.get('temperature', 0),
                        price = tea_data.get('price', 0),
                    )

                    tastes_list = tea_data.get('tastes', [])
                    for taste in tastes_list:
                        taste_obj, _ = Taste.objects.update_or_create(name=taste)
                        BaseTeaTaste.objects.update_or_create(tea=tea, taste=taste_obj)
                    
                    if i < len(tea_cart_urls):
                        time.sleep(3)
                        
                except Exception as e:
                    logger.error(f"error: {str(e)}")
                    continue
                
                time.sleep(5)

            logger.info(f"parced from this url: {url}")
        
        self.create_taste_wheel()
        self.bind_tastes_subtastes()
        self.create_themes()

        logger.info("parsing is done")


    def create_taste_wheel(self):
        logger.info("start adding tastes, subtastes and additives")

        file_path = Path(__file__).parent / 'data' / 'taste_wheel.json'

        if not file_path.exists():
            logger.error("file not found")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            taste_wheel = json.load(f)

        for primary_name, subcategories in taste_wheel.items():
            base_taste, _ = BaseTaste.objects.update_or_create(name=primary_name)
            
            for subcategory_name, additives in subcategories.items():
                subtaste, _ = Subtaste.objects.update_or_create(name=subcategory_name, base_taste=base_taste)

                for additive_name in additives:
                    additive_name = additive_name.lower()
                    additive, _ = Additive.objects.update_or_create(name=additive_name)

                    SubtasteAdditive.objects.update_or_create(subtaste=subtaste, additive=additive)

        logger.info("done adding tastes, subtastes and additives")

    def bind_tastes_subtastes(self):
        logger.info("start binding tastes and subtastes")

        tastes = Taste.objects.all()
        subtastes = Subtaste.objects.all()

        for taste in tastes:
            taste_name_lower = taste.name.lower()

            for subtaste in subtastes:
                subtaste_name_lower = subtaste.name.lower()
                
                if subtaste_name_lower in taste_name_lower or taste_name_lower in subtaste_name_lower:
                    TasteSubtaste.objects.get_or_create(taste=taste, subtaste=subtaste)

        logger.info("done binding tastes and subtastes")

    def create_themes(self):
        file_path = Path(__file__).parent / 'data' / 'themes.json'
        
        if not file_path.exists():
            logger.error("file not found")
            return
        
        with open(file_path, 'r', encoding='utf-8') as f:
            themes_data = json.load(f)

        for theme_data in themes_data:
            theme_name = theme_data['name']
            
            theme, _ = Theme.objects.update_or_create(name=theme_name)
            
            for additive_name in theme_data.get('additives', []):
                additive_name_lower = additive_name.lower().strip()
                
                additive = Additive.objects.filter(name=additive_name_lower).first()
                
                if additive:
                    theme.additives.add(additive)
                else:
                    logger.warning("skip: subtaste not found")
                    continue
            
            for subtaste_name in theme_data.get('subtastes', []):
                subtaste_name_clean = subtaste_name.strip()

                subtaste = Subtaste.objects.filter(name=subtaste_name_clean).first()
                
                if subtaste:
                    theme.subtastes.add(subtaste)
                else:
                    logger.warning("skip: subtaste not found")
                    continue
        