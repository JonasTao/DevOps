from dataclasses import dataclass
from enum import Enum

class ServerStatus(Enum):
    ONLINE = "在线"
    OFFLINE = "离线"
    CONNECTING = "连接中"
    UNKNOWN = "未知"

@dataclass
class Server:
    id: str
    name: str
    ip: str
    port: int = 22
    username: str = "root"
    password: str = ""
    private_key_path: str = ""
    status: ServerStatus = ServerStatus.UNKNOWN
    description: str = ""
    
    def __repr__(self):
        return f"Server(name={self.name}, ip={self.ip}, status={self.status.value})"
