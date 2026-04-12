# 语音转文字流程

## 方法
1. ffmpeg 转 wav：`ffmpeg -i input.ogg -ar 16000 -ac 1 /tmp/voice.wav -y`
2. whisper tiny 转录：
```python
import whisper
model = whisper.load_model('tiny')
result = model.transcribe('/tmp/voice.wav', language='zh')
print(result['text'])
```

## 注意
- 模型：tiny（已缓存，72MB），够用
- base（139MB）下载太慢，不用
- CPU 模式，FP32，单条语音约 5-10 秒
