import subprocess
import platform

def check_service_status(service_name):
    system = platform.system()
    try:
        if system == 'Darwin':
            if service_name == 'nginx':
                result = subprocess.run(['brew', 'services', 'list'], capture_output=True, text=True)
                for line in result.stdout.splitlines():
                    if 'nginx' in line:
                        if 'started' in line:
                            return 'active'
                        else:
                            return 'inactive'
                return 'not installed'
            else:
                return 'unknown service'
        else:
            result = subprocess.run(['systemctl', 'is-active', service_name], capture_output=True, text=True)
            status = result.stdout.strip()
            return status
    except Exception as e:
        return f'error: {str(e)}'

def restart_service(service_name):
    system = platform.system()
    try:
        if system == 'Darwin':
            if service_name == 'nginx':
                result = subprocess.run(['brew', 'services', 'restart', service_name],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            else:
                return f"Перезапуск сервиса {service_name} не поддерживается на macOS"
        else:
            result = subprocess.run(['sudo', 'systemctl', 'restart', service_name],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return f"Сервис {service_name} успешно перезапущен."
        else:
            return f"Ошибка: {result.stderr.strip()}"
    except Exception as e:
        return f"Ошибка выполнения команды: {str(e)}"
