#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸克网盘 Python 客户端
支持文件列表、分享链接生成、文件下载
"""

import os
import json
import time
import requests
from typing import Optional, Dict, List, Any
from pathlib import Path


class QuarkClient:
    """夸克网盘客户端"""
    
    BASE_URL = "https://drive-pc.quark.cn/1/clouddrive"
    
    def __init__(self, cookie: Optional[str] = None, cookie_file: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            cookie: 夸克网盘 Cookie 字符串
            cookie_file: Cookie 文件路径（默认 ~/.quark_cookie）
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Origin': 'https://pan.quark.cn',
            'Referer': 'https://pan.quark.cn/',
        })
        
        # 加载 Cookie
        self.cookie_file = cookie_file or os.path.expanduser("~/.quark_cookie")
        if cookie:
            self._set_cookie(cookie)
        elif os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'r') as f:
                self._set_cookie(f.read().strip())
        else:
            raise ValueError("需要提供 Cookie 或 Cookie 文件路径")
    
    def _set_cookie(self, cookie: str):
        """设置 Cookie"""
        # 解析 Cookie 字符串
        for item in cookie.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                self.session.cookies.set(key.strip(), value.strip())
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            **kwargs: requests 参数
            
        Returns:
            API 响应 JSON
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            response.raise_for_status()
            
            data = response.json()
            
            # 检查业务状态码
            if data.get('status') != 200 and data.get('code') != 0:
                raise Exception(f"API 错误: {data.get('message', '未知错误')}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"请求失败: {str(e)}")
    
    def list_files(self, folder_id: str = "0", page: int = 1, size: int = 100) -> Dict[str, Any]:
        """
        列出文件夹内容
        
        Args:
            folder_id: 文件夹 ID（0 为根目录）
            page: 页码（从 1 开始）
            size: 每页数量
            
        Returns:
            文件列表数据
        """
        params = {
            'pr': 'ucpro',
            'fr': 'pc',
            'pdir_fid': folder_id,
            '_page': page,
            '_size': size,
            '_fetch_total': 1,
            '_fetch_sub_dirs': 0,
            '_sort': 'file_type:asc,updated_at:desc',
        }
        
        return self._request('GET', '/file/sort', params=params)
    
    def get_file_info(self, file_id: str) -> Dict[str, Any]:
        """
        获取文件详细信息
        
        Args:
            file_id: 文件 ID
            
        Returns:
            文件信息
        """
        params = {
            'pr': 'ucpro',
            'fr': 'pc',
        }
        data = {
            'fids': [file_id]
        }
        
        result = self._request('POST', '/file/info', params=params, json=data)
        
        if result.get('data') and len(result['data']) > 0:
            return result['data'][0]
        
        raise Exception("文件不存在")
    
    def create_share(self, file_ids: List[str], expired_type: int = 2, 
                     passcode: str = "", title: str = "") -> Dict[str, Any]:
        """
        创建分享链接
        
        Args:
            file_ids: 文件 ID 列表
            expired_type: 过期类型（1=1天, 2=7天, 3=30天, 4=永久, 5=自定义）
            passcode: 提取码（留空则无密码）
            title: 分享标题
            
        Returns:
            分享信息（包含 share_id 和 share_url）
        """
        params = {
            'pr': 'ucpro',
            'fr': 'pc',
        }
        
        data = {
            'fid_list': file_ids,
            'expired_type': expired_type,
            'title': title,
            'url_type': 1,
            'passcode': passcode,
        }
        
        result = self._request('POST', '/share', params=params, json=data)
        
        if result.get('data'):
            share_data = result['data']
            # 构造完整分享链接
            share_url = f"https://pan.quark.cn/s/{share_data.get('share_id')}"
            if passcode:
                share_url += f" 提取码: {passcode}"
            
            return {
                'share_id': share_data.get('share_id'),
                'share_url': share_url,
                'passcode': passcode,
                'expired_type': expired_type,
            }
        
        raise Exception("创建分享失败")
    
    def get_download_url(self, file_id: str) -> Dict[str, Any]:
        """
        获取文件下载链接
        
        Args:
            file_id: 文件 ID
            
        Returns:
            下载信息（包含 download_url）
        """
        params = {
            'pr': 'ucpro',
            'fr': 'pc',
        }
        
        data = {
            'fids': [file_id]
        }
        
        result = self._request('POST', '/file/download', params=params, json=data)
        
        if result.get('data') and len(result['data']) > 0:
            file_data = result['data'][0]
            return {
                'file_id': file_id,
                'download_url': file_data.get('download_url'),
                'file_name': file_data.get('file_name'),
                'size': file_data.get('size'),
            }
        
        raise Exception("获取下载链接失败")
    
    def download_file(self, file_id: str, save_path: str, chunk_size: int = 8192) -> str:
        """
        下载文件到本地
        
        Args:
            file_id: 文件 ID
            save_path: 保存路径（文件夹或完整文件路径）
            chunk_size: 下载块大小
            
        Returns:
            保存的文件路径
        """
        # 获取下载链接
        download_info = self.get_download_url(file_id)
        download_url = download_info['download_url']
        file_name = download_info['file_name']
        
        # 确定保存路径
        save_path = Path(save_path)
        if save_path.is_dir():
            save_path = save_path / file_name
        
        # 确保目录存在
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 下载文件
        print(f"开始下载: {file_name}")
        response = requests.get(download_url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    # 显示进度
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r进度: {progress:.1f}% ({downloaded}/{total_size})", end='')
        
        print(f"\n下载完成: {save_path}")
        return str(save_path)
    
    def search_files(self, keyword: str, page: int = 1, size: int = 50) -> Dict[str, Any]:
        """
        搜索文件
        
        Args:
            keyword: 搜索关键词
            page: 页码
            size: 每页数量
            
        Returns:
            搜索结果
        """
        params = {
            'pr': 'ucpro',
            'fr': 'pc',
        }
        
        data = {
            'keyword': keyword,
            '_page': page,
            '_size': size,
            '_fetch_total': 1,
        }
        
        return self._request('POST', '/file/search', params=params, json=data)
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        获取存储空间信息
        
        Returns:
            存储信息（total, used, remain）
        """
        params = {
            'pr': 'ucpro',
            'fr': 'pc',
        }
        
        result = self._request('GET', '/capacity/growth/info', params=params)
        
        if result.get('data'):
            capacity = result['data'].get('cap_composition', {})
            return {
                'total': capacity.get('total', 0),
                'used': capacity.get('used', 0),
                'remain': capacity.get('total', 0) - capacity.get('used', 0),
            }
        
        raise Exception("获取存储信息失败")


def format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def main():
    """命令行工具示例"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python quark_client.py list [folder_id]           # 列出文件")
        print("  python quark_client.py share <file_id>            # 创建分享")
        print("  python quark_client.py download <file_id> [path]  # 下载文件")
        print("  python quark_client.py search <keyword>           # 搜索文件")
        print("  python quark_client.py info                       # 存储信息")
        sys.exit(1)
    
    try:
        client = QuarkClient()
        command = sys.argv[1]
        
        if command == 'list':
            folder_id = sys.argv[2] if len(sys.argv) > 2 else "0"
            result = client.list_files(folder_id)
            
            files = result.get('data', {}).get('list', [])
            print(f"\n共 {len(files)} 个文件/文件夹:\n")
            
            for item in files:
                file_type = "📁" if item.get('dir') else "📄"
                name = item.get('file_name')
                size = format_size(item.get('size', 0))
                fid = item.get('fid')
                print(f"{file_type} {name} ({size}) [ID: {fid}]")
        
        elif command == 'share':
            if len(sys.argv) < 3:
                print("错误: 需要提供文件 ID")
                sys.exit(1)
            
            file_id = sys.argv[2]
            result = client.create_share([file_id], expired_type=4)  # 永久有效
            
            print(f"\n✅ 分享链接创建成功:")
            print(f"链接: {result['share_url']}")
        
        elif command == 'download':
            if len(sys.argv) < 3:
                print("错误: 需要提供文件 ID")
                sys.exit(1)
            
            file_id = sys.argv[2]
            save_path = sys.argv[3] if len(sys.argv) > 3 else "."
            
            client.download_file(file_id, save_path)
        
        elif command == 'search':
            if len(sys.argv) < 3:
                print("错误: 需要提供搜索关键词")
                sys.exit(1)
            
            keyword = sys.argv[2]
            result = client.search_files(keyword)
            
            files = result.get('data', {}).get('list', [])
            print(f"\n找到 {len(files)} 个结果:\n")
            
            for item in files:
                file_type = "📁" if item.get('dir') else "📄"
                name = item.get('file_name')
                size = format_size(item.get('size', 0))
                fid = item.get('fid')
                print(f"{file_type} {name} ({size}) [ID: {fid}]")
        
        elif command == 'info':
            info = client.get_storage_info()
            print(f"\n存储空间:")
            print(f"总容量: {format_size(info['total'])}")
            print(f"已使用: {format_size(info['used'])}")
            print(f"剩余: {format_size(info['remain'])}")
            print(f"使用率: {(info['used'] / info['total'] * 100):.1f}%")
        
        else:
            print(f"未知命令: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
