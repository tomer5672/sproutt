# Sproutt insurance project

This is an example of insurance application.

this application built by django REST API.

### Installation Guide

```
pip install requirements.txt
```

### running Guide
create .env file with the relevant parameters:
SECRET_KEY
HEALTH_CLASS_TABLE_FILE(and make sure it exists) under price_calculator/files 
RATES_TABLE_FILE(and make sure it exists) under price_calculator/files
```
cd .\sproutt_insurance_api\
python manage.py runserver
```

### API Endpoints

| POST | /price/ | to calculate price by factors(see more in README.md in price_calculator folder).

### Authors

https://github.com/tomer5672
