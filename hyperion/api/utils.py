# api/utils.py
import psutil

def get_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        processes.append({
            'pid': proc.info['pid'],
            'name': proc.info['name'],
            'status': proc.info['status']
        })
    return processes

def get_services():
    services = []
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        if 'systemd' in proc.info['name'] or 'service' in proc.info['name']:
            services.append({
                'name': proc.info['name'],
                'status': proc.info['status']
            })
    return services