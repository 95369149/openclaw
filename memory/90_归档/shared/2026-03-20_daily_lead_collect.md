# 每日线索采集报告 2026-03-20

**执行时间**: 2026-03-20 08:30 (Asia/Shanghai)  
**后端状态**: ✅ 在线

## 采集结果

| 平台 | 关键词 | 状态 | 导入 | 跳过 | 备注 |
|------|--------|------|------|------|------|
| ImportYeti | oscillating knife cutter | ✅ 成功 | 10 | 0 | batch: ImportYeti_20260320_0830 |
| ImportYeti | vibrating blade cutting machine | ✅ 成功 | 10 | 0 | batch: ImportYeti_20260320_0830 |
| Apollo | CNC cutting machine | ❌ 失败 | 0 | 0 | 403 Forbidden - API Key 权限问题 |
| Apollo | composite material cutting | ❌ 失败 | 0 | 0 | 403 Forbidden - API Key 权限问题 |

## 汇总

- **总采集**: 20 条
- **成功导入**: 20 条
- **跳过**: 0 条
- **失败任务**: 2 个（Apollo 全部 403）

## 问题记录

Apollo API 返回 403 Forbidden，URL: `https://api.apollo.io/api/v1/mixed_people/search`  
可能原因：API Key 过期、额度耗尽、或账号权限变更。  
**建议**: 登录 Apollo 控制台检查 API Key 状态。
