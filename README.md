Версия Python 3.12

Виртуальная среда:
* Установка
    * pip install virtualenv
* Создание виртуальной среды
    * python -m venv venv
* Активация виртульной среды
    * cmd: .\Scripts\activate
    * VS Code: Ctrl+Shift+P, команда "Python: Select Interpreter"

Установка библиотек: pip install -r requirements.txt  
Установка tesserocr:
* Официальный репозиторий: https://github.com/sirfz/tesserocr  
Если версия Python отличается, следовать инструкции по установке в репозитории
* Установить tesserocr.whl файл (\Tesserocr) (для версии 3.12)
* Добавить в переменные среды TESSDATA_PREFIX, указать путь "\Tesserocr\Models"  
Консольная команда  
setx TESSDATA_PREFIX %\...\Tesserocr\Models%

Требования для работы бота:
* Разрешение экрана 1920*1080
* Панель задач Windows всегда активна
* Игра должна быть в окне с рамкой на весь экран