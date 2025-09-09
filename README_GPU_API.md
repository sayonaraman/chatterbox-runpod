# 🚀 Chatterbox TTS - GPU Serverless API

**Высокопроизводительный TTS API для RunPod GPU Serverless**

Оптимизированная версия [Chatterbox TTS](https://github.com/resemble-ai/chatterbox) специально для **GPU-only serverless** развертывания на RunPod. Никаких GUI интерфейсов - только мощный API.

## ⚡ Ключевые особенности

- 🎯 **GPU-only**: Оптимизировано для максимальной производительности на GPU
- 🌍 **23 языка**: Включая русский, английский, китайский, японский и др.
- 🎤 **Voice Cloning**: Zero-shot клонирование голоса через base64 аудио
- 📊 **Мониторинг**: Встроенные метрики GPU времени и памяти
- ⚡ **Быстрый старт**: Предзагруженные модели для минимального cold start
- 💰 **Экономичность**: Платите только за GPU время использования

## 🔧 Быстрое развертывание на RunPod

### 1. GitHub Setup
```bash
# Форкните этот репозиторий на GitHub
# GitHub Actions автоматически соберет Docker образ
```

### 2. RunPod Serverless Endpoint
```
Container Image: ghcr.io/your-username/chatterbox-runpod:latest
GPU: RTX 4090 / A100 (рекомендуется)
Memory: 16GB+
Container Disk: 25GB+
Min Workers: 0
Idle Timeout: 5 секунд
```

### 3. Готово! 🎉

## 📡 API Использование

### Python SDK
```python
import runpod
import base64

runpod.api_key = "YOUR_API_KEY"
endpoint = runpod.Endpoint("YOUR_ENDPOINT_ID")

# Английский TTS
response = endpoint.run({
    "text": "Hello world! This is GPU-powered Chatterbox TTS.",
    "model_type": "english"
})

# Сохранение аудио
audio_data = base64.b64decode(response["audio"])
with open("output.wav", "wb") as f:
    f.write(audio_data)
```

### Мультиязычный TTS
```python
# Русский
response = endpoint.run({
    "text": "Привет мир! Это высокопроизводительный TTS на GPU.",
    "model_type": "multilingual",
    "language_id": "ru"
})

# Китайский с эмоциями
response = endpoint.run({
    "text": "你好世界！这是GPU加速的语音合成。",
    "model_type": "multilingual",
    "language_id": "zh",
    "exaggeration": 0.8,  # Высокая выразительность
    "cfg_weight": 0.3     # Качественная генерация
})
```

### Voice Cloning
```python
# Загрузите референсный голос
with open("reference.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode()

# Клонирование голоса
response = endpoint.run({
    "text": "This will sound like the reference voice.",
    "model_type": "english",
    "audio_prompt": audio_b64,
    "exaggeration": 0.6,
    "cfg_weight": 0.4
})
```

### HTTP API
```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "text": "GPU-powered text to speech!",
      "model_type": "english"
    }
  }'
```

## 🎛️ API Параметры

| Параметр | Тип | Описание | Диапазон | По умолчанию |
|----------|-----|----------|----------|--------------|
| `text` | string | Текст для синтеза (обязательно) | 1-5000 символов | - |
| `model_type` | string | Модель TTS | "english", "multilingual" | "english" |
| `language_id` | string | Язык для multilingual модели | "en", "ru", "zh", и др. | "en" |
| `audio_prompt` | string | Base64 аудио для клонирования | WAV format | null |
| `exaggeration` | float | Эмоциональная выразительность | 0.0 - 1.0 | 0.5 |
| `cfg_weight` | float | Контроль качества/скорости | 0.0 - 1.0 | 0.5 |

## 📊 Ответ API

```json
{
  "audio": "base64_wav_data",
  "sample_rate": 22050,
  "duration": 2.5,
  "text": "original_text",
  "language": "ru",
  "model_type": "multilingual",
  "gpu_time": 1.2,
  "gpu_memory_gb": 8.4
}
```

## 🌍 Поддерживаемые языки

| Код | Язык | Код | Язык | Код | Язык |
|-----|------|-----|------|-----|------|
| `ar` | Arabic | `da` | Danish | `de` | German |
| `el` | Greek | `en` | English | `es` | Spanish |
| `fi` | Finnish | `fr` | French | `he` | Hebrew |
| `hi` | Hindi | `it` | Italian | `ja` | Japanese |
| `ko` | Korean | `ms` | Malay | `nl` | Dutch |
| `no` | Norwegian | `pl` | Polish | `pt` | Portuguese |
| `ru` | **Russian** | `sv` | Swedish | `sw` | Swahili |
| `tr` | Turkish | `zh` | **Chinese** | | |

## ⚡ Производительность

### GPU Рекомендации
- **RTX 4090**: Оптимальное соотношение цена/производительность
- **A100 40GB**: Максимальная производительность для больших нагрузок
- **RTX 3090**: Бюджетный вариант для тестирования

### Метрики производительности
- **Cold start**: 30-60 секунд (первый запрос)
- **Warm generation**: 1-5 секунд на RTX 4090
- **Throughput**: 10-15 запросов/минуту
- **GPU Memory**: 6-12GB в зависимости от модели

### Оптимизация настроек

**Быстрая генерация:**
```python
{
    "exaggeration": 0.3,
    "cfg_weight": 0.7
}
```

**Высокое качество:**
```python
{
    "exaggeration": 0.5,
    "cfg_weight": 0.5
}
```

**Драматичная речь:**
```python
{
    "exaggeration": 0.8,
    "cfg_weight": 0.3
}
```

## 💰 Стоимость (примерная)

| GPU | Цена/час | 1000 запросов* | Рекомендация |
|-----|----------|----------------|--------------|
| RTX 3090 | $0.34 | ~$0.95 | 💡 Тестирование |
| RTX 4090 | $0.79 | ~$2.20 | ⭐ Оптимально |
| A100 40GB | $1.89 | ~$5.25 | 🚀 Production |

*При среднем времени генерации 10 секунд на запрос

### Экономия средств:
- ✅ **Idle Timeout**: 5 секунд (автоотключение)
- ✅ **Min Workers**: 0 (платите только за использование)
- ✅ **Batch requests**: Группируйте запросы
- ✅ **Spot instances**: Скидка до 50% (если доступны)

## 🔍 Мониторинг и отладка

### Логи RunPod
```
Console → Serverless → Your Endpoint → Logs
```

### Метрики в ответе API
```python
response = endpoint.run({...})
print(f"GPU Time: {response['gpu_time']:.2f}s")
print(f"GPU Memory: {response['gpu_memory_gb']:.1f}GB")
```

### Частые проблемы

**GPU Out of Memory:**
```python
# Решение: Используйте более короткий текст или больше GPU памяти
{"error": "GPU out of memory. Try shorter text or restart container."}
```

**Model not loaded:**
```python
# Решение: Дождитесь завершения cold start
{"error": "Model 'multilingual' not available"}
```

## 🧪 Тестирование

### Локальное тестирование
```python
# Используйте test_api.py для проверки
python test_api.py --mode runpod --endpoint-id YOUR_ID --api-key YOUR_KEY
```

### Нагрузочное тестирование
```python
import asyncio
import aiohttp

async def test_load():
    tasks = []
    for i in range(10):  # 10 параллельных запросов
        task = endpoint.run_async({
            "text": f"Test message {i}",
            "model_type": "english"
        })
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## 🔗 Интеграция

### С вашими проектами
Этот API идеально подходит для:
- 🎬 Автогенерации видеоконтента
- 🎮 Игровых движков
- 📱 Мобильных приложений
- 🤖 AI агентов и чат-ботов
- 📚 E-learning платформ

### Webhook интеграция
```python
# Асинхронная обработка через webhooks
response = endpoint.run_async({
    "text": "Long text for processing...",
    "webhook": "https://your-app.com/tts-callback"
})
```

## 📞 Поддержка

- **RunPod Discord**: https://discord.gg/runpod
- **Chatterbox Issues**: https://github.com/resemble-ai/chatterbox/issues
- **Документация**: https://docs.runpod.io

---

**🚀 Готов к production использованию на GPU!**
