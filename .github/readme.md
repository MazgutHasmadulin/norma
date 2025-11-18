Развертывание приложения

sudo apt install python3.13 python3.13-pip -y точно не уверен, но нам нужен питон 3.13.5, 3.13 мб тоже пойдет

Проверить версию

python --version или python3 --version

Установить модуль создания виртуальных окружений

sudo apt install python3-venv -y

Создать вирт окружение

mkdir /webapps
cd /webapps
python3 -m venv myproject_venv
source myproject_venv/bin/activate

Поставить sqlite3
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install sqlite3
$ sqlite3 --version

Склонировать проект из гита

git clone https://github.com/MazgutHasmadulin/norma.git --branch=Simplified

сменить папку на папку, куда закинул проект

Уставновить джанго, проверить, что запускаем скрипт из папки с проектом

pip install -r requirements.txt
создать виртуальное окружение

Установить bootstrap 5

$ pip install django-bootstrap-v5

В файле setting.py 
DEBUG=False
чтобы юзеры не видели отладочную инфу

в ALLOWED_HOST прописать свой хост или домен

Накатить БД

python manage.py migrate

И собрать статику

python manage.py collectstatic

Создать суперюзера

python manage.py createsuperuser