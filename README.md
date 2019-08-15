# Training Diary #

Web application for recording and analyzing trainings.

## Installation ##

* Install Python 3.6+

* Clone repository or download source code

Run following commands in repository root folder:

* Install required python libraries

````
pip install -r requirements.txt
````

* Set up the database

````
python Treenit/manage.py migrate
````

* Import static data

````
python build/import_data.py
````

## Getting Started ##

Start program by running following command
````
python Treenit/manage.py runserver
````

Open web-browser (preferred Chrome) and go to
````
http://127.0.0.1:8000/treenipaivakirja/
````

Log in or register a new user.

## Features ##

### Keep track of your trainings

* Input and modify trainings
* Search and investigate historical trainings
* Download training data to excel or csv

![trainings](./img/trainings.png)

### Analyze your trainings

* Analyze your training amounts with various graphical reports

![report_amount](./img/report_amount.png)

### Track your progression

* Analyze progression in each sport

![report_sport](./img/report_sport.png)

### Multiuser support and personalise settings

* Multiple users can use the same program
* Sports and training zones can be customized to each user

![settings](./img/settings.png)