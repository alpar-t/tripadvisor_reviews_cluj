# About 

A dear friend working on her PhD thesis in Tourism asked me if there is a quick and easy way to get
some review data for attractions in our home town, [Cluj-Napoca|https://en.wikipedia.org/wiki/Cluj-Napoca].
I told her it's possible and easy for sure, after all there's APIs for everything these days, and
there is a client that already can pull the data, so I don't even need to write that. 

I was wrong. (#TODO: detail why). The data needs to be collected from the web front-end directly,
and there are surprisingly few tools to make this easy and productive, two of which stood out: 
[Scrappy|http://scrapy.org/] (Python) and  [Geb|http://www.gebish.org/] (Groovy). Considering how
modern web pages make use of javascript and asynchronous request this task is not what it used to
be. So I set out to put these tools to use :
    - Scrappy ( out of the box )
    - Scrappy ( with phantomjs )
    - Geb ( with phantomjs )

I have used Geb before, but in a different context, and have not used Scrappy. 
Out of this experiment I expect to get some experience with these tools and write an article about
the problems and challenges of extracting data when there is no API available, and maybe prototype
some tools to go with it and write an article about it. 

# Development 

## Python 

To make it easy to run use [virtualenv|http://docs.python-guide.org/en/latest/dev/virtualenvs/]

### Setup
    
    virtualenv -p /usr/bin/python2.7 venv
    source venv/bin/activate
    pip install -r requirements.txt

### Activate the virtual environemnt 

    source venv/bin/activate

### When adding new packages 

    pip freeze > requirements.txt
