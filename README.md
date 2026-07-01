# sklAuto

浙江师范大学「上课啦」自动签到工具。

> 日后闯出祸来，切莫将为师说出来就行了 ^v^

## 功能

- **自动签到**：循环检测签到码变动，自动批量尝试所有签到码完成签到
- **Token 自动刷新**：登录 CAS 认证获取 Bearer Token，过期后自动重新获取
- **课表查询**：查询今日课表 / 本周课表
- **签到记录**：查询个人签到历史记录
- **多用户支持**：通过 `config/json_config.json` 管理多个账号配置
- **MySQL 存储**（可选）：签到结果写入数据库

## 项目结构

```
sklAuto/
├── main.py                 # 入口文件
├── config/
│   ├── base_config.py      # 基础配置（账号、数据库等）
│   ├── json_config.json    # 多用户 JSON 配置
│   └── config.ini          # 运行时配置
├── killer/
│   ├── core.py             # 签到主逻辑调度（sklZJNU）
│   ├── client.py           # HTTP 请求、签到执行、课表/记录查询
│   ├── helper.py           # CAS 登录、密码加密、Token 获取
│   ├── skl.txt             # 签到码字典
│   └── skl_encode.js       # 密码加密 JS（供 PyExecJS 调用）
├── DB/
│   └── mysql.py            # MySQL 封装
├── Model/
│   └── User.py             # 用户数据模型
├── tools/
│   ├── log.py              # 日志配置
│   └── tips.py             # 工具函数
├── logs/                   # 运行日志
└── requirements.txt        # Python 依赖
```

## 环境要求

- Python 3.12+
- Node.js（PyExecJS 依赖 Node 执行密码加密 JS）
- MySQL（可选，用于存储签到记录）

## 安装

```bash
git clone https://github.com/yzzob/sklAuto.git
cd sklAuto

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

## 配置

### 1. 多用户配置（推荐）

编辑 `config/json_config.json`，按以下格式添加用户：

```json
{
  "202211111": {
    "PASSWORD": "your_password",
    "DIFFERENCE": 0,
    "AUTHORIZATION": "Bearer eyJ..."
  }
}
```

| 字段 | 说明 |
|---|---|
| `PASSWORD` | 统一身份认证密码 |
| `DIFFERENCE` | 初始签到差值，程序运行后会自动更新 |
| `AUTHORIZATION` | Bearer Token，首次运行会自动获取并回写 |

### 2. 数据库配置（可选）

编辑 `config/base_config.py` 中的 MySQL 连接信息：

```python
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "your_password"
MYSQL_DATABASE = "your_database"
```

### 3. 其他配置

在 `config/base_config.py` 中还可以调整：

```python
# 运行模式：cycle=循环签到, one=单次签到
RUN_MODEL = "cycle"

# 学期起止日期（用于查询签到统计）
START_DATE = "2025-02-10"
END_DATE = "2025-08-01"
```

## 使用

### 启动自动签到

```bash
python main.py
```

程序会：
1. 从 `json_config.json` 读取用户配置
2. 使用保存的 Token（或自动登录获取新 Token）
3. 循环检测签到状态，发现新签到码时自动批量尝试
4. 每轮间隔约 4~6 秒，Token 过期时自动刷新

### 其他功能

在 `main.py` 中取消注释对应行即可使用：

```python
zjnu = sklZJNU()
zjnu.beforeStart(user_id="202211111")

zjnu.start()                        # 启动循环签到（带自动检测）
zjnu.just_run()                     # 直接循环尝试签到码（不检测变动）
zjnu.obtain_course_schedule_today() # 查询今日课表
zjnu.obtain_course_schedule_week()  # 查询本周课表
zjnu.obtain_check_in_records()      # 查询签到记录
zjnu.test_connection()              # 测试账号连接
zjnu.test_authorization()           # 测试 Token 是否有效
```

## 工作原理

```
┌──────────┐    CAS 登录     ┌───────────────────┐
│  main.py │ ──────────────► │ authserver.zjnu   │
│          │ ◄── Bearer Token ─── .edu.cn        │
│          │                  └───────────────────┘
│          │    检测签到状态    ┌───────────────────┐
│          │ ──────────────► │ skl.zjnu.edu.cn   │
│          │ ◄── 签到码变动 ─── (上课啦平台)      │
│          │                  └───────────────────┘
│          │    批量提交签到码  ┌───────────────────┐
│          │ ──────────────► │ /checkIn/valid-code │
│          │ ◄── 签到结果 ──── │                   │
└──────────┘                  └───────────────────┘
```

1. 通过学校 CAS 统一认证获取 Bearer Token
2. 轮询签到统计接口，检测 `totalCount - rightCount` 是否变化
3. 变化时异步并发尝试 `skl.txt` 中的所有签到码
4. 记录签到成功/过期/失败的结果

## 注意事项

- 登录次数过多会导致账号被临时锁定（约半小时），请合理设置轮询间隔
- `config/json_config.json` 包含账号密码，**请勿提交到公开仓库**
- 首次运行前确保 `logs/` 目录存在，否则日志写入会报错
- 密码加密依赖 Node.js 环境，请确保 `node` 命令可用

## License

MIT
