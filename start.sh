#!/bin/bash
echo "Установка зависимостей..."
pip3 install -r requirements.txt
echo "Запуск сервера..."
python3 app.py