<h1 align="center">📊 ServerPanel — интерактивная серверная панель</h1>

<p align="center">
  Умная панель мониторинга сервера с авторизацией, графиками и активными соединениями на базе Flask.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python" />
  <img src="https://img.shields.io/badge/Flask-%20microframework-green?style=flat&logo=flask" />
  <img src="https://img.shields.io/badge/OS-Mac%20%7C%20Linux-lightgrey?style=flat" />
  <img src="https://img.shields.io/badge/license-MIT-blue" />
</p>

---

## 🚀 Возможности

- 🔐 Авторизация (Flask-Login + CSRF защита)
- 📈 Мониторинг:
  - Аптайм, ОС, hostname
  - Загрузка CPU, RAM, диск
  - Сетевой трафик (TX/RX)
  - Активные сетевые соединения
- 🌙 Поддержка тёмной и светлой темы
- 🌐 API-эндпоинты `/api/status`, `/api/connections`
- ⚠️ Rate Limiting (Flask-Limiter)
- 🧩 Удобный frontend с автообновлением и графиками

---

## 📷 Скриншоты
![Dashboard Preview](https://user-images.githubusercontent.com/405f4621-fa41-4e5f-aabd-69f061c36c0a.png)

---

## ⚙️ Установка

```bash
# 1. Клонируй проект
git clone https://github.com/your-username/server-panel.git
cd server-panel

# 2. Создай виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# 3. Установи зависимости
pip install -r requirements.txt

# 4. Запусти
python app.py
По умолчанию сервер запускается на http://localhost:5050.

🔐 Авторизация
Логин	Пароль
admin	password

📡 API
/api/status — возвращает JSON с основной системной информацией

/api/metrics — используется для графиков

/api/connections — активные сетевые соединения

🧰 Зависимости
txt
Copy
Edit
Flask
Flask-Login
Flask-WTF
Flask-Limiter
psutil
📁 Структура
csharp
Copy
Edit
server-panel/
│
├── app.py               # Основной Flask-приложение
├── templates/           # HTML-шаблоны (login, dashboard)
├── static/              # CSS/JS
├── requirements.txt     # Зависимости
└── README.md            # Этот файл
🛡 Безопасность
✅ CSRF-защита всех POST-запросов

✅ Ограничение по IP/времени (rate limit)

⚠️ Не предназначено для продакшена без HTTPS и защиты через WSGI сервер (например, Gunicorn + Nginx)

📄 Лицензия
Этот проект распространяется под лицензией MIT.

<h4 align="center">💡 Разработано для изучения, мониторинга и как основа для админки</h4> ```
