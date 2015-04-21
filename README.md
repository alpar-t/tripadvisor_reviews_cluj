
# Development 

To make it easy to run use [virtualenv|http://docs.python-guide.org/en/latest/dev/virtualenvs/]

## Setup
    
    virtualenv -p /usr/bin/python2.7 venv
    source venv/bin/activate
    pip install -r requirements.txt

## Activate the virtual environemnt 

    source venv/bin/activate

## When adding new packages 

    pip freeze > requirements.txt
