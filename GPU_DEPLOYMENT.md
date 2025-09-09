# 🚀 GPU Serverless Deployment Guide

**Быстрое развертывание Chatterbox TTS на RunPod GPU Serverless**

## 📋 Чек-лист развертывания

### ✅ 1. GitHub подготовка (2 минуты)
```bash
# Форкните репозиторий на GitHub
# GitHub Actions автоматически соберет Docker образ
```

### ✅ 2. RunPod Serverless (5 минут)

**Обязательные настройки:**
```
Container Image: ghcr.io/your-username/chatterbox-runpod:latest
GPU Type: RTX 4090 (рекомендуется) или A100
Memory: 16GB+
Container Disk: 25GB+
```

**Экономичные настройки:**
```
Min Workers: 0
Max Workers: 3
Idle Timeout: 5 секунд
Max Execution Time: 300 секунд
```

### ✅ 3. Тестирование (1 минута)
```python
import runpod
runpod.api_key = "YOUR_API_KEY"
endpoint = runpod.Endpoint("YOUR_ENDPOINT_ID")

# Тест
response = endpoint.run({
    "text": "Привет! GPU TTS работает!",
    "model_type": "multilingual",
    "language_id": "ru"
})
print(f"✅ Успех! GPU время: {response['gpu_time']:.2f}s")
```

## 🎯 Оптимальные GPU конфигурации

### 💡 Для тестирования
```
GPU: RTX 3090
Memory: 16GB
Cost: ~$0.34/час
Throughput: 6-8 запросов/мин
```

### ⭐ Для production
```
GPU: RTX 4090  
Memory: 24GB
Cost: ~$0.79/час
Throughput: 10-15 запросов/мин
```

### 🚀 Для высоких нагрузок
```
GPU: A100 40GB
Memory: 40GB
Cost: ~$1.89/час
Throughput: 15-20 запросов/мин
```

## 📊 Мониторинг производительности

### Ключевые метрики:
- **Cold Start**: 30-60 секунд (первый запрос)
- **GPU Time**: 1-5 секунд на запрос
- **GPU Memory**: 6-12GB использование
- **Throughput**: Зависит от GPU

### Логи RunPod:
```
Console → Serverless → Endpoint → Logs

Ищите:
✅ "All models loaded successfully on GPU"
🎯 "TTS Request: ..."
✅ "Generated 2.5s audio in 1.2s GPU time"
```

## 💰 Оценка стоимости

### Примерный расчет:
```
1000 запросов × 3 сек GPU время = 50 минут GPU
RTX 4090: 50 мин × $0.79/час = ~$0.66
A100: 50 мин × $1.89/час = ~$1.58
```

### Экономия:
- ✅ Idle Timeout 5 сек = автоотключение
- ✅ Min Workers 0 = платите только за использование  
- ✅ Batch запросы = меньше cold starts

## 🔧 Настройки качества

### Быстрая генерация:
```python
{
    "exaggeration": 0.3,
    "cfg_weight": 0.7
}
```

### Высокое качество:
```python
{
    "exaggeration": 0.5,
    "cfg_weight": 0.5  
}
```

### Драматичная речь:
```python
{
    "exaggeration": 0.8,
    "cfg_weight": 0.3
}
```

## 🐛 Решение проблем

### "CUDA not available"
- ✅ Проверьте выбор GPU в RunPod
- ✅ Убедитесь что используете GPU endpoint

### "GPU out of memory"  
- ✅ Используйте более мощный GPU
- ✅ Сократите длину текста (<5000 символов)
- ✅ Перезапустите container

### "Container failed to start"
- ✅ Проверьте Docker образ в GitHub Registry
- ✅ Увеличьте Container Disk до 30GB+

### Медленный cold start
- ✅ Используйте warm workers (Min Workers > 0)
- ✅ Группируйте запросы в batch

## 📞 Быстрая помощь

- **RunPod Discord**: https://discord.gg/runpod
- **Документация**: https://docs.runpod.io/serverless
- **Status**: https://status.runpod.io

---

**🎉 Готово! Ваш GPU TTS API работает!**
