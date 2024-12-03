# api/utils.py
import psutil
import paramiko

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

def execute_ssh_command(host, port, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=port, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode('utf-8')
    ssh.close()
    return result