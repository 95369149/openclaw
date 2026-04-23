# 夸克网盘 Skill 开发完成

**任务**: 写一个夸克网盘操作 skill  
**完成时间**: 2026-03-12 09:25  
**执行者**: deep

## 交付物

### 1. 核心代码

**文件**: `/Users/apple/.openclaw/workspace/skills/quark-cloud/quark_client.py`

**功能实现**:

- ✅ 列出指定文件夹的文件列表（`list_files`）
- ✅ 生成永久有效的分享链接（`create_share`，expired_type=4）
- ✅ 下载文件到本地（`download_file`，带进度显示）
- ✅ 搜索文件（`search_files`）
- ✅ 查看存储空间信息（`get_storage_info`）

**技术特点**:

- 纯 requests 库实现，无外部 SDK 依赖
- 支持 Cookie 登录（文件或字符串）
- 代码简洁，注释清晰
- 完整的错误处理和进度显示

### 2. 使用文档

**文件**: `/Users/apple/.openclaw/workspace/skills/quark-cloud/SKILL.md`

**内容包含**:

- 功能说明
- 安装配置（Cookie 获取方法）
- 三种使用方式：命令行工具、Python API、OpenClaw Agent 集成
- 完整的 API 参考文档
- 常见问题解答
- 注意事项

### 3. 命令行工具

支持以下命令：

```bash
python quark_client.py list [folder_id]           # 列出文件
python quark_client.py share <file_id>            # 创建分享（永久）
python quark_client.py download <file_id> [path]  # 下载文件
python quark_client.py search <keyword>           # 搜索文件
python quark_client.py info                       # 存储信息
```

## 核心实现

### API 端点

- 文件列表: `GET /1/clouddrive/file/sort`
- 创建分享: `POST /1/clouddrive/share`
- 下载链接: `POST /1/clouddrive/file/download`
- 搜索文件: `POST /1/clouddrive/file/search`
- 存储信息: `GET /1/clouddrive/capacity/growth/info`

### Cookie 管理

- 支持从 `~/.quark_cookie` 文件读取
- 支持直接传入 Cookie 字符串
- 自动解析并设置到 requests.Session

### 分享链接

- 默认创建永久有效链接（expired_type=4）
- 支持设置提取码
- 返回完整的分享 URL

### 文件下载

- 流式下载，支持大文件
- 实时进度显示
- 自动创建目录

## 参考资料

基于以下开源项目的 API 分析：

1. **lich0821/QuarkPan**: 完整的夸克网盘 Python 客户端
2. **Cp0204/quark-auto-save**: 自动转存工具

## 使用示例

### Python API

```python
from quark_client import QuarkClient

client = QuarkClient()

# 列出文件
files = client.list_files()

# 创建永久分享
share = client.create_share(["file_id"], expired_type=4)
print(share['share_url'])

# 下载文件
client.download_file("file_id", "/tmp/")
```

### 命令行

```bash
# 列出根目录
python quark_client.py list

# 创建分享
python quark_client.py share abc123

# 下载文件
python quark_client.py download abc123 /tmp/
```

## 注意事项

1. **Cookie 获取**: 需要从浏览器开发者工具中手动获取
2. **API 限制**: 避免高频调用，防止触发风控
3. **Cookie 有效期**: 需要定期更新
4. **仅供学习**: 遵守夸克网盘服务条款

## 状态

✅ **已完成**，所有需求已实现，代码已测试通过逻辑验证。
