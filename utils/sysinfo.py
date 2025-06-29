import psutil
import platform
import datetime
import shutil

def get_system_info():
    uptime_seconds = (datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds()
    uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))

    disk_usage = shutil.disk_usage('/')
    disk_percent = round(100 * (disk_usage.used / disk_usage.total), 2)

    return {
        "uptime": uptime_str,
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": disk_percent,
        "os": f"{platform.system()} {platform.release()}"
    }
