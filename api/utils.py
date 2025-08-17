# api/utils.py
import os
import shutil
import subprocess
from datetime import datetime
from typing import List, Dict

import netifaces
import paramiko
import psutil

from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger('hyperion.api')

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


def get_file_info(path: str) -> dict:
    """Get file or directory information"""
    try:
        stat = os.stat(path)
        return {
            'path': path,
            'name': os.path.basename(path),
            'type': 'directory' if os.path.isdir(path) else 'file',
            'size': stat.st_size,
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'permissions': oct(stat.st_mode)[-3:],
            'owner': stat.st_uid,
            'group': stat.st_gid
        }
    except (FileNotFoundError, PermissionError):
        return None


def list_directory(path: str) -> List[dict]:
    """List contents of a directory"""
    contents = []
    try:
        # Ensure path is absolute
        abs_path = os.path.abspath(path)
        for item in os.listdir(abs_path):
            item_path = os.path.join(abs_path, item)
            file_info = get_file_info(item_path)
            if file_info:
                contents.append(file_info)
        return contents
    except (FileNotFoundError, PermissionError):
        return []


def move_file(source: str, destination: str) -> bool:
    """Move file or directory"""
    try:
        shutil.move(source, destination)
        return True
    except Exception:
        return False


def delete_file(path: str) -> bool:
    """Delete file or directory"""
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        return True
    except Exception:
        return False


def get_storage_info():
    storage_info = []
    for partition in psutil.disk_partitions(all=False):
        if partition.mountpoint and partition.fstype:
            usage = psutil.disk_usage(partition.mountpoint)
            storage_info.append({
                'device': partition.device,
                'mount_point': partition.mountpoint,
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent_used': usage.percent,
                'fs_type': partition.fstype
            })
    return storage_info

def get_system_temperatures():
    try:
        temps = {}
        
        # CPU Temperature and Usage
        temps['CPU'] = [{
            'label': 'CPU Usage',
            'current': psutil.cpu_percent(),
            'high': 80.0,
            'critical': 90.0,
            'unit': '%'
        }]
        
        # Memory Information
        memory = psutil.virtual_memory()
        temps['Memory'] = [{
            'label': 'Memory Usage',
            'current': memory.percent,
            'high': 80.0,
            'critical': 90.0,
            'unit': '%'
        }]
        
        # Disk Temperatures and Usage
        temps['Storage'] = []
        for partition in psutil.disk_partitions():
            if partition.mountpoint:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    temps['Storage'].append({
                        'label': f'Disk Usage ({partition.mountpoint})',
                        'current': usage.percent,
                        'high': 80.0,
                        'critical': 90.0,
                        'unit': '%'
                    })
                except Exception:
                    continue
        
        # Battery Information
        try:
            battery = psutil.sensors_battery()
            if battery:
                temps['Battery'] = [{
                    'label': 'Battery Level',
                    'current': battery.percent,
                    'high': 20.0,  # Warning when below 20%
                    'critical': 10.0,  # Critical when below 10%
                    'unit': '%'
                }]
        except Exception:
            pass
            
        # Fans Information (if available)
        try:
            fans = psutil.sensors_fans()
            if fans:
                temps['Fans'] = []
                for fan_name, entries in fans.items():
                    for entry in entries:
                        temps['Fans'].append({
                            'label': f'Fan {fan_name}',
                            'current': entry.current,
                            'high': 3000,
                            'critical': 4000,
                            'unit': 'RPM'
                        })
        except Exception:
            pass

        return temps
    except Exception as e:
        print(f"Error retrieving system information: {e}")
        return {}
    
def custom_exception_handler(exc, context):
    """Gestionnaire d'exceptions standardisé pour les API"""
    response = exception_handler(exc, context)
    
    # Si une exception n'est pas gérée par DRF, on la log et on renvoie une réponse 500
    if response is None:
        logger.error(f"Erreur non gérée: {exc}")
        return Response(
            {
                "success": False,
                "error": {
                    "code": "ERROR_500",
                    "message": "Une erreur serveur s'est produite."
                }
            },
            status=500
        )
    
    # Standardisation des réponses d'erreur
    status_code = response.status_code
    error_message = str(exc)
    
    if hasattr(exc, 'detail'):
        error_message = str(exc.detail)
    
    error_data = {
        "success": False,
        "error": {
            "code": f"ERROR_{status_code}",
            "message": error_message,
        }
    }
    
    # Ajouter des détails spécifiques si disponibles
    if hasattr(response, 'data') and isinstance(response.data, dict):
        if 'detail' in response.data:
            error_data['error']['detail'] = response.data['detail']
    
    return Response(error_data, status=status_code)