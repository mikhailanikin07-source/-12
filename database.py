import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='tours.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tours (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT NOT NULL,
                country TEXT NOT NULL,
                duration_days INTEGER NOT NULL,
                price REAL NOT NULL,
                start_date TEXT NOT NULL,
                tour_operator TEXT NOT NULL,
                hotel_name TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_tour(self, destination, country, duration_days, price, start_date, tour_operator, hotel_name):
        """Добавление нового тура"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tours (destination, country, duration_days, price, start_date, tour_operator, hotel_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (destination, country, duration_days, price, start_date, tour_operator, hotel_name))
        
        conn.commit()
        tour_id = cursor.lastrowid
        conn.close()
        return tour_id
    
    def get_all_tours(self):
        """Получение всех туров"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tours ORDER BY start_date
        ''')
        
        tours = cursor.fetchall()
        conn.close()
        return tours
    
    def update_tour(self, tour_id, destination, country, duration_days, price, start_date, tour_operator, hotel_name):
        """Обновление тура"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tours 
            SET destination=?, country=?, duration_days=?, price=?, start_date=?, tour_operator=?, hotel_name=?
            WHERE id=?
        ''', (destination, country, duration_days, price, start_date, tour_operator, hotel_name, tour_id))
        
        conn.commit()
        conn.close()
    
    def delete_tour(self, tour_id):
        """Удаление тура"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tours WHERE id=?', (tour_id,))
        
        conn.commit()
        conn.close()
    
    def search_tours(self, search_term):
        """Поиск туров"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tours 
            WHERE destination LIKE ? OR country LIKE ? OR tour_operator LIKE ? OR hotel_name LIKE ?
            ORDER BY start_date
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        tours = cursor.fetchall()
        conn.close()
        return tours
