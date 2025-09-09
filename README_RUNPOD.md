# Chatterbox TTS для RunPod Serverless

Этот репозиторий содержит адаптированную версию [Chatterbox TTS](https://github.com/resemble-ai/chatterbox) для развертывания на RunPod Serverless платформе.

## 🚀 Быстрый старт

### 1. Подготовка репозитория

1. Форкните этот репозиторий в свой GitHub аккаунт
2. Клонируйте форк локально для тестирования (опционально)

### 2. Развертывание на RunPod

#### Через GitHub интеграцию:

1. Войдите в [RunPod Console](https://www.runpod.io/console)
2. Перейдите в раздел **Serverless**
3. Нажмите **New Endpoint**
4. Выберите **GitHub** как источник
5. Подключите ваш GitHub аккаунт (если еще не подключен)
6. Выберите форкнутый репозиторий
7. Настройте параметры:
   - **Container Image**: Оставьте пустым (будет собран из Dockerfile)
   - **Container Registry**: Docker Hub или GitHub Container Registry
   - **GPU Type**: RTX 3090, RTX 4090, или A100 (рекомендуется)
   - **Memory**: Минимум 16GB
   - **Container Disk**: 20GB+
   - **Max Workers**: По потребности
   - **Idle Timeout**: 5-10 секунд

#### Через Docker Registry:

```bash
# Соберите образ локально
docker build -t your-username/chatterbox-tts:latest .

# Загрузите в Docker Hub
docker push your-username/chatterbox-tts:latest
```

Затем используйте `your-username/chatterbox-tts:latest` как Container Image в RunPod.

## 📡 API Использование

### Базовый запрос (английский TTS)

```python
import runpod
import base64

# Настройка клиента
runpod.api_key = "YOUR_RUNPOD_API_KEY"
endpoint = runpod.Endpoint("YOUR_ENDPOINT_ID")

# Простой TTS
response = endpoint.run({
    "text": "Hello world! This is Chatterbox TTS running on RunPod.",
    "model_type": "english"
})

# Сохранение аудио
if "audio" in response:
    audio_data = base64.b64decode(response["audio"])
    with open("output.wav", "wb") as f:
        f.write(audio_data)
```

### Мультиязычный TTS

```python
# Русский TTS
response = endpoint.run({
    "text": "Привет мир! Это Chatterbox TTS на RunPod.",
    "model_type": "multilingual",
    "language_id": "ru"
})

# Китайский TTS
response = endpoint.run({
    "text": "你好世界！这是在RunPod上运行的Chatterbox TTS。",
    "model_type": "multilingual", 
    "language_id": "zh"
})
```

### Voice Cloning (клонирование голоса)

```python
# Загрузите референсный аудиофайл
with open("reference_voice.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode()

# TTS с клонированием голоса
response = endpoint.run({
    "text": "This text will be spoken in the reference voice.",
    "model_type": "english",
    "audio_prompt": audio_b64,
    "exaggeration": 0.7,  # Эмоциональная выразительность
    "cfg_weight": 0.3     # Контроль качества
})
```

### Параметры API

| Параметр | Тип | Описание | По умолчанию |
|----------|-----|----------|--------------|
| `text` | string | Текст для синтеза (обязательно) | - |
| `model_type` | string | "english" или "multilingual" | "english" |
| `language_id` | string | Код языка для multilingual модели | "en" |
| `audio_prompt` | string | Base64 аудио для клонирования голоса | null |
| `exaggeration` | float | Эмоциональная выразительность (0.0-1.0) | 0.5 |
| `cfg_weight` | float | Контроль качества генерации (0.0-1.0) | 0.5 |

### Поддерживаемые языки

Arabic (ar), Danish (da), German (de), Greek (el), English (en), Spanish (es), Finnish (fi), French (fr), Hebrew (he), Hindi (hi), Italian (it), Japanese (ja), Korean (ko), Malay (ms), Dutch (nl), Norwegian (no), Polish (pl), Portuguese (pt), Russian (ru), Swedish (sv), Swahili (sw), Turkish (tr), Chinese (zh)

## 🔧 Локальное тестирование

### С Docker Compose

```bash
# Соберите и запустите контейнер
docker-compose up --build

# Тестирование API
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "text": "Hello from local Docker!",
      "model_type": "english"
    }
  }'
```

### Без Docker

```bash
# Установите зависимости
pip install -r requirements.txt
pip install -e .

# Запустите handler
python handler.py
```

## 💡 Советы по оптимизации

### Производительность

1. **GPU выбор**: RTX 4090 > RTX 3090 > A100 для лучшего соотношения цена/производительность
2. **Batch processing**: Группируйте запросы для экономии
3. **Кэширование**: Используйте одинаковые audio_prompt для серии запросов

### Качество аудио

1. **Для разговорной речи**: `exaggeration=0.5`, `cfg_weight=0.5`
2. **Для драматичной речи**: `exaggeration=0.7`, `cfg_weight=0.3`
3. **Для быстрых голосов**: Уменьшите `cfg_weight` до 0.3

### Экономия средств

1. **Idle Timeout**: Установите 5-10 секунд для быстрого отключения
2. **Spot instances**: Используйте если доступны
3. **Auto-scaling**: Настройте минимальные и максимальные воркеры

## 🐛 Устранение неполадок

### Частые проблемы

**Ошибка загрузки модели**
```
Error loading models: CUDA out of memory
```
Решение: Увеличьте GPU память или используйте более мощную карту.

**Медленный cold start**
```
Timeout waiting for response
```
Решение: Увеличьте timeout в RunPod настройках или используйте warm workers.

**Ошибка аудио формата**
```
Error converting base64 to audio file
```
Решение: Убедитесь что audio_prompt в правильном base64 формате WAV файла.

### Логи и мониторинг

Логи доступны в RunPod Console в разделе Logs для каждого endpoint'а. Используйте их для диагностики проблем.

## 📊 Примеры использования

### Интеграция с веб-приложением

```javascript
// JavaScript пример
async function generateTTS(text, language = 'en') {
    const response = await fetch('https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer YOUR_API_KEY',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            input: {
                text: text,
                model_type: 'multilingual',
                language_id: language
            }
        })
    });
    
    const result = await response.json();
    return result.output.audio; // base64 audio
}
```

### Batch обработка

```python
# Обработка множественных текстов
texts = [
    {"text": "First text", "language_id": "en"},
    {"text": "Второй текст", "language_id": "ru"},
    {"text": "第三个文本", "language_id": "zh"}
]

for item in texts:
    response = endpoint.run({
        "text": item["text"],
        "model_type": "multilingual",
        "language_id": item["language_id"]
    })
    # Сохранение результата...
```

## 📄 Лицензия

MIT License - см. оригинальный [LICENSE](LICENSE) файл.

## 🤝 Поддержка

- **Оригинальный Chatterbox**: [GitHub Issues](https://github.com/resemble-ai/chatterbox/issues)
- **RunPod документация**: [docs.runpod.io](https://docs.runpod.io)
- **RunPod Discord**: [Официальный сервер](https://discord.gg/runpod)

---

**Создано для RunPod Serverless** 🚀
