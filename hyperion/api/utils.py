# api/utils.py
import psutil
import paramiko
import subprocess
import socket
import netifaces
from typing import List, Dict

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

def block_ip(ip_address: str) -> bool:
    """Block an IP address using iptables"""
    try:
        subprocess.check_call([
            'sudo', 'iptables', 
            '-A', 'INPUT', 
            '-s', ip_address, 
            '-j', 'DROP'
        ])
        return True
    except subprocess.CalledProcessError:
        return False

def unblock_ip(ip_address: str) -> bool:
    """Unblock a previously blocked IP address"""
    try:
        subprocess.check_call([
            'sudo', 'iptables', 
            '-D', 'INPUT', 
            '-s', ip_address, 
            '-j', 'DROP'
        ])
        return True
    except subprocess.CalledProcessError:
        return False

def block_port(port: int, protocol: str = 'tcp') -> bool:
    """Block a specific port using iptables"""
    try:
        subprocess.check_call([
            'sudo', 'iptables',
            '-A', 'INPUT',
            '-p', protocol,
            '--dport', str(port),
            '-j', 'DROP'
        ])
        return True
    except subprocess.CalledProcessError:
        return False

def get_network_interfaces() -> List[Dict]:
    """Get detailed information about network interfaces"""
    interfaces = []
    for iface in netifaces.interfaces():
        try:
            addrs = netifaces.ifaddresses(iface)
            ipv4 = addrs.get(netifaces.AF_INET, [])
            ipv6 = addrs.get(netifaces.AF_INET6, [])
            
            interface_info = {
                'name': iface,
                'ipv4': [addr['addr'] for addr in ipv4],
                'ipv6': [addr['addr'] for addr in ipv6],
                'is_up': 'up' in psutil.net_if_stats()[iface].flags,
                'speed': psutil.net_if_stats()[iface].speed,
                'mtu': psutil.net_if_stats()[iface].mtu
            }
            interfaces.append(interface_info)
        except Exception:
            continue
    return interfaces

def configure_interface(interface_name: str, config: Dict) -> bool:
    """Configure a network interface"""
    try:
        # Set IP address
        if 'ip_address' in config:
            subprocess.check_call([
                'sudo', 'ip', 'addr', 'add',
                config['ip_address'],
                'dev', interface_name
            ])
        
        # Set MTU
        if 'mtu' in config:
            subprocess.check_call([
                'sudo', 'ip', 'link', 'set',
                interface_name, 'mtu', str(config['mtu'])
            ])
        
        # Set interface up/down
        if 'up' in config:
            action = 'up' if config['up'] else 'down'
            subprocess.check_call([
                'sudo', 'ip', 'link', 'set',
                interface_name, action
            ])
            
        return True
    except subprocess.CalledProcessError:
        return False

def execute_ssh_command(host, port, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port=port, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode('utf-8')
    ssh.close()
    return result