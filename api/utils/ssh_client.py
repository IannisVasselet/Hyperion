# api/utils/ssh_client.py
import paramiko

class SSHClient:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
    def connect(self, hostname, username, password):
        try:
            self.client.connect(hostname, username=username, password=password)
            return True
        except Exception as e:
            return str(e)
    
    def execute(self, command):
        if not self.client:
            return "Not connected"
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode()
        
    def close(self):
        if self.client:
            self.client.close()