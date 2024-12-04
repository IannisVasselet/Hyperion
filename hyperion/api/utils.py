# api/utils.py
import psutil
import paramiko
import subprocess

def get_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
        try:
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'status': proc.info['status'],
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent()
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)

def stop_process(pid):
    try:
        process = psutil.Process(pid)
        process.terminate()
        return True
    except psutil.NoSuchProcess:
        return False

def change_process_priority(pid, priority):
    try:
        process = psutil.Process(pid)
        process.nice(priority)
        return True
    except psutil.NoSuchProcess:
        return False

def get_services():
    services = []
    try:
        # Get service list using systemctl
        output = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--all'])
        for line in output.decode('utf-8').split('\n')[1:-7]:
            if line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0].replace('.service', '')
                    status = parts[2]
                    services.append({
                        'name': name,
                        'status': status
                    })
    except:
        # Fallback to psutil for non-systemd systems
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            if 'service' in proc.info['name']:
                services.append({
                    'name': proc.info['name'],
                    'status': proc.info['status']
                })
    return services

def start_service(service_name):
    try:
        subprocess.check_call(['systemctl', 'start', f'{service_name}.service'])
        return True
    except:
        return False

def stop_service(service_name):
    try:
        subprocess.check_call(['systemctl', 'stop', f'{service_name}.service'])
        return True
    except:
        return False

def restart_service(service_name):
    try:
        subprocess.check_call(['systemctl', 'restart', f'{service_name}.service'])
        return True
    except:
        return False

def get_network_usage():
    network_stats = []
    for interface, stats in psutil.net_io_counters(pernic=True).items():
        network_stats.append({
            'interface': interface,
            'received': stats.bytes_recv,
            'sent': stats.bytes_sent
        })
    return network_stats

def execute_ssh_command(host, port, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=port, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode('utf-8')
    ssh.close()
    return result