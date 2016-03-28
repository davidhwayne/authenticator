import time
import gzip
import csv
import numpy as np
from scipy.sparse import dok_matrix
from sklearn.utils import shuffle
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score

def get_sample_data(numlines):
    with gzip.open('auth.txt.gz','rb') as fh:
        read_obj=csv.reader(fh)
        data=[]
        for i,line in enumerate(read_obj):
            if i==numlines:
                break
            data.append(line)
    return data
    
def networkcheck(user):
    if user=='ANONYMOUS LOGON':
        return 1
    elif user=='LOCAL SERVICE':
        return 2
    elif user=='NETWORK SERVICE':
        return 3
    else:
        return np.nan
    
def makefeatures(data,numlines):
    feats=[]
    X=dok_matrix((numlines,50000),dtype=np.float32)
    y=[]
    dataindexer={}
    userts={}
    lastindex=6
    for i,d in enumerate(data):
        y.append(d[-1])
        #Split source user + dom and dest user + dom into user and dom
        #Check if user contains network information
        source=d[1].split('@')
        dest=d[2].split('@')
        try:
            X[i,networkcheck(source[0])]=1
        except:
            pass
        try:
            X[i,networkcheck(dest[0])+3]=1
        except:
            pass
        #Index the dom, add to feature vector
        for j,dom in enumerate([source[1],dest[1]]):
            try:
                X[i,dataindexer[str(j+1)+'--'+dom]]=1
            except:
                dataindexer[str(j+1)+'--'+dom]=lastindex+1
                lastindex+=1
                X[i,dataindexer[str(j+1)+'--'+dom]]=1
        #Use source user data to normalize time stamp field
        try:
            X[i,0]=d[0]-userts[source[0]]
            userts[source[0]]=d[0]
        except:
            X[i,0]=0
            userts[source[0]]=d[0]
        #Index remaining data elements, add to feature vector
        for j in range(3,8):
            try:
                X[i,dataindexer[str(j)+'--'+d[j]]]=1
            except:
                dataindexer[str(j)+'--'+d[j]]=lastindex+1
                lastindex+=1
                X[i,dataindexer[str(j)+'--'+d[j]]]=1
    return (X,y)

def main(numlines):
    start=time.time()
    if numlines>1000000:
        print 'Warning: choosing a large number of rows of data can lead to huge slowdowns'
    print '\nImporting Training Set'
    (X,y)=makefeatures(get_sample_data(numlines),numlines)
    print 'Shuffling'
    X, y = shuffle(X, y, random_state=0)
    train_X=X[:int(numlines*.8),:]
    train_y=y[:int(numlines*.8)]
    test_X=X[int(numlines*.8):,:]
    test_y=y[int(numlines*.8):]
    print 'Training Model'
    clf=RandomForestClassifier(class_weight='auto',random_state=1)
    clf.fit(train_X,train_y)
    print 'Predicting and Evaluating'
    predictions=clf.predict(test_X)
    print '\nResults:'
    print 'Accuracy: ',accuracy_score(test_y,predictions)
    print 'Success Recall: ',recall_score(test_y,predictions,pos_label='Success')
    print 'Success Precision: ',precision_score(test_y,predictions,pos_label='Success')
    print 'Fail Recall: ',recall_score(test_y,predictions,pos_label='Fail')
    print 'Fail Precision: ',precision_score(test_y,predictions,pos_label='Fail')
    print '\nCompleted in {duration} seconds'.format(duration=time.time()-start)

main(int(raw_input('\nOn how many rows of data would you like to train and test the model? ')))

