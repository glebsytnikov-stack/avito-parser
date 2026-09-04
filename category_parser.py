#!/usr/bin/env python3
"""
Специализированные парсеры для разных категорий Авито
"""

from advanced_parser import AdvancedAvitoParser
from storage import Storage
from models import init_db
import json

class CategoryParser:
    """Парсеры для разных категорий товаров"""
    
    CATEGORIES = {
        'clothes': {
            'name': 'Одежда',
            'url': 'https://www.avito.ru/all/odezhda',
            'fields': ['title', 'price', 'size', 'brand', 'condition']
        },
        'cars': {
            'name': 'Автомобили',
            'url': 'https://www.avito.ru/all/avtomobili',
            'fields': ['title', 'price', 'brand', 'model', 'year', 'mileage', 'body_type']
        },
        'apartments': {
            'name': 'Квартиры',
            'url': 'https://www.avito.ru/all/kvartiry',
            'fields': ['title', 'price', 'rooms', 'area', 'floor', 'address']
        },
        'phones': {
            'name': 'Телефоны',
            'url': 'https://www.avito.ru/all/mobilnye_telefony',
            'fields': ['title', 'price', 'brand', 'model', 'condition', 'memory']
        }
    }
    
    def __init__(self, category='cars', use_browser=True, headless=True):
        """Инициализировать парсер для категории"""
        if category not in self.CATEGORIES:
            raise ValueError(f"Неизвестная категория: {category}")
        
        self.category = category
        self.category_info = self.CATEGORIES[category]
        self.parser = AdvancedAvitoParser(use_browser=use_browser, headless=headless)
        init_db()
    
    def parse_category(self, pages=1, details=True):
        """Парсить категорию товаров"""
        print(f"\n{'='*60}")
        print(f"Парсинг категории: {self.category_info['name']}")
        print(f"URL: {self.category_info['url']}")
        print(f"Количество страниц: {pages}")
        print(f"{'='*60}\n")
        
        all_ads = []
        
        for page in range(1, pages + 1):
            print(f"📄 Страница {page}/{pages}...")
            
            ads = self.parser.parse_listing_page_with_browser(
                self.category_info['url'],
                page=page
            )
            
            if not ads:
                print(f"⚠️  Объявления на странице {page} не найдены")
                break
            
            print(f"✓ Найдено {len(ads)} объявлений")
            
            # Загружать детали если нужно
            if details:
                for i, ad in enumerate(ads, 1):
                    if ad['url']:
                        print(f"  ↳ Загружаем детали {i}/{len(ads)}...")
                        details_data = self.parser.parse_ad_details_with_browser(ad['url'])
                        ad.update(details_data)
            
            all_ads.extend(ads)
        
        print(f"\n✅ Всего спарсено: {len(all_ads)} объявлений\n")
        return all_ads
    
    def save_results(self, ads, format='all', output_name=None):
        """Сохранить результаты в разных форматах"""
        if output_name is None:
            output_name = f"{self.category}_ads"
        
        if format in ['db', 'all']:
            Storage.save_to_db(ads)
            print(f"✓ Сохранено в БД")
        
        if format in ['csv', 'all']:
            Storage.save_to_csv(ads, f'{output_name}.csv')
            print(f"✓ Сохранено в CSV: {output_name}.csv")
        
        if format in ['json', 'all']:
            Storage.save_to_json(ads, f'{output_name}.json')
            print(f"✓ Сохранено в JSON: {output_name}.json")
    
    def close(self):
        """Закрыть браузер"""
        self.parser.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def parse_clothes(pages=2, headless=True):
    """Парсить одежду"""
    print("\n👔 ПАРСИНГ ОДЕЖДЫ")
    with CategoryParser('clothes', headless=headless) as parser:
        ads = parser.parse_category(pages=pages, details=True)
        parser.save_results(ads, format='all', output_name='clothes')
        
        # Показать статистику
        print_statistics(ads, 'Одежда')
        return ads


def parse_cars(pages=2, headless=True):
    """Парсить автомобили"""
    print("\n🚗 ПАРСИНГ АВТОМОБИЛЕЙ")
    with CategoryParser('cars', headless=headless) as parser:
        ads = parser.parse_category(pages=pages, details=True)
        parser.save_results(ads, format='all', output_name='cars')
        
        # Показать статистику
        print_statistics(ads, 'Автомобили')
        
        # Анализ по брендам
        brands = {}
        for ad in ads:
            if ad.get('title'):
                # Попытка извлечь марку из названия
                title_parts = ad['title'].split()
                if title_parts:
                    brand = title_parts[0]
                    brands[brand] = brands.get(brand, 0) + 1
        
        print("\n📊 Распределение по маркам:")
        for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {brand}: {count}")
        
        return ads


def parse_apartments(pages=2, headless=True):
    """Парсить квартиры"""
    print("\n🏠 ПАРСИНГ КВАРТИР")
    with CategoryParser('apartments', headless=headless) as parser:
        ads = parser.parse_category(pages=pages, details=True)
        parser.save_results(ads, format='all', output_name='apartments')
        
        # Показать статистику
        print_statistics(ads, 'Квартиры')
        
        # Анализ по локации
        locations = {}
        for ad in ads:
            if ad.get('location'):
                locations[ad['location']] = locations.get(ad['location'], 0) + 1
        
        print("\n📊 Топ локаций:")
        for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {location}: {count}")
        
        return ads


def parse_phones(pages=2, headless=True):
    """Парсить телефоны"""
    print("\n📱 ПАРСИНГ ТЕЛЕФОНОВ")
    with CategoryParser('phones', headless=headless) as parser:
        ads = parser.parse_category(pages=pages, details=True)
        parser.save_results(ads, format='all', output_name='phones')
        
        # Показать статистику
        print_statistics(ads, 'Телефоны')
        
        # Анализ по брендам
        brands = {}
        for ad in ads:
            if ad.get('title'):
                title_parts = ad['title'].split()
                if title_parts:
                    brand = title_parts[0]
                    brands[brand] = brands.get(brand, 0) + 1
        
        print("\n📊 Топ производителей:")
        for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  {brand}: {count}")
        
        return ads


def print_statistics(ads, category_name):
    """Вывести статистику по объявлениям"""
    print(f"\n📈 Статистика по {category_name}:")
    
    # Количество
    print(f"  Всего объявлений: {len(ads)}")
    
    # Цены
    prices = [ad.get('price') for ad in ads if ad.get('price')]
    if prices:
        prices = [p for p in prices if isinstance(p, (int, float))]
        if prices:
            print(f"  Минимальная цена: {min(prices):.0f} руб")
            print(f"  Максимальная цена: {max(prices):.0f} руб")
            print(f"  Средняя цена: {sum(prices)/len(prices):.0f} руб")
    
    # Проверенные продавцы
    verified = sum(1 for ad in ads if ad.get('is_verified'))
    print(f"  От проверенных: {verified}")
    
    # С телефонами
    with_phones = sum(1 for ad in ads if ad.get('phone'))
    print(f"  С номером телефона: {with_phones}")


def parse_all(pages=1, headless=True):
    """Парсить все категории"""
    print("\n" + "="*60)
    print("ПОЛНЫЙ ПАРСИНГ ВСЕ КАТЕГОРИИ")
    print("="*60)
    
    results = {
        'clothes': parse_clothes(pages, headless),
        'cars': parse_cars(pages, headless),
        'apartments': parse_apartments(pages, headless),
        'phones': parse_phones(pages, headless)
    }
    
    # Общая статистика
    print("\n" + "="*60)
    print("ОБЩАЯ СТАТИСТИКА")
    print("="*60)
    for category, ads in results.items():
        print(f"{CategoryParser.CATEGORIES[category]['name']}: {len(ads)} объявлений")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python category_parser.py [clothes|cars|apartments|phones|all] [pages] [headless]")
        print("\nПримеры:")
        print("  python category_parser.py clothes 2 --headless")
        print("  python category_parser.py cars 3")
        print("  python category_parser.py apartments 1 --no-headless")
        print("  python category_parser.py all 1")
        sys.exit(1)
    
    category = sys.argv[1] if len(sys.argv) > 1 else 'cars'
    pages = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    headless = '--no-headless' not in sys.argv
    
    try:
        if category == 'all':
            parse_all(pages, headless)
        elif category == 'clothes':
            parse_clothes(pages, headless)
        elif category == 'cars':
            parse_cars(pages, headless)
        elif category == 'apartments':
            parse_apartments(pages, headless)
        elif category == 'phones':
            parse_phones(pages, headless)
        else:
            print(f"Неизвестная категория: {category}")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Парсинг прерван пользователем")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
