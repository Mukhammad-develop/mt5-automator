# Быстрое исправление проблем установки

Вы запустили `py setup.py` и увидели несколько ошибок. Вот как их исправить:

## Проблема 1: Отсутствуют Python пакеты

**Все пакеты не установлены.** Нужно установить зависимости.

### Решение:

```powershell
pip install -r requirements-windows.txt
```

Или если не работает:

```powershell
py -m pip install -r requirements-windows.txt
```

**Что это установит:**
- telethon (для Telegram)
- MetaTrader5 (для MT5)
- pytesseract (для OCR)
- Pillow (для обработки изображений)
- opencv-python (cv2)
- pyyaml (yaml)
- python-dotenv (dotenv)
- и другие зависимости

**Время установки:** 2-5 минут

## Проблема 2: Tesseract OCR не найден

**Tesseract установлен, но не в PATH.**

### Решение:

1. Найдите, где установлен Tesseract:
   - Обычно: `C:\Program Files\Tesseract-OCR\tesseract.exe`
   - Или: `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`

2. Откройте файл `config.env` в текстовом редакторе

3. Добавьте или измените строку:
   ```env
   TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
   ```
   (Используйте ваш реальный путь)

4. Сохраните файл

**Подробная инструкция:** См. `docs/FIX_TESSERACT_WINDOWS_RU.md`

## Проблема 3: Отсутствует папка logs

**Папка будет создана автоматически** при первом запуске бота, но можно создать вручную:

```powershell
mkdir logs
```

Или просто запустите `py setup.py` ещё раз - он теперь создаст её автоматически.

## Проблема 4: config/config.yaml не найден

**Это нормально!** Проект использует `config.env` вместо `config.yaml`.

Просто убедитесь, что у вас есть файл `config.env` (скопируйте из `config.env.example` если его нет).

## Пошаговая инструкция исправления

### Шаг 1: Установить зависимости

```powershell
pip install -r requirements-windows.txt
```

Дождитесь завершения установки (может занять несколько минут).

### Шаг 2: Настроить Tesseract

1. Откройте `config.env`
2. Найдите строку `TESSERACT_CMD=`
3. Установите путь к tesseract.exe:
   ```env
   TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract.exe
   ```

### Шаг 3: Создать папку logs (опционально)

```powershell
mkdir logs
```

Или просто запустите `py setup.py` ещё раз.

### Шаг 4: Проверить снова

```powershell
py setup.py
```

Теперь должно быть больше зелёных галочек ✅

## Быстрая команда (всё сразу)

Если хотите сделать всё быстро:

```powershell
# 1. Установить зависимости
pip install -r requirements-windows.txt

# 2. Создать папку logs
mkdir logs

# 3. Проверить снова
py setup.py
```

## После исправления

Когда все проверки пройдут:

1. **Настройте config.env:**
   - MT5_LOGIN, MT5_PASSWORD, MT5_SERVER
   - TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
   - TELEGRAM_CHANNELS

2. **Запустите тесты:**
   ```powershell
   py test_system.py
   ```

3. **Запустите бота:**
   ```powershell
   py main.py
   ```

## Нужна помощь?

- **Tesseract:** См. `docs/FIX_TESSERACT_WINDOWS_RU.md`
- **Python:** См. `docs/INSTALL_PYTHON_WINDOWS_RU.md`
- **MT5 Server:** См. `docs/FIND_MT5_SERVER_RU.md`

