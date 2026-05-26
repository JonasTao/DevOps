import paramiko
import socket
from src.core.server import Server, ServerStatus
from src.utils.logger import logger
from src.config.config import Config

class SSHManager:
    def __init__(self):
        self.connections = {}
    
    def connect(self, server: Server) -> bool:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if server.private_key_path:
                private_key = paramiko.RSAKey.from_private_key_file(server.private_key_path)
                ssh.connect(
                    hostname=server.ip,
                    port=server.port,
                    username=server.username,
                    pkey=private_key,
                    timeout=Config.SSH_TIMEOUT
                )
            else:
                ssh.connect(
                    hostname=server.ip,
                    port=server.port,
                    username=server.username,
                    password=server.password,
                    timeout=Config.SSH_TIMEOUT
                )
            
            self.connections[server.id] = ssh
            server.status = ServerStatus.ONLINE
            logger.info(f"成功连接到服务器: {server.name} ({server.ip})")
            return True
            
        except paramiko.AuthenticationException:
            logger.error(f"认证失败: {server.name} ({server.ip})")
            server.status = ServerStatus.OFFLINE
            return False
        except socket.timeout:
            logger.error(f"连接超时: {server.name} ({server.ip})")
            server.status = ServerStatus.OFFLINE
            return False
        except Exception as e:
            logger.error(f"连接失败 {server.name} ({server.ip}): {str(e)}")
            server.status = ServerStatus.OFFLINE
            return False
    
    def disconnect(self, server_id: str):
        if server_id in self.connections:
            try:
                self.connections[server_id].close()
                del self.connections[server_id]
                logger.info(f"断开连接: {server_id}")
            except Exception as e:
                logger.error(f"断开连接失败 {server_id}: {str(e)}")
    
    def execute_command(self, server_id: str, command: str) -> tuple:
        if server_id not in self.connections:
            return False, "未建立连接"
        
        try:
            ssh = self.connections[server_id]
            stdin, stdout, stderr = ssh.exec_command(command, timeout=Config.DEFAULT_TIMEOUT)
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')
            
            if error:
                return False, error
            return True, output
            
        except Exception as e:
            logger.error(f"执行命令失败 {server_id}: {str(e)}")
            return False, str(e)
    
    def is_connected(self, server_id: str) -> bool:
        return server_id in self.connections
    
    def close_all(self):
        for server_id in list(self.connections.keys()):
            self.disconnect(server_id)

ssh_manager = SSHManager()
