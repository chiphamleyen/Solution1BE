import pickle
import pandas as pd
import numpy as np
from urllib.parse import urlparse
from sklearn.preprocessing import LabelEncoder

import re
import socket

# Load models
with open("ml_models/cat_model.pkl", "rb") as f:
    cat_model = pickle.load(f)
with open("ml_models/xgb_model.pkl", "rb") as f:
    xgb_model = pickle.load(f)
with open("ml_models/lgb_model.pkl", "rb") as f:
    lgb_model = pickle.load(f)
with open("ml_models/rf_model.pkl", "rb") as f:
    rf_model = pickle.load(f)

def extract_features(url: str):
    features = {}

    parsed = urlparse(url)

    # Feature 1: use_of_ip
    try:
        socket.inet_aton(parsed.netloc)
        features['use_of_ip'] = 1
    except socket.error:
        features['use_of_ip'] = 0

    # Research use whois database to search, not free so remove
    # Feature 2: abnormal_url
    # features['abnormal_url'] = 0

    # Feature 3: suspicious_words
    suspicious_keywords = ['PayPal', 'login', 'signin', 'bank', 'account', 'update', 'bonus', 'ebay']
    features['suspicious_words'] = int(any(word.lower() in url.lower() for word in suspicious_keywords))

    # Feature 4: digit_count
    features['digit_count'] = sum(c.isdigit() for c in url)

    # Feature 5: count_?
    features['count_?'] = url.count('?')

    # Feature 6: count_@
    features['count_@'] = url.count('@')

    # Feature 7: no_of_dir
    features['no_of_dir'] = url.count('/')

    # Feature 8: count-.
    features['count-.'] = url.count('.')

    # Feature 9: count-www
    features['count-www'] = url.count('www')

    # Feature 10: google_index
    # TODO integrate google index API
    # features['google_index'] = 0

    # Feature 11: count_embedded_domain
    features['count_embedded_domain'] = url.count('//')

    # Feature 12: short_url
    shortening_services = r"(bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|tinyurl|tr\.im|is\.gd|cli\.gs|yfrog\.com|migre\.me|ff\.im|tiny\.cc)"
    features['short_url'] = 1 if re.search(shortening_services, url) else 0

    # Feature 13: count_https
    features['count_https'] = url.count('https')

    # Feature 14: count_http
    features['count_http'] = url.count('http')

    # Feature 15: count_%20
    features['count_%20'] = url.count('%20')

    # Feature 16: count_dash
    features['count_dash'] = url.count('-')

    # Feature 17: count_equal
    features['count_equal'] = url.count('=')

    # Feature 18: url_length
    features['url_length'] = len(parsed)

    # Feature 19: hostname_length
    features['hostname_length'] = len(parsed.netloc)

    # Feature 20: first_dir_length
    try:
        features['first_dir_length'] = len(parsed.path.split('/')[1])
    except IndexError:
        features['first_dir_length'] = 0

    # Feature 21: top_level_domain
    try:
        features['top_level_domain'] = parsed.netloc.split('.')[-1]
    except IndexError:
        features['top_level_domain'] = ''

    # Feature 22: count_letters
    features['count_letters'] = sum(c.isalpha() for c in url)

    return features

def label_decoder(label):
    if label == 0:
        return "Benign"
    elif label == 1:
        return "Defacement"
    elif label == 2:
        return "Malware"
    elif label == 3:
        return "Phishing"

def detection_decoder(label):
    if label == "Benign":
        return False
    else:
        return True

def get_prediction(df: pd.DataFrame) -> pd.DataFrame:
    # Preprocess data
    feature_list = []
    for url in df['url']:
        feature_list.append(extract_features(url))
    features_df = pd.DataFrame(feature_list)

    # Encode the 'top level domain' feature
    le = LabelEncoder()
    features_df['top_level_domain'] = le.fit_transform(features_df['top_level_domain'])

    # Predict using all models
    cat_preds = cat_model.predict(features_df)
    xgb_preds = xgb_model.predict(features_df).reshape(-1, 1)
    lgb_preds = lgb_model.predict(features_df).reshape(-1, 1)

    # Meta input in order of XGBoost, LightGBM, CatBoost
    meta_inputs = np.hstack((xgb_preds, lgb_preds, cat_preds))
    rf_preds = rf_model.predict(meta_inputs)

    # Create result df
    result_df = pd.DataFrame(columns=["url", "detection", "classifier"])
    result_df['url'] = df['url']
    result_df['classifier'] = rf_preds
    
    for i in range(len(result_df)):
        classifier = label_decoder(result_df.loc[i, 'classifier'])
        detection = detection_decoder(classifier)
        result_df.loc[i, 'classifier'] = classifier
        result_df.loc[i, 'detection'] = detection

    return result_df