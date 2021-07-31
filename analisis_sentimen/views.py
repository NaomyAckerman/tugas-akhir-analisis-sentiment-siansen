import pandas as pd
import numpy as np
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from analisis_sentimen.models import *
from analisis_sentimen.utils.tweets import TweetManager
from analisis_sentimen.utils.preprocessing import Preprocessing
from analisis_sentimen.utils.classifier import Classifier

def index(request):
    template = 'index.html'
    app_url = request.path
    konteks = {
        'judul' : 'Analisis Sentimen',
        'app_url' : app_url
    }
    return render(request, template, konteks)

def dashboard(request):
    template = 'dashboard.html'
    app_url = request.path
    konteks = {
        'judul' : 'Analisis Sentimen',
        'app_url' : app_url
    }
    if request.method == 'GET':
        datasets = Datasets.objects.filter(tipe_data='testing')
        sentiments = [tweet['label'] for tweet in datasets[0].tweets]
        lptg_positif = []
        lptg_negatif = []
        lptg_netral = []
        lptg_tanggal = []
        datasets_df = pd.DataFrame(data=datasets[0].tweets)
        for data in datasets_df.groupby(datasets_df['tanggal'].dt.strftime('%d-%m-%y • Jam %H')):
            lptg_tanggal.append(data[0])
            lptg_positif.append(data[1].label.tolist().count('positif'))
            lptg_negatif.append(data[1].label.tolist().count('negatif'))
            lptg_netral.append(data[1].label.tolist().count('netral'))
        konteks['lptg'] = json.dumps({
            'positif' : lptg_positif,
            'negatif' : lptg_negatif,
            'netral' : lptg_netral,
            'tanggal' : lptg_tanggal,
        })
        konteks['data_tanggal'] = datasets[0].tanggal_update
        konteks['data_keyword'] = datasets[0].keyword
        konteks['tweets'] = datasets[0].tweets
        konteks['sentiments'] = [{
            'positif':sentiments.count('positif'),
            'netral' : sentiments.count('netral'),
            'negatif' : sentiments.count('negatif')
        }]
        return render(request, template, konteks)
    # Datasets testing
    tweet_mngr = TweetManager()
    data_prepro = Preprocessing()
    keyword = '#dirumahaja OR #vaksinuntukrakyatindonesia OR #psbb OR #covid OR #covid19 OR #covidindonesia OR #vaksinjakarta OR #vaksin OR #vaksinPulihkanRI OR #vaksinDemiLindungiNKRI'
    data_crawling = tweet_mngr.crawling_tweet(keyword, 10, 'recent', 'id')
    df_testing = data_prepro.process(data_crawling)
    # Datasets training
    datasets_train = Datasets.objects.filter(tipe_data='training')
    df_training = pd.DataFrame(data=datasets_train[0].tweets)
    # Training model => data from db
    x_train = df_training.list_tweet
    y_train = df_training.label
    clf = Classifier(x_train, y_train)
    # Predict clf
    x_test = df_testing.list_tweet
    predict = clf.predict(x_test)
    df_testing['label'] = ['negatif' if i == -1 else 'positif' if i == 1 else 'netral' for i in predict]
    # Update datasets
    list_tweets = []
    for data in df_testing.values.tolist():
        list_tweets.append({
            'nama' : data[0],
            'username' : data[1],
            'tanggal' : data[2],
            'tweet' : data[3],
            'list_tweet' : data[10],
            'label' : data[11],
        })
    new_datasets = Datasets.objects.get(tipe_data='testing')
    new_datasets.keyword = keyword
    new_datasets.tweets = list_tweets
    new_datasets.save(update_fields=['keyword', 'tweets', 'tanggal_update'])
    messages.success(request, 'Data Berhasil diupdate!')
    return redirect('dashboard')
    
def upload(request):
    template = 'upload.html'
    konteks ={'judul' : 'Upload Dataset'}
    if request.method == 'GET': return render(request, template, konteks)
    try:
        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            messages.error(request, 'Format tidak didukung!')
            return redirect('upload')
        datasets = pd.read_csv(file, usecols = ['nama', 'username', 'tanggal', 'tweet', 'list_tweet', 'label'])
    except Exception as err:
        messages.error(request, str(err))
        return redirect('upload')
    list_tweets = []
    for data in datasets.values.tolist():
        list_tweets.append({
            'nama' : data[0],
            'username' : data[1],
            'tanggal' : datetime.strptime(data[2], '%Y-%m-%d %H:%M:%S'),
            'tweet' : data[3],
            'list_tweet' : data[4],
            'label' : data[5],
        })
    d = Datasets()
    d.keyword = '#dirumahaja #vaksinuntukrakyatindonesia #psbb #covid #covid19 #covidindonesia #vaksinjakarta #vaksin #vaksinPulihkanRI #vaksinDemiLindungiNKRI'
    d.tipe_data = 'training'
    d.tweets = list_tweets
    d.save()
    messages.success(request, 'Data Berhasil diupload!')
    return redirect('upload')