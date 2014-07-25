import numpy as np

from sklearn.feature_extraction.text import CountVectorizer as CV
from sklearn.naive_bayes import MultinomialNB as MNB

from streamScript.domain.send_data import query_all_db, query_all_db_Tweet200, read_in_bb_file
import picklers

u"""Generates a vocabulary
set and builds a feature matrix. Creates a classifier and returns
cross-validated predictions. Pickles dataset and matrix as necessary."""


def check_city_locations(location_lat, location_lng):
    bb_dict = read_in_bb_file()
    for city, values in bb_dict.items():
        if (values[0][0] < location_lat < values[0][1]) and \
                values[1][0] < location_lng < values[1][1]:
            return city, values


def build_test_matrix(history, vocab):
    u"""Takes in a list of lists, with each list containing tuples
    representing tweets from a single user, and a vocab list. Returns an X
    matrix of the test user features, a list of the user names, and a Y
    array of the labels."""
    matrix = []
    user_array = []
    user_cities = []
    user_string = ""
    user_name = history[0][0]
    user_array.append(user_name)
    if history[0][2] and history[0][3]:
        actual = check_city_locations(history[0][2], history[0][3])
        user_cities.append(actual)
    else:
        user_cities.append(history[0][5])
    for tweet in history:
        if history[0][0] == user_name:
            user_string += tweet[1].lower()
    matrix.append(user_string)
    vec = CV(
        analyzer='word',
        vocabulary=vocab
    )
    print "Building test X, Y..."
    X = vec.fit_transform(matrix, vocab).todense()
    return X, user_array, user_cities


def vectorize(user_matrix, user_array, n):
    stopwords = open('text/stopwords.txt').read().lower().split()
    vec = CV(
        analyzer='word',
        stop_words=stopwords,
        max_features=n,
    )
    print "Building X, Y..."
    X = vec.fit_transform(user_matrix).toarray()
    Y = np.array(user_array)
    return X, Y, vec.get_feature_names()


def build_matrix(data, n=1000):
    u"""Uses blocks of tweets from multiple users per city.
    Takes in a raw dataset and an optional parameter to limit the feature
    set to n. Defaults to 1000. Returns a tuple containing a matrix of n features,
    a vector of labels, and a vocabulary list of the features examined."""
    user_matrix = []
    user_array = []
    tweet_count = 0
    for key, val in data.items():
        for tweet in val:
            if not tweet_count % 200:
                user_array.append(key)
                user_matrix.append(" ")
            user_matrix[-1] += tweet[2].lower()
            tweet_count += 1
    return user_matrix, user_array, n


def build_matrix_per_user(data, n=1000):
    u""" Uses blocks of tweets from single users per city.
    Takes in a raw dataset and an optional parameter to limit the feature
    set to n. Defaults to 1000. Returns a tuple containing a matrix of n features,
    a vector of labels, and a vocabulary list of the features examined."""
    user_matrix = []
    user_array = []
    for key, val in data.items():
        count = 0
        for tweet in val:
            if count == 0:
                this_user = tweet[0]
                our_string = ""
            if (tweet[0] == this_user) and (count < 200):
                our_string += tweet[2].lower()
                count += 1
            elif (tweet[0] != this_user) and (len(user_matrix[-1]) >= 14000):
                count = 0
                user_matrix.append(our_string)
                user_array.append(key)
            elif tweet[0] != this_user:
                count = 0
    return user_matrix, user_array, n


def fit_classifier(X, y):
    u"""Takes in an X matrix and a Y array of labels.
    Fits classifier"""
    mnb = MNB()
    return mnb.fit(X, y)


def get_raw_classifier(make_new_pickles=False, read_pickles=True, useTweet200=False):
    u"""Takes in keyword arguments to determine source of data. Returns a
    trained classifier."""
    if read_pickles:
        X = picklers.load_pickle('matrix_pickle')
        y = picklers.load_pickle('labels_pickle')
    else:
        if useTweet200:
            data = query_all_db_Tweet200()
            user_matrix, user_array, n = build_matrix_per_user(data)
        else:
            data = query_all_db(limit=True)
            user_matrix, user_array, n = build_matrix(data)
        X, y, vocab = vectorize(user_matrix, user_array, n)
    mnb = fit_classifier(X, y)
    if make_new_pickles:
        picklers.write_pickle(mnb, 'classifier_pickle')
        if not read_pickles:
            picklers.write_pickle(data, 'pickle')
            picklers.write_pickle(X, 'matrix_pickle')
            picklers.write_pickle(y, 'labels_pickle')
            picklers.write_pickle(vocab, 'vocab_pickle')
    print "returning mnb"
    return mnb


def generate_predictions(userTestdata):
    u"""Takes in a list of twitter users' last 200 tweets, formatted as
    'blobs'. Returns a percent correct (if known), a list of all incorrect
    guesses (or unknown), and a list of all the city predictions."""
    mnb = picklers.load_pickle('classifier_pickle')
    vocab = picklers.load_pickle('vocab_pickle')
    X, user_array, user_cities = build_test_matrix(userTestdata, vocab)
    correct = 0
    incorrect = 0
    got_wrong = []
    all_results = []
    predictions = mnb.predict(X)
    print user_array
    print user_cities
    if len(predictions):
        for idx, prediction in enumerate(predictions):
            report = (user_array[idx], user_cities[idx], prediction)
            if user_cities[idx] == prediction:
                correct += 1
            else:
                incorrect += 1
                got_wrong.append(report)
            all_results.append(report)
        percent_right = correct / (float(correct) + incorrect)
        return percent_right, got_wrong, all_results, user_cities

if __name__ == "__main__":
    print get_raw_classifier(make_new_pickles=True, read_pickles=False, useTweet200=False)
