import tkinter as tk
from gui import TourApp

def main():
    """Основная функция приложения"""
    try:
        root = tk.Tk()
        app = TourApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")

if __name__ == "__main__":
    main()
