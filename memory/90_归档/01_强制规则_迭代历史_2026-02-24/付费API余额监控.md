# 付费 API 余额监控

## 账户信息（2026-02-23 基准）

### mynewapi
- 总充值: $101.95
- 基准已用: $73.73
- 基准余额: $28.22
- 接口: `GET https://api.penguinsaichat.dpdns.org/v1/dashboard/billing/usage`
- Key: `sk-LKKoZH689LbdeSAvMUfoJhIPmWp0G2osPyawiEolgPpAcVzH`

### xjrouter
- 总充值: $250.00
- 基准已用: $1.12
- 基准余额: $248.88
- 接口: `GET http://xjrouter.xyz/v1/dashboard/billing/usage`（需 --noproxy --resolve）
- Key: `sk-cEYiAFgGxqEdDtoXsiMGqcIhz1QAd2fb9wztF3fbNZw3AVTB`

## 计算公式
余额 = 总充值 - (total_usage / 100)

## 告警规则
1. 余额 < 20% 总充值 → 提醒厂长充值
2. 余额 < $10 → 紧急告警
3. 单日消耗 > $5 → 异常告警
4. 请求返回 401/403 → 立即通知（可能已欠费）

## 汇报格式
```
💰 付费 API 日报
mynewapi: 余额 $XX.XX / $101.95（已用 $XX.XX，今日 +$X.XX）
xjrouter: 余额 $XXX.XX / $250.00（已用 $XX.XX，今日 +$X.XX）
```

## 厂长充值后更新
厂长说充了多少，Kitt 更新此文件的"总充值"字段。
