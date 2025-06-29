import os
import platform
import psutil
import socket
import subprocess
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = "your_secret_key"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[]
)
limiter.init_app(app)

# дальше остальной код...

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# --- Пользователь (минимально) ---
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# --- Функции для системной информации ---
def get_system_info():
    uptime_seconds = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    users = [user.name for user in psutil.users()]
    net_io = psutil.net_io_counters()

    return {
        'uptime': str(uptime_seconds).split('.')[0],
        'cpu_percent': psutil.cpu_percent(interval=1),
        'ram_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'os': platform.system() + " " + platform.release(),
        'hostname': socket.gethostname(),
        'users': ", ".join(set(users)),
        'processes': len(psutil.pids()),
        'bytes_sent': net_io.bytes_sent,
        'bytes_recv': net_io.bytes_recv
    }


def is_mac():
    return platform.system() == "Darwin"

def get_service_status(service):
    try:
        if is_mac():
            result = subprocess.run(['brew', 'services', 'list'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if line.strip().startswith(service):
                    parts = line.split()
                    if len(parts) > 1 and parts[1] == 'started':
                        return "active"
                    else:
                        return "inactive"
            return "not found"
        else:
            result = subprocess.run(['systemctl', 'is-active', service], capture_output=True, text=True)
            return result.stdout.strip()
    except Exception as e:
        print(f"Ошибка в get_service_status: {e}")
        return "unknown"

def restart_service(service):
    try:
        if is_mac():
            subprocess.run(['brew', 'services', 'restart', service], check=True)
        else:
            subprocess.run(['sudo', 'systemctl', 'restart', service], check=True)
        return True, f"Сервис {service} успешно перезапущен."
    except subprocess.CalledProcessError as e:
        return False, f"Ошибка при перезапуске {service}: {str(e)}"
    except Exception as e:
        return False, f"Неизвестная ошибка: {str(e)}"

# --- Роуты ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "password":
            user = User(id=1)
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Неверное имя пользователя или пароль")
    return render_template("login.html")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def dashboard():
    info = get_system_info()
    nginx_status = get_service_status("nginx")
    return render_template("dashboard.html", info=info, nginx_status=nginx_status)

@app.route("/system_info")
@login_required
def system_info_api():
    info = get_system_info()
    services = ['nginx']
    service_statuses = {srv: get_service_status(srv) for srv in services}
    return jsonify({
        'info': info,
        'services': service_statuses
    })

@app.route("/restart_nginx", methods=["POST"])
@login_required
def restart_nginx():
    success, message = restart_service("nginx")
    flash(message)
    return redirect(url_for("dashboard"))

@app.route('/api/status')
def api_status():
    uptime_seconds = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    info = {
        'uptime': str(uptime_seconds).split('.')[0],
        'cpu_percent': psutil.cpu_percent(),
        'ram_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'os': platform.system() + " " + platform.release(),
        'hostname': socket.gethostname(),
        'users': ", ".join([user.name for user in psutil.users()]),
        'processes': len(psutil.pids())
    }
    return jsonify(info)

@app.route("/api/metrics")
@login_required
def api_metrics():
    info = get_system_info()
    # Получаем топ 5 процессов по CPU
    processes = []
    for pid in psutil.pids():
        try:
            p = psutil.Process(pid)
            processes.append({
                'pid': pid,
                'name': p.name(),
                'cpu': p.cpu_percent(interval=0.1),
                'memory': p.memory_percent()
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    top_cpu = sorted(processes, key=lambda x: x['cpu'], reverse=True)[:5]
    top_mem = sorted(processes, key=lambda x: x['memory'], reverse=True)[:5]

    return jsonify({
        'cpu_percent': info['cpu_percent'],
        'ram_percent': info['ram_percent'],
        'disk_percent': info['disk_percent'],
        'top_cpu': top_cpu,
        'top_mem': top_mem
    })

@app.route("/api/connections")
@login_required
def api_connections():
    return jsonify(get_active_connections())

def get_active_connections():
    connections = []
    for conn in psutil.net_connections(kind="inet"):
        try:
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "-"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"
            pid = conn.pid or "-"
            # При попытке получить имя процесса может быть AccessDenied
            name = "-"
            if pid != "-":
                try:
                    name = psutil.Process(pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    name = "-"
            connections.append({
                'pid': pid,
                'name': name,
                'laddr': laddr,
                'raddr': raddr,
                'status': conn.status
            })
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            # Просто пропускаем соединения без доступа
            continue
        except Exception:
            continue
    return connections


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
