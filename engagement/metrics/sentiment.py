import nltk.classify.util
#nltk.download('movie_reviews')
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews

def extract_features(word_list):
    return dict([(word,True) for word in word_list]) 

## trains sentiment classifier
def sentiment_train():
    pos_fileID = movie_reviews.fileids('pos')
    neg_fileID = movie_reviews.fileids('neg')
    
    pos_features = [(extract_features(movie_reviews.words(fileids=[f])), 'Positive') for f in pos_fileID]
    neg_features = [(extract_features(movie_reviews.words(fileids=[f])), 'Negative') for f in neg_fileID]
    
    threshold = 0.8
    threshold_pos = int(threshold * len(pos_features))
    threshold_neg = int(threshold * len(neg_features))
    
    train_features = pos_features[:threshold_pos] + neg_features[:threshold_neg]
    test_features = pos_features[threshold_pos:] + neg_features[threshold_neg:]
    
    classifier = NaiveBayesClassifier.train(train_features)

    return classifier

## extracts sentiment using trained classifier           
def sentiment_extract(text, classifier):
    probDist = classifier.prob_classify(extract_features(text.split()))
    sentiment_pred = probDist.max()
    sentiment_prob = round(probDist.prob(sentiment_pred), 2)

    return sentiment_pred, sentiment_prob

## runs sentiment script
def sentiment_run(text):
    classifier = sentiment_train()
    sentiment_pred, sentiment_prob = sentiment_extract(text, classifier)
    
    return sentiment_pred, sentiment_prob
    