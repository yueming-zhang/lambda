import sys, os, inspect, pathlib 
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = f"{pathlib.Path(currentdir).parent.parent.absolute()}/"
sys.path.insert(0,parentdir)

import json
import pytest
from news_sentiment_app import app



def test_news_find():

    ret = app.findNews()

    d = ret.json()

    assert d['status'] == 'ok', 'get news should return ok status'
    assert len(d['articles']) > 5, 'get news should return at least 5 news'
    newsTitle=d['articles'][0]['title']
    assert len(newsTitle), 'len (first news title) needs to be > 0'

    print(ret)
    pass



def test_setment_get():

    ret = app.getSentiment('the bitcoin is doing great')
    res = json.loads(ret)

    assert res['Sentiment'] == 'POSITIVE', 'doing great means positive'

def test_news_crud():
    title = 'bitcoin is great'
    ts = '2021071325'
    app.insertDynamo('POSITIVE', title, ts)

    item = app.getDynamo(title, ts)

    assert item != None
    assert item['Item']['title'] == title
    assert item['Item']['timestamp'] == ts

    delRsp = app.deleteDynamoItem(title, ts)
    assert delRsp != None
    assert delRsp['ResponseMetadata']['HTTPStatusCode'] == 200
    