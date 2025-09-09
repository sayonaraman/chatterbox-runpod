# 🚀 Развертывание Chatterbox TTS на RunPod

## Пошаговая инструкция

### 1. Подготовка GitHub репозитория

1. **Форк репозитория**:
   - Перейдите на GitHub и создайте форк этого репозитория
   - Клонируйте форк к себе на машину (опционально)

2. **Настройка GitHub Actions** (автоматическая сборка Docker):
   - GitHub Actions автоматически соберет Docker образ при push
   - Образ будет доступен в GitHub Container Registry: `ghcr.io/your-username/chatterbox-runpod`

### 2. Создание RunPod Serverless Endpoint

1. **Войдите в RunPod Console**: https://www.runpod.io/console

2. **Создайте новый Serverless Endpoint**:
   ```
   Serverless → New Endpoint
   ```

3. **Настройте параметры**:

   **Container Configuration:**
   - **Container Image**: `ghcr.io/your-username/chatterbox-runpod:latest`
   - **Container Registry Credentials**: GitHub (если репозиторий приватный)
   - **Container Start Command**: `python handler.py`

   **Hardware:**
   - **GPU**: RTX 3090, RTX 4090, или A100
   - **Memory**: 16GB+ (рекомендуется 24GB)
   - **Container Disk**: 25GB+
   - **Volume Disk**: 0GB (не требуется)

   **Scaling:**
   - **Min Workers**: 0 (для экономии)
   - **Max Workers**: 3-5 (по потребности)
   - **Idle Timeout**: 5 секунд
   - **Max Execution Time**: 300 секунд

   **Advanced:**
   - **Environment Variables**: Оставьте пустым
   - **Exposed HTTP Ports**: 8000

4. **Создайте Endpoint** и дождитесь готовности

### 3. Тестирование API

#### Через RunPod Python SDK:

```python
import runpod
import base64

# Настройка
runpod.api_key = "YOUR_RUNPOD_API_KEY"
endpoint = runpod.Endpoint("YOUR_ENDPOINT_ID")

# Тест английского TTS
response = endpoint.run({
    "text": "Hello world! This is Chatterbox TTS on RunPod.",
    "model_type": "english"
})

# Сохранение аудио
if "audio" in response:
    audio_data = base64.b64decode(response["audio"])
    with open("test.wav", "wb") as f:
        f.write(audio_data)
    print("✅ Audio saved as test.wav")
```

#### Через HTTP API:

```bash
curl -X POST https://api.runpod.ai/v2/YOUR_ENDPOINT_ID/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "text": "Привет мир! Это тест на русском языке.",
      "model_type": "multilingual",
      "language_id": "ru"
    }
  }'
```

### 4. Локальное тестирование (опционально)

Если хотите протестировать локально перед развертыванием:

```bash
# Соберите образ
docker build -t chatterbox-runpod:local .

# Запустите контейнер
docker run --gpus all -p 8000:8000 chatterbox-runpod:local

# Тестируйте API
python test_api.py --mode local
```

## 💰 Оценка стоимости

### Примерные цены RunPod (могут изменяться):

- **RTX 3090**: ~$0.34/час
- **RTX 4090**: ~$0.79/час  
- **A100 40GB**: ~$1.89/час

### Оптимизация расходов:

1. **Idle Timeout**: 5-10 секунд для быстрого отключения
2. **Spot Instances**: Используйте если доступны (скидка до 50%)
3. **Batch Processing**: Группируйте запросы
4. **Min Workers = 0**: Платите только за активное использование

### Примерный расчет:
- 1000 запросов по 10 секунд каждый = ~2.8 часа RTX 3090 = ~$0.95
- Cold start: ~30-60 секунд (первый запрос после idle)

## 🔧 Настройка производительности

### Для лучшего качества:
```python
{
    "text": "Your text here",
    "model_type": "multilingual",
    "language_id": "ru",
    "exaggeration": 0.5,    # Стандартная выразительность
    "cfg_weight": 0.5       # Баланс качества/скорости
}
```

### Для драматичной речи:
```python
{
    "text": "Dramatic announcement!",
    "model_type": "english", 
    "exaggeration": 0.8,    # Высокая выразительность
    "cfg_weight": 0.3       # Более медленная, качественная генерация
}
```

### Для быстрой генерации:
```python
{
    "text": "Quick generation",
    "model_type": "english",
    "exaggeration": 0.3,    # Низкая выразительность
    "cfg_weight": 0.7       # Быстрая генерация
}
```

## 🐛 Решение проблем

### Частые ошибки:

**"CUDA out of memory"**
- Используйте GPU с большим объемом памяти (RTX 4090, A100)
- Уменьшите batch size в коде

**"Container failed to start"**
- Проверьте Docker образ в GitHub Container Registry
- Убедитесь что образ собрался без ошибок

**"Timeout waiting for response"**
- Увеличьте Max Execution Time в настройках endpoint
- Проверьте что GPU достаточно мощный

**"Model loading failed"**
- Увеличьте Container Disk до 30GB+
- Проверьте интернет соединение контейнера

### Мониторинг:

1. **RunPod Logs**: Console → Serverless → Your Endpoint → Logs
2. **Metrics**: Отслеживайте время выполнения и использование ресурсов
3. **Costs**: Регулярно проверяйте расходы в Billing

## 📞 Поддержка

- **RunPod Discord**: https://discord.gg/runpod
- **RunPod Docs**: https://docs.runpod.io
- **Chatterbox Issues**: https://github.com/resemble-ai/chatterbox/issues

---

**Готово к production использованию!** 🎉
