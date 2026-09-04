#!/usr/bin/env python3
"""
Примеры использования продвинутого парсера с браузером
"""

from advanced_parser import AdvancedAvitoParser
from parser import AvitoParser
from storage import Storage
from models import init_db

# Пример 1: Парсинг с браузером (обходит JS защиту)
def example_browser_parsing():
    """Парсить с браузером - преодолевает JS защиту"""
    print("=== Пример 1: Парсинг с браузером ===")
    
    init_db()
    
    # Используем контекстный менеджер для автоматического закрытия браузера
    with AdvancedAvitoParser(use_browser=True, headless=False) as parser:
        url = 'https://www.avito.ru/all/avtomobili'
        
        ads = parser.parse_listing_page_with_browser(url, page=1)
        print(f"Найдено {len(ads)} объявлений")
        
        for ad in ads[:3]:
            print(f"- {ad['title']} - {ad['price']} руб.")
        
        Storage.save_to_db(ads)
        print("✓ Сохранено в БД\n")


# Пример 2: Парсинг деталей с браузером
def example_browser_details():
    """Загружать детали через браузер"""
    print("=== Пример 2: Детали с браузером ===")
    
    init_db()
    
    with AdvancedAvitoParser(use_browser=True, headless=True) as parser:
        url = 'https://www.avito.ru/all/mobilnye_telefony'
        
        ads = parser.parse_listing_page_with_browser(url, page=1)
        print(f"Найдено {len(ads)} объявлений")
        
        # Загрузить детали для первых 3
        for i, ad in enumerate(ads[:3]):
            if ad['url']:
                print(f"Загружаем детали {i+1}/3...")
                details = parser.parse_ad_details_with_browser(ad['url'])
                ad.update(details)
                print(f"✓ Загружены детали для: {ad['title']}")
        
        Storage.save_to_csv(ads, 'phones_with_details.csv')
        print("✓ Сохранено в CSV\n")


# Пример 3: Смешанный парсинг (быстро + подробно)
def example_hybrid_parsing():
    """Комбинировать быстрый парсер со случайной загрузкой деталей"""
    print("=== Пример 3: Гибридный парсинг ===")
    
    init_db()
    
    # Быстро парсим списки обычным парсером
    basic_parser = AvitoParser()
    url = 'https://www.avito.ru/all/kvartiry'
    
    all_ads = []
    for page in range(1, 3):
        ads = basic_parser.parse_listing_page(url, page=page)
        all_ads.extend(ads)
    
    print(f"Быстро спарсено {len(all_ads)} объявлений")
    
    # Загружаем детали браузером для случайных объявлений
    import random
    selected_ads = random.sample(all_ads, min(5, len(all_ads)))
    
    with AdvancedAvitoParser(use_browser=True, headless=True) as browser_parser:
        for i, ad in enumerate(selected_ads):
            if ad['url']:
                print(f"Загружаем детали {i+1}/{len(selected_ads)}...")
                details = browser_parser.parse_ad_details_with_browser(ad['url'])
                ad.update(details)
    
    Storage.save_to_db(all_ads)
    Storage.save_to_json(all_ads, 'apartments_hybrid.json')
    print("✓ Сохранено в БД и JSON\n")


# Пример 4: Мониторинг с имитацией поведения
def example_human_like_monitoring():
    """Мониторинг как настоящий человек"""
    print("=== Пример 4: Мониторинг с человеческим поведением ===")
    
    init_db()
    
    with AdvancedAvitoParser(use_browser=True, headless=False) as parser:
        # Случайно выбираем товары для мониторинга
        urls = [
            'https://www.avito.ru/all/mobilnye_telefony?q=iphone',
            'https://www.avito.ru/all/noutbuki',
            'https://www.avito.ru/all/playstation'
        ]
        
        import random
        url = random.choice(urls)
        print(f"Мониторим: {url}")
        
        # Загружаем 2 страницы как обычный пользователь
        all_ads = []
        for page in range(1, 3):
            ads = parser.parse_listing_page_with_browser(url, page=page)
            all_ads.extend(ads)
            print(f"✓ Страница {page} загружена")
        
        # Загружаем детали для некоторых
        selected = random.sample(all_ads, min(3, len(all_ads)))
        for ad in selected:
            if ad['url']:
                parser.parse_ad_details_with_browser(ad['url'])
        
        Storage.save_to_db(all_ads)
        print(f"✓ Мониторинг завершен, сохранено {len(all_ads)} объявлений\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python advanced_examples.py [1|2|3|4]")
        print("1 - Парсинг с браузером")
        print("2 - Загрузка деталей с браузером")
        print("3 - Гибридный парсинг (быстро + подробно)")
        print("4 - Мониторинг с человеческим поведением")
        sys.exit(1)
    
    example_num = sys.argv[1]
    
    if example_num == '1':
        example_browser_parsing()
    elif example_num == '2':
        example_browser_details()
    elif example_num == '3':
        example_hybrid_parsing()
    elif example_num == '4':
        example_human_like_monitoring()
    else:
        print(f"Неизвестный пример: {example_num}")
