#Predicting Success or Failure of Authentication
A machine learning project based on the LANL Comprehensive, Multi-Source Cyber-Security Events datasets.

### Background
The Los Alamos National Laboratory has made public a group of datasets collected from their networks over approximately 2 months. The goal of this project is to build a binary classifier that accurately predicts the success or failure of authentication using the auth.txt.gz dataset provided by LANL.

### Description
From LANL:
This data represents authentication events collected from individual Windows-based desktop computers, servers, and Active Directory servers. Each event is on a separate line in the form of "time,source user@domain,destination user@domain,source computer,destination computer,authentication type,logon type,authentication orientation,success/failure" and represents an authentication event at the given time. The values are comma delimited and any fields that do not have a valid value are represented as a question mark ('?').

Here are three lines from the data as an example:

```
1,C625$@DOM1,U147@DOM1,C625,C625,Negotiate,Batch,LogOn,Success
1,C653$@DOM1,SYSTEM@C653,C653,C653,Negotiate,Service,LogOn,Success
1,C660$@DOM1,SYSTEM@C660,C660,C660,Negotiate,Service,LogOn,Success
```

### Data Manipulation
After exploring a large sub-collection of data from this dataset (using a temporary SQL database) consistent patterns were difficult to determine. The only thing that became obvious is that number of samples that have a failure of authentication were vastly outnumbered by those with successful authentication. On a 10,000,000 row sample, the failure rate is approximately .75%. Not knowing exactly what to look for, the strategy is to build a model based on the dataset that is pre-processed and normalized into numerical or binary features.

Most of the users and domains are anonymized, and there isn't a clear relationship between the various types and orientations. This means that these data elements should be normalized into large vectors with binary features. The only adjustment to this is to split the two user@domain fields into the user and the domain. Since the user information is in some manner redundant with the computer information, it is ignored unless it contains network information (i.e. user=ANONYMOUS LOGON).

The final data element is the timestamp. This value is approximately continuous, but it doesn't mean much if it is used as a strictly increasing value. To make it more useful, the timestamp is replaced by the number of seconds since the last authentication attempt by the given user.  

### Model
The current best performing model is a Random Forest classifier with weighted classes. Because of the sparsity of authentication failures, we add weights to the classes based on the inverse of the class frequency in the training set. This is done in an automated way by including the option `class_weight='auto'` when instantiating the Random Forest.  

Running the algorithm on a training set of 80,000 samples and a test set of 20,000 samples yields the following results:
```
Accuracy:  0.99485
Success Recall:  0.99500554939
Success Precision:  0.99979723222
Fail Recall:  0.977528089888
Fail Precision:  0.637362637363
```
The results are very accurate, but they are only useful if they are able to correctly identify the authentication failures. According to the metrics, we are able to correctly identify 97.7% of the failures, but 37% of the samples that were predicted to be failures were actually successes. Because of the relative frequency of failures, this is not a huge number of false positives. However, more work can certainly be done to improve precision of the failure classification. 

### Future Work
One of the requirements for this project was portability; the ability to run and reproduce results on other machines without to much trouble. Further work may include distributing the computation across a cluster so that the model can consume more training data. While doing this will have some amount of overhead in building and configuring cluster, the benefits should be improved performance and improved results.


### Pre-Requisites
Install Python 2.7.X along with the following auxiliary modules:
- numpy==1.10.4
- scikit-learn==0.16.1
- scipy==0.16.1

Download the dataset:
- Go to http://csr.lanl.gov/data/cyber1/ and download auth.txt.gz to you working directory.

### Usage
In the shell (or an IDE), navigate to your working directory containing the authproject.py python script and the auth.txt.gz compressed data file. Enter `python authproject.py`. You will be prompted to enter a quantity of samples for use in the training and testing of the model. Due to the sparsity of failure, results are poor for sample sizes less than 10,000. Depending on the configuration of your machine, choosing sample sizes greater than 1,000,000 can negatively affect performance and speed of completion. 



#####Author: David Wayne

#####Last Updated: 2016-03-28