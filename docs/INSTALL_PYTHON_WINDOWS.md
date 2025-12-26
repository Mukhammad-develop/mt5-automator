# Как установить Python на Windows

Пошаговая инструкция по установке Python для MT5 Automator.

## Способ 1: Официальный установщик (Рекомендуется)

### Шаг 1: Скачать Python

1. Откройте браузер
2. Перейдите на: https://www.python.org/downloads/
3. Нажмите большую жёлтую кнопку **"Download Python 3.x.x"** (самая новая версия)
   - Или выберите конкретную версию: https://www.python.org/downloads/windows/
   - **Важно:** Нужна версия 3.9 или выше (рекомендуется 3.11 или 3.12)

### Шаг 2: Установить Python

1. **Запустите скачанный файл** (например: `python-3.12.0-amd64.exe`)
2. **ВАЖНО:** Внизу окна установки отметьте галочку:
   - ✅ **"Add Python to PATH"** (Добавить Python в PATH)
   - Это очень важно! Без этого Python не будет работать из командной строки
3. Нажмите **"Install Now"** (Установить сейчас)
4. Дождитесь завершения установки
5. Нажмите **"Close"** (Закрыть)

### Шаг 3: Проверить установку

1. Откройте **PowerShell** или **Командную строку** (CMD)
2. Введите:
   ```powershell
   python --version
   ```
3. Должно показать: `Python 3.12.x` (или вашу версию)

Если показывает версию - всё готово! ✅

Если показывает ошибку "python не распознан" - см. раздел "Устранение проблем" ниже.

## Способ 2: Через Microsoft Store (Альтернатива)

1. Откройте **Microsoft Store** (Магазин Microsoft)
2. Найдите **"Python 3.12"** или **"Python 3.11"**
3. Нажмите **"Установить"**
4. После установки проверьте: `python --version`

**Примечание:** Этот способ автоматически добавляет Python в PATH.

## Проверка установки

После установки проверьте в PowerShell:

```powershell
# Проверить версию Python
python --version

# Проверить pip (менеджер пакетов)
pip --version

# Проверить, что Python работает
python -c "print('Hello, Python!')"
```

Все три команды должны работать без ошибок.

## Устранение проблем

### Проблема: "python не распознан как команда"

**Решение 1: Переустановить с PATH**
1. Удалите Python через "Программы и компоненты"
2. Скачайте и установите заново
3. **Обязательно отметьте "Add Python to PATH"**

**Решение 2: Добавить в PATH вручную**
1. Найдите, где установлен Python:
   - Обычно: `C:\Users\ВашеИмя\AppData\Local\Programs\Python\Python312\`
   - Или: `C:\Program Files\Python312\`
2. Добавьте этот путь в системную переменную PATH (см. инструкцию ниже)

**Решение 3: Использовать py launcher**
Windows обычно устанавливает `py` launcher:
```powershell
py --version
py -m pip --version
```

### Проблема: Несколько версий Python

Если установлено несколько версий:
```powershell
# Использовать конкретную версию
py -3.12 --version
py -3.11 --version

# Или указать полный путь
C:\Python312\python.exe --version
```

## Добавление Python в PATH вручную

Если Python не в PATH:

1. **Найти путь к Python:**
   - Обычно: `C:\Users\ВашеИмя\AppData\Local\Programs\Python\Python312\`
   - Или: `C:\Program Files\Python312\`
   - Или: `C:\Python312\`

2. **Добавить в PATH:**
   - Нажмите `Win + R`
   - Введите `sysdm.cpl` и нажмите Enter
   - "Переменные среды" (Environment Variables)
   - В "Системные переменные" найдите `Path` → "Изменить"
   - "Создать" → Добавьте путь к Python (например: `C:\Python312`)
   - "Создать" → Добавьте путь к Scripts (например: `C:\Python312\Scripts`)
   - "OK" на всех окнах

3. **Перезапустить PowerShell** (закрыть и открыть заново)

4. **Проверить:** `python --version`

## Рекомендуемая версия

Для MT5 Automator рекомендуется:
- **Python 3.11** или **3.12** (самые стабильные)
- Минимум: **Python 3.9**

Не используйте Python 2.x - он устарел и не поддерживается.

## После установки Python

1. **Обновить pip:**
   ```powershell
   python -m pip install --upgrade pip
   ```

2. **Установить зависимости проекта:**
   ```powershell
   cd C:\Users\abdurakhmon\Desktop\mt5-automator
   pip install -r requirements-windows.txt
   ```

3. **Проверить установку:**
   ```powershell
   python check_setup.py
   ```

## Быстрая проверка

После установки выполните:

```powershell
python --version
pip --version
python -c "import sys; print(sys.executable)"
```

Если все три команды работают - Python установлен правильно! ✅

## Полезные ссылки

- **Официальный сайт:** https://www.python.org/downloads/
- **Документация:** https://docs.python.org/3/
- **Руководство для начинающих:** https://www.python.org/about/gettingstarted/

## Следующие шаги

После установки Python:

1. ✅ Установите зависимости: `pip install -r requirements-windows.txt`
2. ✅ Настройте config.env
3. ✅ Запустите тесты: `python test_system.py`
4. ✅ Запустите бота: `python main.py`

