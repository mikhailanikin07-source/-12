import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class TourApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Туроператор - Управление турами")
        self.root.geometry("1000x600")
        self.root.configure(bg='#f0f0f0')
        
        self.db = None
        self.current_tour_id = None
        
        self.setup_database()
        self.create_widgets()
        self.load_tours()
    
    def setup_database(self):
        """Инициализация базы данных"""
        try:
            from database import Database
            self.db = Database()
        except ImportError as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к базе данных: {str(e)}")
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка веса строк и столбцов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Управление турами", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Поля ввода
        fields = [
            ("Направление:", "destination"),
            ("Страна:", "country"),
            ("Длительность (дни):", "duration_days"),
            ("Цена (руб):", "price"),
            ("Дата начала:", "start_date"),
            ("Туроператор:", "tour_operator"),
            ("Отель:", "hotel_name")
        ]
        
        self.entries = {}
        for i, (label_text, field_name) in enumerate(fields):
            label = ttk.Label(main_frame, text=label_text)
            label.grid(row=i+1, column=0, sticky=tk.W, padx=(0, 10), pady=2)
            
            entry = ttk.Entry(main_frame, width=30)
            entry.grid(row=i+1, column=1, sticky=(tk.W, tk.E), pady=2)
            self.entries[field_name] = entry
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        self.add_button = ttk.Button(button_frame, text="Добавить тур", 
                                   command=self.add_tour)
        self.add_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.update_button = ttk.Button(button_frame, text="Обновить тур", 
                                      command=self.update_tour, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.delete_button = ttk.Button(button_frame, text="Удалить тур", 
                                      command=self.delete_tour, state=tk.DISABLED)
        self.delete_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Очистить", 
                                     command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT)
        
        # Поиск
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=9, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(10, 10))
        self.search_entry.bind('<KeyRelease>', self.search_tours)
        
        # Таблица с турами
        columns = ("ID", "Направление", "Страна", "Дни", "Цена", "Дата начала", 
                  "Туроператор", "Отель")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        column_widths = [50, 120, 100, 50, 80, 100, 120, 150]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, minwidth=50)
        
        self.tree.grid(row=10, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=10, column=4, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Привязка события выбора
        self.tree.bind('<<TreeviewSelect>>', self.on_tour_select)
    
    def add_tour(self):
        """Добавление нового тура"""
        try:
            data = self.get_form_data()
            if not data:
                return
            
            tour_id = self.db.add_tour(**data)
            messagebox.showinfo("Успех", f"Тур успешно добавлен! ID: {tour_id}")
            self.clear_form()
            self.load_tours()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить тур: {str(e)}")
    
    def update_tour(self):
        """Обновление выбранного тура"""
        if not self.current_tour_id:
            messagebox.showwarning("Внимание", "Выберите тур для редактирования")
            return
        
        try:
            data = self.get_form_data()
            if not data:
                return
            
            self.db.update_tour(self.current_tour_id, **data)
            messagebox.showinfo("Успех", "Тур успешно обновлен!")
            self.clear_form()
            self.load_tours()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить тур: {str(e)}")
    
    def delete_tour(self):
        """Удаление выбранного тура"""
        if not self.current_tour_id:
            messagebox.showwarning("Внимание", "Выберите тур для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот тур?"):
            try:
                self.db.delete_tour(self.current_tour_id)
                messagebox.showinfo("Успех", "Тур успешно удален!")
                self.clear_form()
                self.load_tours()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить тур: {str(e)}")
    
    def get_form_data(self):
        """Получение данных из формы с валидацией"""
        destination = self.entries['destination'].get().strip()
        country = self.entries['country'].get().strip()
        duration_days = self.entries['duration_days'].get().strip()
        price = self.entries['price'].get().strip()
        start_date = self.entries['start_date'].get().strip()
        tour_operator = self.entries['tour_operator'].get().strip()
        hotel_name = self.entries['hotel_name'].get().strip()
        
        # Валидация
        if not destination:
            messagebox.showerror("Ошибка", "Введите направление")
            return None
        
        if not country:
            messagebox.showerror("Ошибка", "Введите страну")
            return None
        
        try:
            duration_days = int(duration_days)
            if duration_days <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
            return None
        
        try:
            price = float(price)
            if price <= 0:
                raise ValueError
        except ValueError:

            messagebox.showerror("Ошибка", "Цена должна быть положительным числом")
            return None
        
        if not start_date:
            messagebox.showerror("Ошибка", "Введите дату начала")
            return None
        
        if not tour_operator:
            messagebox.showerror("Ошибка", "Введите туроператора")
            return None
        
        return {
            'destination': destination,
            'country': country,
            'duration_days': duration_days,
            'price': price,
            'start_date': start_date,
            'tour_operator': tour_operator,
            'hotel_name': hotel_name
        }
    
    def load_tours(self):
        """Загрузка туров в таблицу"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        tours = self.db.get_all_tours()
        for tour in tours:
            # Форматирование цены
            formatted_tour = list(tour)
            formatted_tour[4] = f"{tour[4]:.2f} руб"  # Форматируем цену
            self.tree.insert("", tk.END, values=formatted_tour)
    
    def search_tours(self, event=None):
        """Поиск туров"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.load_tours()
            return
        
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        tours = self.db.search_tours(search_term)
        for tour in tours:
            formatted_tour = list(tour)
            formatted_tour[4] = f"{tour[4]:.2f} руб"  # Форматируем цену
            self.tree.insert("", tk.END, values=formatted_tour)
    
    def on_tour_select(self, event):
        """Обработка выбора тура в таблице"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        tour_data = self.tree.item(item)['values']
        
        if tour_data:
            self.current_tour_id = tour_data[0]
            
            # Заполнение формы данными выбранного тура
            self.entries['destination'].delete(0, tk.END)
            self.entries['destination'].insert(0, tour_data[1])
            
            self.entries['country'].delete(0, tk.END)
            self.entries['country'].insert(0, tour_data[2])
            
            self.entries['duration_days'].delete(0, tk.END)
            self.entries['duration_days'].insert(0, tour_data[3])
            
            # Убираем "руб" из цены при редактировании
            price_value = tour_data[4].replace(' руб', '') if 'руб' in str(tour_data[4]) else tour_data[4]
            self.entries['price'].delete(0, tk.END)
            self.entries['price'].insert(0, price_value)
            
            self.entries['start_date'].delete(0, tk.END)
            self.entries['start_date'].insert(0, tour_data[5])
            
            self.entries['tour_operator'].delete(0, tk.END)
            self.entries['tour_operator'].insert(0, tour_data[6])
            
            self.entries['hotel_name'].delete(0, tk.END)
            self.entries['hotel_name'].insert(0, tour_data[7] if len(tour_data) > 7 and tour_data[7] else "")
            
            # Активация кнопок редактирования и удаления
            self.update_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.add_button.config(state=tk.DISABLED)
    
    def clear_form(self):
        """Очистка формы"""
        self.current_tour_id = None
        
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        
        # Сброс выделения в таблице
        self.tree.selection_remove(self.tree.selection())
        

        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.NORMAL)

