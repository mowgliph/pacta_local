import psutil
import platform
from datetime import datetime

def get_system_metrics():
    """
    Recopila métricas del sistema usando psutil
    Retorna un diccionario con información del servidor
    """
    try:
        # Información del CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        # Información de memoria
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_total = round(memory.total / (1024**3), 2)  # GB
        memory_used = round(memory.used / (1024**3), 2)    # GB
        memory_available = round(memory.available / (1024**3), 2)  # GB
        
        # Información del disco
        disk = psutil.disk_usage('/')
        disk_percent = round((disk.used / disk.total) * 100, 1)
        disk_total = round(disk.total / (1024**3), 2)  # GB
        disk_used = round(disk.used / (1024**3), 2)   # GB
        disk_free = round(disk.free / (1024**3), 2)   # GB
        
        # Información de red
        net_io = psutil.net_io_counters()
        bytes_sent = round(net_io.bytes_sent / (1024**2), 2)  # MB
        bytes_recv = round(net_io.bytes_recv / (1024**2), 2)  # MB
        
        # Información del sistema
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        uptime_hours = round(uptime.total_seconds() / 3600, 1)
        
        # Procesos activos
        process_count = len(psutil.pids())
        
        return {
            'cpu': {
                'percent': cpu_percent,
                'count': cpu_count,
                'frequency': round(cpu_freq.current, 2) if cpu_freq else 0
            },
            'memory': {
                'percent': memory_percent,
                'total_gb': memory_total,
                'used_gb': memory_used,
                'available_gb': memory_available
            },
            'disk': {
                'percent': disk_percent,
                'total_gb': disk_total,
                'used_gb': disk_used,
                'free_gb': disk_free
            },
            'network': {
                'bytes_sent_mb': bytes_sent,
                'bytes_recv_mb': bytes_recv
            },
            'system': {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'architecture': platform.architecture()[0],
                'processor': platform.processor(),
                'uptime_hours': uptime_hours,
                'process_count': process_count,
                'boot_time': boot_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
    except Exception as e:
        # En caso de error, retornar valores por defecto
        return {
            'cpu': {'percent': 0, 'count': 0, 'frequency': 0},
            'memory': {'percent': 0, 'total_gb': 0, 'used_gb': 0, 'available_gb': 0},
            'disk': {'percent': 0, 'total_gb': 0, 'used_gb': 0, 'free_gb': 0},
            'network': {'bytes_sent_mb': 0, 'bytes_recv_mb': 0},
            'system': {
                'platform': 'Unknown',
                'platform_version': 'Unknown',
                'architecture': 'Unknown',
                'processor': 'Unknown',
                'uptime_hours': 0,
                'process_count': 0,
                'boot_time': 'Unknown'
            },
            'error': str(e)
        }