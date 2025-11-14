# 🚀 Deployment Guide - Backtesting Platform

Руководство по развертыванию веб-приложения для backtesting platform.

## 🌐 Streamlit Cloud (Рекомендуется - БЕСПЛАТНО)

Самый простой способ опубликовать приложение в интернете.

### Шаг 1: Подготовка

Все необходимые файлы уже готовы:
- ✅ `requirements.txt` - зависимости
- ✅ `.streamlit/config.toml` - конфигурация
- ✅ `frontend/app.py` - приложение

### Шаг 2: Деплой на Streamlit Cloud

1. **Перейдите на** [share.streamlit.io](https://share.streamlit.io)

2. **Авторизуйтесь через GitHub**

3. **Создайте новое приложение:**
   - Repository: `Bakstag1337/solid-octo-fiesta`
   - Branch: `claude/backtesting-platform-daytrading-01DJkp8GuYBufZYHv9181NRr`
   - Main file path: `backtesting/frontend/app.py`

4. **Нажмите Deploy**

Приложение будет доступно по адресу:
```
https://[your-app-name].streamlit.app
```

### Шаг 3: Поделиться ссылкой

После деплоя вы получите публичную ссылку, которой можно поделиться.

---

## 🐳 Docker (Альтернативный способ)

Для развертывания на собственном сервере или VPS.

### Билд образа

```bash
cd backtesting
docker build -t backtesting-platform .
```

### Запуск контейнера

```bash
docker run -p 8501:8501 backtesting-platform
```

Приложение будет доступно на `http://localhost:8501`

### Docker Compose (опционально)

```bash
docker-compose up -d
```

---

## 🖥️ Локальный запуск

Для локального тестирования:

### Вариант 1: С установкой зависимостей

```bash
cd backtesting
pip install -r requirements.txt
streamlit run frontend/app.py
```

### Вариант 2: Через скрипт (Linux/Mac)

```bash
cd backtesting
chmod +x run.sh
./run.sh
```

### Вариант 3: Через скрипт (Windows)

```cmd
cd backtesting
run.bat
```

---

## ☁️ Другие облачные платформы

### Heroku

1. Создать `Procfile`:
```
web: streamlit run backtesting/frontend/app.py --server.port=$PORT
```

2. Деплой:
```bash
heroku create your-app-name
git push heroku main
```

### Railway.app

1. Подключить GitHub репозиторий
2. Указать start command:
```
streamlit run backtesting/frontend/app.py
```

### Render.com

1. Создать Web Service
2. Build Command: `pip install -r backtesting/requirements.txt`
3. Start Command: `streamlit run backtesting/frontend/app.py`

---

## 🔧 Конфигурация

### Переменные окружения (опционально)

Можно настроить через `.streamlit/secrets.toml` (для Streamlit Cloud):

```toml
[general]
initial_capital = 10000
default_ticker = "AAPL"
```

### Настройка темы

Редактировать `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#1f77b4"      # Основной цвет
backgroundColor = "#ffffff"    # Цвет фона
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
```

---

## 📊 Мониторинг

### Streamlit Cloud

- Логи доступны в dashboard Streamlit Cloud
- Автоматический перезапуск при ошибках
- Метрики использования в реальном времени

### Docker

Просмотр логов:
```bash
docker logs -f [container-id]
```

Статус контейнера:
```bash
docker stats [container-id]
```

---

## 🚨 Troubleshooting

### Проблема: Недостаточно памяти

**Решение для Streamlit Cloud:**
- Ограничить период данных (использовать "1 month" вместо "1 year")
- Уменьшить количество одновременных стратегий

**Решение для Docker:**
```bash
docker run -m 2g -p 8501:8501 backtesting-platform
```

### Проблема: yfinance не устанавливается

**Решение:**
Использовать точные версии в `requirements.txt`:
```
yfinance==0.2.38
```

### Проблема: Медленная загрузка данных

**Решение:**
- Использовать более короткие периоды
- Тестировать на ликвидных акциях (AAPL, MSFT, SPY)

---

## 📝 Checklist перед деплоем

- [ ] Протестировано локально
- [ ] requirements.txt содержит все зависимости
- [ ] .streamlit/config.toml настроен
- [ ] README.md обновлен
- [ ] Secrets не содержатся в коде
- [ ] Ошибки обрабатываются корректно

---

## 🎯 Рекомендуемые настройки

### Для публичного доступа (Streamlit Cloud)
- Ограничить период данных до 6 месяцев
- Добавить rate limiting для Yahoo Finance
- Включить кэширование результатов

### Для приватного использования (Docker)
- Добавить аутентификацию
- Увеличить лимиты памяти
- Настроить HTTPS

---

## 📱 Мобильная версия

Streamlit автоматически адаптируется под мобильные устройства. Дополнительная настройка не требуется.

---

## 🔗 Полезные ссылки

- [Streamlit Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Docker Hub](https://hub.docker.com)
- [Heroku Documentation](https://devcenter.heroku.com)
- [Railway Documentation](https://docs.railway.app)

---

**Готово к деплою! 🚀**

Рекомендуем начать со Streamlit Cloud - это самый простой и бесплатный вариант.
