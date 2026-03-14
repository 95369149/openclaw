# quark-cloud - 夸克网盘操作 Skill

夸克网盘文件管理工具，支持文件列表、分享链接生成、文件下载。

## 功能

- ✅ 列出指定文件夹的文件列表
- ✅ 生成永久有效的分享链接
- ✅ 下载文件到本地
- ✅ 搜索文件
- ✅ 查看存储空间信息

## 安装

无需额外依赖，仅使用 Python 标准库 + requests：

```bash
pip install requests
```

## 配置

### 获取 Cookie

1. 浏览器打开 https://pan.quark.cn
2. 登录账号
3. 按 F12 打开开发者工具
4. 切换到 Network（网络）标签
5. 刷新页面，找到任意请求
6. 在 Request Headers 中复制完整的 Cookie 值
7. 保存到 `~/.quark_cookie` 文件

**Cookie 示例格式：**
```
__pus=...; __kp=...; __kps=...; __ktd=...; __uid=...; __puus=...
```

### 环境变量（可选）

```bash
export QUARK_COOKIE="your_cookie_here"
```

## 使用方式

### 1. 命令行工具

```bash
# 列出根目录文件
python quark_client.py list

# 列出指定文件夹（需要文件夹 ID）
python quark_client.py list <folder_id>

# 创建永久分享链接
python quark_client.py share <file_id>

# 下载文件到当前目录
python quark_client.py download <file_id>

# 下载文件到指定路径
python quark_client.py download <file_id> /path/to/save

# 搜索文件
python quark_client.py search "关键词"

# 查看存储空间
python quark_client.py info
```

### 2. Python API

```python
from quark_client import QuarkClient

# 初始化客户端（自动从 ~/.quark_cookie 读取）
client = QuarkClient()

# 或手动指定 Cookie
client = QuarkClient(cookie="your_cookie_here")

# 列出根目录文件
result = client.list_files(folder_id="0")
files = result['data']['list']

for item in files:
    print(f"{item['file_name']} - {item['fid']}")

# 创建永久分享链接
share_info = client.create_share(
    file_ids=["file_id_here"],
    expired_type=4,  # 4=永久有效
    passcode="",     # 留空=无密码
)
print(f"分享链接: {share_info['share_url']}")

# 获取下载链接
download_info = client.get_download_url("file_id_here")
print(f"下载地址: {download_info['download_url']}")

# 下载文件到本地
saved_path = client.download_file("file_id_here", "/path/to/save")

# 搜索文件
result = client.search_files("关键词")
files = result['data']['list']

# 查看存储空间
info = client.get_storage_info()
print(f"总容量: {info['total']} 字节")
print(f"已使用: {info['used']} 字节")
```

### 3. OpenClaw Agent 集成

```python
# 在 Agent 中使用
exec: cd /Users/apple/.openclaw/workspace/skills/quark-cloud && python quark_client.py list

# 创建分享链接
exec: cd /Users/apple/.openclaw/workspace/skills/quark-cloud && python quark_client.py share <file_id>

# 下载文件
exec: cd /Users/apple/.openclaw/workspace/skills/quark-cloud && python quark_client.py download <file_id> /tmp/
```

## API 参考

### QuarkClient 类

#### `__init__(cookie=None, cookie_file=None)`
初始化客户端
- `cookie`: Cookie 字符串
- `cookie_file`: Cookie 文件路径（默认 `~/.quark_cookie`）

#### `list_files(folder_id="0", page=1, size=100)`
列出文件夹内容
- `folder_id`: 文件夹 ID（"0" 为根目录）
- `page`: 页码（从 1 开始）
- `size`: 每页数量
- 返回: 文件列表数据

#### `create_share(file_ids, expired_type=2, passcode="", title="")`
创建分享链接
- `file_ids`: 文件 ID 列表
- `expired_type`: 过期类型
  - `1` = 1天
  - `2` = 7天
  - `3` = 30天
  - `4` = 永久
  - `5` = 自定义
- `passcode`: 提取码（留空则无密码）
- `title`: 分享标题
- 返回: 分享信息（share_id, share_url, passcode）

#### `get_download_url(file_id)`
获取文件下载链接
- `file_id`: 文件 ID
- 返回: 下载信息（download_url, file_name, size）

#### `download_file(file_id, save_path, chunk_size=8192)`
下载文件到本地
- `file_id`: 文件 ID
- `save_path`: 保存路径（文件夹或完整文件路径）
- `chunk_size`: 下载块大小
- 返回: 保存的文件路径

#### `search_files(keyword, page=1, size=50)`
搜索文件
- `keyword`: 搜索关键词
- `page`: 页码
- `size`: 每页数量
- 返回: 搜索结果

#### `get_storage_info()`
获取存储空间信息
- 返回: 存储信息（total, used, remain）

## 常见问题

### Q: Cookie 过期怎么办？
A: 重新从浏览器获取 Cookie 并更新 `~/.quark_cookie` 文件。

### Q: 如何获取文件 ID？
A: 使用 `list` 命令查看文件列表，输出中会显示每个文件的 ID。

### Q: 分享链接有效期多久？
A: 使用 `expired_type=4` 创建永久有效的分享链接。

### Q: 下载速度慢怎么办？
A: 夸克网盘的下载速度取决于账号等级和网络环境，建议使用会员账号。

### Q: 支持批量操作吗？
A: `create_share` 支持传入多个文件 ID 创建批量分享。下载需要循环调用。

## 注意事项

1. **Cookie 安全**: Cookie 包含账号凭证，请妥善保管，不要泄露
2. **API 限制**: 夸克网盘可能有 API 调用频率限制，避免短时间大量请求
3. **Cookie 有效期**: Cookie 会过期，需要定期更新
4. **仅供学习**: 本工具仅供学习和个人使用，请遵守夸克网盘服务条款

## 参考资料

- [lich0821/QuarkPan](https://github.com/lich0821/QuarkPan) - 夸克网盘 Python 客户端
- [Cp0204/quark-auto-save](https://github.com/Cp0204/quark-auto-save) - 自动转存工具

## 更新日志

### v1.0.0 (2026-03-12)
- ✅ 初始版本
- ✅ 支持文件列表、分享链接、下载
- ✅ 支持搜索和存储信息查询
- ✅ 命令行工具和 Python API
