# Модель: Туризм: Розподіл завантаження номерів у готелі (на прикладі Marriott, Hyatt)
# Автор: Антонов В. В., група АІ-235

import os
import numpy as np
from http.server import BaseHTTPRequestHandler, HTTPServer

# Зчитування змінних середовища Docker (з дефолтними значеннями)
STUDENT_NAME = os.getenv("STUDENT_NAME", "Антонов В. В.")
GROUP_NAME = os.getenv("GROUP", "АІ-235")
MODE = os.getenv("MODE", "comfort")  # Твій варіант: непарний -> comfort

class HotelRevenueOptimizer:
    def __init__(self):
        self.N = 200          # Кількість номерів
        self.mean_d = 210     # Середній попит
        self.std_d = 15       # Відхилення
        
        # Логіка варіанту: змінюємо базові параметри залежно від екологічного чи комфорт режиму
        if MODE.lower() == "comfort":
            self.C = 220      # Вища вартість номера у комфорт-класі
            self.W = 350      # Більший штраф за відмову VIP-клієнту
        else:
            self.C = 140      # Стандартна ціна (режим eco)
            self.W = 250      # Стандартний штраф
        
    def simulate_revenue(self, O, num_simulations=1000):
        np.random.seed(42)
        demands = np.random.normal(self.mean_d, self.std_d, num_simulations).astype(int)
        total_revenue = 0
        total_rejections = 0
        
        for d in demands:
            booked = min(d, self.N + O)
            arrivals = min(booked, self.N)
            rejections = max(0, booked - self.N)
            revenue = (self.C * arrivals) - (self.W * rejections)
            total_revenue += revenue
            total_rejections += rejections
            
        return total_revenue / num_simulations, (total_rejections / (demands.sum() + 1e-5)) * 100

    def optimize_gradient_descent(self):
        O = 0.0
        for _ in range(50):
            rev_current, _ = self.simulate_revenue(int(round(O)))
            rev_next, _ = self.simulate_revenue(int(round(O + 1)))
            derivative = rev_next - rev_current
            O_new = max(0, min(O + 0.1 * derivative, 50))
            if abs(O_new - O) < 0.01: break
            O = O_new
        return int(round(O))

# Створення легковагого вебсервера всередині контейнера
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        
        optimizer = HotelRevenueOptimizer()
        base_rev, base_reject = optimizer.simulate_revenue(O=0)
        optimal_O = optimizer.optimize_gradient_descent()
        opt_rev, opt_reject = optimizer.simulate_revenue(O=optimal_O)
        
        # Формуємо відповідь, яку буде видно в браузері або консолі
        response = f"=== DOCKER CONTAINER ACTIVE ===\n"
        response += f"Модель розгорнув: {STUDENT_NAME}\n"
        response += f"Група: {GROUP_NAME}\n"
        response += f"Контейнеризований режим (Варіант): {MODE.upper()}\n"
        response += "="*50 + "\n"
        response += f"Базова стратегія (O=0):  Дохід = {base_rev:,.2f}$, Відмови = {base_reject:.2f}%\n"
        response += f"Оптимальна (Градієнт): Дохід = {opt_rev:,.2f}$, Оптимальний овердокінг O* = {optimal_O}\n"
        response += f"Ефект чисельної оптимізації: +{opt_rev - base_rev:,.2f}$\n"
        response += "="*50 + "\n"
        
        self.wfile.write(response.encode('utf-8'))

if __name__ == "__main__":
    print(f"[*] Запуск моделі для студента: {STUDENT_NAME} ({GROUP_NAME})")
    print(f"[*] Активовано режим: {MODE}")
    
    server_address = ('0.0.0.0', 5000)
    httpd = HTTPServer(server_address, WebServerHandler)
    print("[+] Сервер успішно запущено у контейнері на порту 5000...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()