# Модель: Туризм: Розподіл завантаження номерів у готелі (на прикладі Marriott, Hyatt)
# Автор: Антонов В. В., група АІ-235

import numpy as np

class HotelRevenueOptimizer:
    def __init__(self, rooms=200, price=140, penalty=250, mean_demand=210, std_dev=15):
        self.N = rooms          # Кількість номерів у готелі
        self.C = price          # Вартість номера за ніч
        self.W = penalty        # Штраф за відмову у заселенні клієнта
        self.mean_d = mean_demand
        self.std_d = std_dev
        
    def simulate_revenue(self, O, num_simulations=1000):
        """Моделювання очікуваного доходу при заданому рівні овердокінгу O"""
        np.random.seed(42)  # Фіксація для відтворюваності результатів
        demands = np.random.normal(self.mean_d, self.std_d, num_simulations).astype(int)
        
        total_revenue = 0
        total_rejections = 0
        
        for d in demands:
            # Загальна кількість прийнятих бронювань із врахуванням ліміту овердокінгу
            booked = min(d, self.N + O)
            
            # Фактичний заїзд та відмови
            arrivals = min(booked, self.N)
            rejections = max(0, booked - self.N)
            
            # Фінансовий результат дня
            revenue = (self.C * arrivals) - (self.W * rejections)
            total_revenue += revenue
            total_rejections += rejections
            
        avg_revenue = total_revenue / num_simulations
        rejection_rate = (total_rejections / (demands.sum() + 1e-5)) * 100
        return avg_revenue, rejection_rate

    def optimize_gradient_descent(self, start_O=0, lr=0.1, epochs=50):
        """Чисельний метод градієнтного спуску для пошуку оптимального O"""
        O = float(start_O)
        for epoch in range(epochs):
            # Наближене обчислення похідної (чисельне диференціювання)
            rev_current, _ = self.simulate_revenue(int(round(O)))
            rev_next, _ = self.simulate_revenue(int(round(O + 1)))
            
            derivative = rev_next - rev_current
            
            # Рух у напрямку градієнта (максимізація, тому знак +)
            O_new = O + lr * derivative
            O_new = max(0, min(O_new, 50))  # Обмеження розумного ліміту овердокінгу
            
            if abs(O_new - O) < 0.01:
                break
            O = O_new
            
        return int(round(O))

if __name__ == "__main__":
    print("="*65)
    print("  ОПТИМІЗАЦІЯ РІВНЯ ОВЕРДОКІНГУ В НОМЕРНОМУ ФОНДІ ГОТЕЛЮ")
    print("="*65)
    
    optimizer = HotelRevenueOptimizer()
    
    # 1. Базова стратегія (Без овердокінгу, O = 0)
    base_rev, base_reject = optimizer.simulate_revenue(O=0)
    
    # 2. Оптимальна стратегія (Пошук через Градієнтний Спуск)
    optimal_O = optimizer.optimize_gradient_descent()
    opt_rev, opt_reject = optimizer.simulate_revenue(O=optimal_O)
    
    # Виведення результатів
    print(f"{'Стратегія':<25} | {'Сумарний Дохід':<15} | {'Оптимальний O*':<14} | {'Відсоток Відмов'}")
    print("-"*65)
    print(f"{'Базова (O = 0)':<25} | {base_rev:<13,.2f}$ | {0:<14} | {base_reject:.2f}%")
    print(f"{'Оптимальна (GD)':<25} | {opt_rev:<13,.2f}$ | {optimal_O:<14} | {opt_reject:.2f}%")
    print("-"*65)
    print(f"Висновок: Оптимізація за допомогою Градієнтного Спуску збільшила дохід на {opt_rev - base_rev:,.2f}$.")
    print("="*65)