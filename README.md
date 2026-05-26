# AutoOps - 自动化运维工具

基于 Python 和 PyQt5 的自动化运维工具，提供服务器管理、命令执行、文件传输、任务调度等功能。

## 功能特性

- **服务器管理**: 添加、编辑、删除服务器，支持密码和密钥认证
- **命令执行**: 在远程服务器上执行命令，实时显示输出
- **文件传输**: 本地与远程服务器之间的文件上传下载
- **任务调度**: 创建定时任务，支持一次性和周期性任务
- **日志查看**: 查看应用运行日志，支持过滤和搜索

## 技术栈

- Python 3.x
- PyQt5 - GUI框架
- Paramiko - SSH连接
- Schedule - 任务调度
- Colorlog - 日志美化

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 项目结构

```
.
├── main.py                 # 启动脚本
├── requirements.txt        # 依赖列表
├── logs/                   # 日志目录
└── src/
    ├── __init__.py
    ├── config/             # 配置模块
    │   ├── __init__.py
    │   ├── config.py       # 配置类
    │   └── .env            # 环境变量
    ├── core/               # 核心模块
    │   ├── __init__.py
    │   ├── server.py       # 服务器模型
    │   └── ssh_manager.py  # SSH管理器
    ├── ui/                 # 界面模块
    │   ├── __init__.py
    │   ├── main_window.py      # 主窗口
    │   ├── server_manager.py   # 服务器管理
    │   ├── command_executor.py # 命令执行
    │   ├── file_transfer.py    # 文件传输
    │   ├── task_scheduler.py   # 任务调度
    │   └── log_viewer.py       # 日志查看
    └── utils/              # 工具模块
        ├── __init__.py
        └── logger.py       # 日志工具
```

## 使用说明

1. 启动程序后，在左侧服务器列表中添加或选择服务器
2. 点击"连接"按钮建立SSH连接
3. 在"命令执行"标签页输入命令并执行
4. 使用其他标签页进行文件传输和任务调度

## 注意事项

- 首次使用需确保目标服务器已开启SSH服务
- 建议使用密钥认证方式以提高安全性
- 任务调度功能需要保持程序运行
