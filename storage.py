import csv
import json
from datetime import datetime
from models import Advertisement, get_session, init_db
from logger import logger

class Storage:
    @staticmethod
    def save_to_db(ads):
        """Сохранить объявления в БД"""
        try:
            session = get_session()
            saved_count = 0
            
            for ad in ads:
                # Проверить, есть ли уже такое объявление
                existing = session.query(Advertisement).filter_by(
                    avito_id=ad['avito_id']
                ).first()
                
                if existing:
                    # Обновить существующее
                    for key, value in ad.items():
                        if value is not None:
                            setattr(existing, key, value)
                    logger.debug(f"Обновлено объявлен��е {ad['avito_id']}")
                else:
                    # Добавить новое
                    new_ad = Advertisement(**ad)
                    session.add(new_ad)
                    saved_count += 1
                    logger.debug(f"Добавлено объявление {ad['avito_id']}")
            
            session.commit()
            session.close()
            logger.info(f"Сохранено {saved_count} новых объявлений в БД")
            return saved_count
            
        except Exception as e:
            logger.error(f"Ошибка сохранения в БД: {e}")
            return 0
    
    @staticmethod
    def save_to_csv(ads, filename='avito_ads.csv'):
        """Сохранить объявления в CSV"""
        try:
            if not ads:
                logger.warning("Нет данных для сохранения в CSV")
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=ads[0].keys())
                writer.writeheader()
                writer.writerows(ads)
            
            logger.info(f"Сохранено {len(ads)} объявлений в {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения в CSV: {e}")
    
    @staticmethod
    def save_to_json(ads, filename='avito_ads.json'):
        """Сохранить объявления в JSON"""
        try:
            if not ads:
                logger.warning("Нет данных для сохранения в JSON")
                return
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(ads, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Сохранено {len(ads)} объявлений в {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения в JSON: {e}")
    
    @staticmethod
    def get_all_ads():
        """Получить все объявления из БД"""
        try:
            session = get_session()
            ads = session.query(Advertisement).all()
            session.close()
            return ads
        except Exception as e:
            logger.error(f"Ошибка получения объявлений: {e}")
            return []
    
    @staticmethod
    def search_ads(category=None, price_min=None, price_max=None, location=None):
        """Поиск объявлений по критериям"""
        try:
            session = get_session()
            query = session.query(Advertisement)
            
            if category:
                query = query.filter(Advertisement.category.ilike(f'%{category}%'))
            if price_min:
                query = query.filter(Advertisement.price >= price_min)
            if price_max:
                query = query.filter(Advertisement.price <= price_max)
            if location:
                query = query.filter(Advertisement.location.ilike(f'%{location}%'))
            
            ads = query.all()
            session.close()
            return ads
            
        except Exception as e:
            logger.error(f"Ошибка поиска объявлений: {e}")
            return []
