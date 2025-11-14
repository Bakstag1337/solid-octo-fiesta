# 🚀 Quick Start Guide

## Вариант 1: Веб-интерфейс (Рекомендуется)

### Шаг 1: Установка зависимостей

```bash
cd backtesting
pip install --break-system-packages yfinance pandas numpy streamlit plotly
```

### Шаг 2: Запуск приложения

```bash
streamlit run frontend/app.py
```

### Шаг 3: Откройте браузер

Перейдите по адресу: `http://localhost:8501`

### Шаг 4: Использование

1. В левой панели введите тикер (например: **AAPL**)
2. Выберите период: **3 months**
3. Выберите стратегии: **Momentum RSI**, **Mean Reversion**
4. Настройте параметры (или оставьте по умолчанию)
5. Нажмите кнопку **🚀 Run Backtest**

---

## Вариант 2: Быстрый тест без UI

Если у вас проблемы с установкой yfinance или streamlit, можно запустить базовый тест на mock данных:

### Шаг 1: Минимальные зависимости

```bash
pip install --break-system-packages pandas numpy
```

### Шаг 2: Запуск теста

```bash
cd backtesting
python3 test_basic.py
```

Этот тест:
- Генерирует mock данные (90 дней)
- Запускает все 4 стратегии
- Показывает сравнительную таблицу результатов
- Выводит детали первых 5 сделок для каждой стратегии

---

## Вариант 3: Python API

Для программного использования:

```python
from backend.backtester import Backtester

# Создать backtester
bt = Backtester()

# Загрузить данные
success, error = bt.load_data("AAPL", "3 months")

if success:
    # Параметры
    params = {
        'initial_capital': 10000,
        'stop_loss': 2.0,
        'take_profit': 4.0,
        'rsi_period': 14,
        'rsi_buy': 30,
        'rsi_sell': 70
    }

    # Запустить стратегии
    results = bt.run_multiple_strategies(
        ["Momentum RSI", "Mean Reversion"],
        params
    )

    # Получить результаты
    comparison_df = bt.get_comparison_dataframe()
    print(comparison_df)
```

---

## 🎯 Примеры Тикеров

### Популярные акции:
- **AAPL** - Apple
- **TSLA** - Tesla
- **MSFT** - Microsoft
- **GOOGL** - Google
- **AMZN** - Amazon
- **NVDA** - NVIDIA
- **META** - Meta (Facebook)

### ETF:
- **SPY** - S&P 500
- **QQQ** - NASDAQ 100
- **DIA** - Dow Jones

---

## 🔧 Устранение Проблем

### Ошибка установки yfinance

Если не получается установить yfinance (проблемы с multitasking):

```bash
# Используйте вариант 2 с mock данными
python3 test_basic.py
```

### Port 8501 уже занят

```bash
# Используйте другой порт
streamlit run frontend/app.py --server.port 8502
```

### ModuleNotFoundError

```bash
# Проверьте установку
pip list | grep pandas
pip list | grep numpy

# Переустановите если нужно
pip install --break-system-packages --force-reinstall pandas numpy
```

---

## 📊 Что ожидать

После запуска backtesting вы увидите:

1. **Comparison Table** - Сравнительная таблица метрик всех стратегий
2. **Equity Curves** - График роста капитала для каждой стратегии
3. **Metrics Dashboard** - Визуальное сравнение ключевых показателей
4. **Trade History** - Детальная история всех сделок

### Примерные метрики:

```
Strategy          Total Return  Win Rate  Sharpe  Trades
--------------------------------------------------------
Momentum RSI           -0.95%    37.50%   -0.62      16
Mean Reversion         -0.18%     0.00%   -2.10       2
Gap Trading            -0.68%    25.00%   -0.29      24
MACD Crossover         -0.30%    66.67%   -0.39       3
```

**Примечание:** Результаты зависят от выбранного тикера и периода. Отрицательные результаты не означают, что стратегия плохая - возможно нужно подобрать параметры или выбрать другой период/актив.

---

## 🎓 Советы

1. **Начните с популярных акций** - AAPL, MSFT обычно дают стабильные результаты
2. **Тестируйте разные периоды** - Стратегии могут работать по-разному в разных условиях рынка
3. **Сравнивайте стратегии** - Запускайте несколько стратегий одновременно для сравнения
4. **Настраивайте параметры** - Меняйте RSI уровни, stop-loss, take-profit для оптимизации
5. **Смотрите на Sharpe Ratio** - Не только на доходность, но и на риск

---

**Готово! Удачного тестирования! 📈**
