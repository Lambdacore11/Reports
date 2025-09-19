Перед запуском убедиться что установлены все нобходимые зависимости.  
В частности библиотеки pytest и rich.  
```bash 
pip install pytest rich
```
Можно установить всё что небходимо непосредственно из проекта.
```bash 
pip install -r requirements.txt
```
Пример работы скрипта
```bash 
python3 main.py --files students1.csv students2.csv students3.csv --report student-performance
```
В аргументы --files можно передать любое количество подходящих .csv файлов
```bash 
python3 main.py --files students1.csv --report student-performance
```
```bash 
python3 main.py --files students1.csv students2.csv  --report student-performance
```
  ps. Добавил 3ю таблицу чтобы была возможность агрегировать по оценкам, как того требовало тз.

