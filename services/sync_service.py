"""
数据同步服务 - 从高德地图API拉取景点和美食数据
"""

import requests
from typing import List, Dict, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

from config import settings

class DataSyncService:
    """数据同步服务"""
    
    def __init__(self):
        self.api_key = settings.AMAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3/place/text"
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def search_poi(self, keywords: str, city: str, page: int = 1) -> Optional[Dict]:
        """搜索POI（兴趣点）"""
        params = {
            "key": self.api_key,
            "keywords": keywords,
            "city": city,
            "offset": 20,  # 每页20条
            "page": page,
            "extensions": "all"
        }
        
        try:
            resp = requests.get(self.base_url, params=params, timeout=10)
            data = resp.json()
            if data.get("status") == "1" and data.get("count") != "0":
                return data
            return None
        except Exception as e:
            print(f"请求高德API失败: {e}")
            return None
    
    def sync_attractions(self, city: str = "北京"):
        """同步景点数据"""
        from models.attraction import Attraction, Base
        Base.metadata.create_all(bind=self.engine)
        
        db = self.SessionLocal()
        try:
            page = 1
            total = 0
            
            while True:
                data = self.search_poi("景点", city, page)
                if not data or "pois" not in data:
                    break
                
                pois = data["pois"]
                if not pois:
                    break
                
                for poi in pois:
                    name = poi.get("name", "")
                    if db.query(Attraction).filter(Attraction.name == name).first():
                        continue  # 已存在则跳过
                    
                    location = poi.get("location", "").split(",")
                    lng, lat = location[0] if len(location) > 0 else "", location[1] if len(location) > 1 else ""
                    
                    # 从biz_ext中提取评分信息
                    biz_ext = poi.get("biz_ext", {}) or {}
                    rating = float(biz_ext.get("rating", "0") or 0)
                    
                    attraction = Attraction(
                        name=name,
                        description=poi.get("address", ""),
                        category=poi.get("type", "").split(";")[0] if poi.get("type") else "",
                        price=0,  # 高德不直接提供门票价格
                        rating=rating,
                        location=f"{city} {poi.get('address', '')}",
                        image_url=poi.get("photos", [{}])[0].get("url", "") if poi.get("photos") else ""
                    )
                    db.add(attraction)
                    total += 1
                
                db.commit()
                page += 1
                time.sleep(0.5)  # 避免触发频率限制
            
            print(f"{city} 同步景点完成，新增{total}条")
            return total
            
        except Exception as e:
            db.rollback()
            print(f"同步景点失败: {e}")
            return 0
        finally:
            db.close()
    
    def sync_foods(self, city: str = "北京"):
        """同步美食数据"""
        from models.food import Food, Base
        Base.metadata.create_all(bind=self.engine)
        
        db = self.SessionLocal()
        try:
            page = 1
            total = 0
            
            keywords_list = ["餐饮", "美食", "餐厅"]
            
            for keyword in keywords_list:
                page = 1
                while True:
                    data = self.search_poi(keyword, city, page)
                    if not data or "pois" not in data:
                        break
                    
                    pois = data["pois"]
                    if not pois:
                        break
                    
                    for poi in pois:
                        name = poi.get("name", "")
                        if db.query(Food).filter(Food.name == name).first():
                            continue
                        
                        types = poi.get("type", "")
                        category = types.split(";")[1] if ";" in types else types.split(";")[0]
                        
                        biz_ext = poi.get("biz_ext", {}) or {}
                        rating = float(biz_ext.get("rating", "0") or 0)
                        
                        food = Food(
                            name=name,
                            restaurant=name,
                            description=poi.get("address", ""),
                            category=category,
                            price=0,
                            rating=rating,
                            location=f"{city} {poi.get('address', '')}",
                            image_url=poi.get("photos", [{}])[0].get("url", "") if poi.get("photos") else "",
                            tags=types.replace(";", ",")
                        )
                        db.add(food)
                        total += 1
                    
                    db.commit()
                    page += 1
                    time.sleep(0.5)
            
            print(f"{city} 同步美食完成，新增{total}条")
            return total
            
        except Exception as e:
            db.rollback()
            print(f"同步美食失败: {e}")
            return 0
        finally:
            db.close()
    
    def sync_all(self, cities: List[str] = None):
        """同步所有城市的数据"""
        if cities is None:
            cities = ["北京", "上海", "广州", "深圳", "成都", "杭州", 
                      "西安", "重庆", "武汉", "南京", "苏州", "三亚",
                      "丽江", "厦门", "青岛", "大连", "长沙", "昆明"]
        
        total_attractions = 0
        total_foods = 0
        
        for city in cities:
            print(f"开始同步 {city}...")
            total_attractions += self.sync_attractions(city)
            total_foods += self.sync_foods(city)
        
        return {"attractions": total_attractions, "foods": total_foods}