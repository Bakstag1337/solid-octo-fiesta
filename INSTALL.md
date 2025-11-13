# 🚀 Быстрая Установка

## DEB Пакет (Ubuntu, Debian, Linux Mint, Pop!_OS, и т.д.)

### Способ 1: Одной командой

```bash
wget https://github.com/Bakstag1337/solid-octo-fiesta/raw/main/sysmon_1.0.0_all.deb
sudo dpkg -i sysmon_1.0.0_all.deb
sudo apt-get install -f
```

### Способ 2: Из исходников

```bash
# Клонируй репозиторий
git clone https://github.com/Bakstag1337/solid-octo-fiesta.git
cd solid-octo-fiesta

# Установи пакет
sudo dpkg -i sysmon_1.0.0_all.deb

# Если есть ошибки зависимостей, исправь:
sudo apt-get install -f
```

### Запуск

```bash
sysmon
```

Или найди **System Monitor** в меню приложений!

---

## Для других дистрибутивов (Arch, Fedora, openSUSE и т.д.)

### Установка зависимостей

**Arch Linux:**
```bash
sudo pacman -S python python-psutil tk
```

**Fedora:**
```bash
sudo dnf install python3 python3-psutil python3-tkinter
```

**openSUSE:**
```bash
sudo zypper install python3 python3-psutil python3-tk
```

### Установка программы

```bash
git clone https://github.com/Bakstag1337/solid-octo-fiesta.git
cd solid-octo-fiesta
chmod +x install.sh
./install.sh
```

### Запуск

```bash
python3 src/sysmon.py
```

---

## Удаление

### Если установил через .deb:
```bash
sudo apt-get remove sysmon
```

### Если установил вручную:
Просто удали папку с программой
```bash
rm -rf solid-octo-fiesta
```

---

## Проблемы?

### "ModuleNotFoundError: No module named 'tkinter'"

Установи Tkinter:

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-tk
```

**Arch:**
```bash
sudo pacman -S tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

### "ModuleNotFoundError: No module named 'psutil'"

```bash
pip3 install psutil --user
```

Или при установке .deb пакета:
```bash
sudo apt-get install -f
```

### Программа не запускается

Убедись что у тебя есть графическое окружение (не SSH сессия).

---

Готово! Наслаждайся! 🎉
