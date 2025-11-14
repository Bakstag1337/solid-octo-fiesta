# 📈 Backtesting Platform для Дейтрейдинг Стратегий

Профессиональный инструмент для тестирования торговых стратегий на исторических данных акций. Позволяет понять, какая стратегия лучше работает на конкретном активе до торговли на реальные деньги.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.31-red.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## 🌐 Быстрый старт - Веб-версия

**Вариант 1: Опубликовать на Streamlit Cloud (БЕСПЛАТНО)**

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

1. Перейти на [share.streamlit.io](https://share.streamlit.io)
2. Авторизоваться через GitHub
3. Указать:
   - Repository: `Bakstag1337/solid-octo-fiesta`
   - Branch: `claude/backtesting-platform-daytrading-01DJkp8GuYBufZYHv9181NRr`
   - Main file: `backtesting/frontend/app.py`
4. Получить публичную ссылку для доступа

**Вариант 2: Запустить локально**

```bash
cd backtesting
chmod +x run.sh
./run.sh
```

Откроется в браузере: `http://localhost:8501`

📖 **Подробнее:** [DEPLOYMENT.md](DEPLOYMENT.md)

## ✨ Возможности

### 📊 Торговые Стратегии

Платформа включает 4 ready-to-use торговые стратегии:

1. **Momentum RSI** - Покупка при перепроданности (RSI < 30), продажа при перекупленности (RSI > 70)
2. **Mean Reversion** - Торговля на отскоке от границ Bollinger Bands
3. **Gap Trading** - Торговля на gap-up открытиях с целью заполнения гэпа на 50%
4. **MACD Crossover** - Торговля на пересечениях MACD линии и сигнальной линии

### 📈 Метрики Производительности

- **Total Return** - Общая доходность в %
- **Win Rate** - Процент прибыльных сделок
- **Sharpe Ratio** - Доходность с учетом риска
- **Max Drawdown** - Максимальная просадка
- **Profit Factor** - Отношение прибыльных к убыточным сделкам
- **Avg Win/Loss** - Средняя прибыль/убыток на сделку

### 🎯 Особенности

- ✅ Одновременное тестирование нескольких стратегий
- ✅ Сравнительный анализ с таблицами и графиками
- ✅ Интерактивные equity curves (кривые роста капитала)
- ✅ Детальная история всех сделок
- ✅ Настраиваемые параметры риск-менеджмента
- ✅ Intraday правила (закрытие позиций в конце дня)
- ✅ Stop Loss и Take Profit
- ✅ Экспорт результатов в CSV
- ✅ Веб-интерфейс на Streamlit

## 🚀 Установка

### Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)

### Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/Bakstag1337/solid-octo-fiesta.git
cd solid-octo-fiesta/backtesting

# Установить зависимости
pip install -r requirements.txt

# Запустить веб-приложение
streamlit run frontend/app.py
```

Откройте браузер по адресу: `http://localhost:8501`

### Альтернатива: Базовый тест без UI

Для быстрой проверки функциональности без веб-интерфейса:

```bash
# Установить минимальные зависимости
pip install pandas numpy

# Запустить базовый тест
python test_basic.py
```

## 💡 Использование

### Веб-интерфейс (Streamlit)

1. **Выберите тикер акции** - Введите символ (например: AAPL, TSLA, MSFT, SPY)
2. **Выберите период** - 1 месяц / 3 месяца / 6 месяцев / 1 год
3. **Выберите стратегии** - Одну или несколько для сравнения
4. **Настройте параметры**:
   - Stop Loss (по умолчанию 2%)
   - Take Profit (по умолчанию 4%)
   - RSI период (по умолчанию 14)
   - RSI уровни покупки/продажи (30/70)
5. **Запустите тест** - Нажмите кнопку "Run Backtest"

### Программный интерфейс (Python API)

```python
from backend.backtester import Backtester

# Создать экземпляр
backtester = Backtester()

# Загрузить данные
success, error = backtester.load_data("AAPL", "3 months")

if success:
    # Настроить параметры
    params = {
        'initial_capital': 10000,
        'stop_loss': 2.0,
        'take_profit': 4.0,
        'rsi_period': 14,
        'rsi_buy': 30,
        'rsi_sell': 70
    }

    # Запустить несколько стратегий
    strategies = ["Momentum RSI", "Mean Reversion", "MACD Crossover"]
    results = backtester.run_multiple_strategies(strategies, params)

    # Получить таблицу сравнения
    comparison_df = backtester.get_comparison_dataframe()
    print(comparison_df)

    # Получить детали сделок
    trades_df = backtester.get_trades_dataframe("Momentum RSI")
    print(trades_df)
```

## 📚 Структура Проекта

```
backtesting/
├── backend/                    # Бэкенд логика
│   ├── strategies/            # Торговые стратегии
│   │   ├── base_strategy.py   # Базовый класс
│   │   ├── momentum_rsi.py    # RSI стратегия
│   │   ├── mean_reversion.py  # Mean Reversion
│   │   ├── gap_trading.py     # Gap Trading
│   │   └── macd_crossover.py  # MACD Crossover
│   ├── backtester.py          # Главный движок
│   ├── metrics.py             # Расчет метрик
│   └── data_loader.py         # Загрузка данных
├── frontend/                   # Веб-интерфейс
│   ├── app.py                 # Streamlit приложение
│   └── components/
│       └── charts.py          # Графики и визуализация
├── test_basic.py              # Базовый тест
├── requirements.txt           # Зависимости
└── README.md                  # Документация
```

## 🎮 Примеры

### Пример 1: Тест одной стратегии

```python
from backend.strategies import MomentumRSI
from backend.data_loader import DataLoader
from backend.metrics import MetricsCalculator

# Загрузить данные
loader = DataLoader()
success, data, error = loader.load_data("AAPL", "3 months")

if success:
    # Создать стратегию
    strategy = MomentumRSI(initial_capital=10000)
    strategy.set_params(rsi_period=14, rsi_oversold=30, rsi_overbought=70)

    # Запустить бэктест
    results = strategy.backtest(data, stop_loss=2.0, take_profit=4.0)

    # Рассчитать метрики
    metrics = MetricsCalculator.calculate_all_metrics(
        initial_capital=10000,
        final_capital=results['final_capital'],
        trades=results['trades'],
        equity_curve=results['equity_curve']
    )

    print(f"Total Return: {metrics['Total Return (%)']:.2f}%")
    print(f"Win Rate: {metrics['Win Rate (%)']:.2f}%")
    print(f"Total Trades: {metrics['Total Trades']}")
```

### Пример 2: Сравнение всех стратегий

```bash
# Запустить веб-приложение
streamlit run frontend/app.py

# В браузере:
# 1. Тикер: AAPL
# 2. Период: 3 months
# 3. Стратегии: Выбрать все 4
# 4. Нажать "Run Backtest"
```

## 🔧 Конфигурация

### Параметры Риск-Менеджмента

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| Initial Capital | $10,000 | Начальный капитал |
| Stop Loss | 2% | Автоматический стоп-лосс |
| Take Profit | 4% | Автоматический тейк-профит |
| Position Size | 100% | Размер позиции от капитала |

### Параметры Стратегий

**Momentum RSI:**
- RSI Period: 14
- RSI Oversold: 30
- RSI Overbought: 70

**Mean Reversion:**
- Bollinger Bands Period: 20
- Standard Deviations: 2

**Gap Trading:**
- Gap Threshold: 1%
- Gap Fill Target: 50%

**MACD Crossover:**
- Fast Period: 12
- Slow Period: 26
- Signal Period: 9

## 📊 Результаты

Платформа предоставляет три уровня детализации:

### 1. Overview (Обзор)
- Сравнительная таблица всех стратегий
- Dashboard с ключевыми метриками
- Equity curves comparison (сравнение кривых роста)

### 2. Strategy Details (Детали стратегии)
- Индивидуальные метрики
- Equity curve
- Статистика сделок

### 3. Trade History (История сделок)
- Полный список всех сделок
- Даты входа/выхода
- Цены и P&L
- Причины закрытия позиций
- Экспорт в CSV

## ⚙️ Правила Торговли

### Intraday Trading Rules

1. **Все сделки внутри дня** - Позиции открываются и закрываются в тот же торговый день
2. **Автоматическое закрытие** - Если позиция не закрылась по сигналу до конца дня, она закрывается принудительно
3. **Одна позиция** - Не открываем новую позицию пока не закрыли текущую
4. **100% капитала** - Весь капитал идет в одну сделку (без leverage)

### Risk Management

1. **Stop Loss** - Автоматическое закрытие при убытке (по умолчанию -2%)
2. **Take Profit** - Автоматическое закрытие при прибыли (по умолчанию +4%)
3. **Защита капитала** - Нельзя открыть позицию если недостаточно капитала

## 🎯 Критерии Приемки

- ✅ Пользователь может запустить одну стратегию на AAPL за 3 месяца и увидеть результаты
- ✅ Пользователь может запустить все 4 стратегии одновременно и увидеть сравнение
- ✅ Таблица сравнения показывает все ключевые метрики корректно
- ✅ Equity curves отображаются на одном графике для сравнения
- ✅ Можно посмотреть детали по каждой сделке (даты, цены, результат)
- ✅ Параметры RSI, stop-loss, take-profit можно менять и перезапускать тест
- ✅ При ошибке (неверный тикер, нет данных) показываем понятное сообщение

## 🚫 Out of Scope

Следующие функции НЕ реализованы в текущей версии:

- ❌ Реальная торговля через API брокера
- ❌ Учет комиссий и slippage
- ❌ Позиции overnight (переносы на следующий день)
- ❌ Оптимизация параметров (перебор значений)
- ❌ Сохранение истории бэктестов
- ❌ Multiple timeframes (только дневные данные)
- ❌ Короткие позиции (short selling)

## 🐛 Устранение Неполадок

### Ошибка: ModuleNotFoundError

```bash
# Убедитесь что все зависимости установлены
pip install -r requirements.txt
```

### Ошибка: No data available for ticker

- Проверьте правильность тикера (должен существовать на Yahoo Finance)
- Попробуйте другой период
- Проверьте интернет-соединение

### Streamlit не запускается

```bash
# Установите Streamlit отдельно
pip install streamlit

# Запустите с явным указанием Python
python -m streamlit run frontend/app.py
```

## 📈 Roadmap

Планируемые улучшения:

- [ ] Поддержка криптовалют
- [ ] Учет комиссий брокера
- [ ] Оптимизация параметров (Grid Search)
- [ ] Поддержка своих кастомных стратегий
- [ ] API для интеграции
- [ ] Backtesting на минутных данных
- [ ] Поддержка short позиций
- [ ] ML-based стратегии

## 🤝 Вклад в Проект

Приветствуются pull requests! Для значительных изменений сначала откройте issue для обсуждения.

## 📜 Лицензия

MIT License - используйте свободно!

## ⚠️ Disclaimer

**Это образовательный инструмент. Не является финансовым советом.**

- Прошлая доходность не гарантирует будущих результатов
- Торговля на финансовых рынках несет риск потери капитала
- Используйте на свой страх и риск
- Проводите собственные исследования перед реальной торговлей

## 👨‍💻 Автор

Создано для трейдеров, которые хотят протестировать свои идеи перед реальной торговлей.

## 🙏 Благодарности

- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance API
- [Streamlit](https://streamlit.io/) - Веб-фреймворк
- [Plotly](https://plotly.com/) - Графики и визуализация
- [pandas](https://pandas.pydata.org/) - Анализ данных

---

**Удачной торговли! 📈💰**
