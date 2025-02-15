import pytest

from streamScript.domain.query_db import query_all_db_Tweet200
from streamScript.domain.query_db import read_in_bb_file
from streamScript.domain.create_classifier import build_matrix_per_user
from streamScript.domain.create_classifier import fit_classifier, vectorize
from streamScript.domain.picklers import pickle_handling

slow = pytest.mark.slow


def test_read_in_bb_file():
    with open("text/bounding_boxes.txt", 'r') as f:
        bbs = f.readlines()
    bb_dict = read_in_bb_file()
    assert len(bbs) == len(bb_dict)


@slow
def test_query_all_db_Tweet200():
    data_set = query_all_db_Tweet200()
    bb_dict = read_in_bb_file()
    pickle_handling.write_pickle(data_set, 'data_set', test=True)
    assert len(bb_dict) == len(data_set)


# Test that the val of each key is apprx the same length

@slow
def test_build_matrix_per_user_array_len_match():
    try:
        data_set = pickle_handling.load_pickle('data_set', test=True)
    except IOError:
        data_set = query_all_db_Tweet200()
        pickle_handling.write_pickle(data_set, 'data_set', test=True)
    user_matrix, user_array, n = build_matrix_per_user(data_set)
    assert len(user_array) == len(user_matrix)


@slow
def test_build_matrix_per_user_array_user_len():
    u"""This test asserts that less than 1 percent of our users
    have less that 5000 characters in their tweet histories."""
    try:
        data_set = pickle_handling.load_pickle('data_set', test=True)
    except IOError:
        data_set = query_all_db_Tweet200()
        pickle_handling.write_pickle(data_set, 'data_set', test=True)
    user_matrix, user_array, n = build_matrix_per_user(data_set)
    count = 0
    for user in user_matrix:
        if len(user) <= 5000:
            count += 1
    assert count <= len(user_matrix) / 100

@slow
def test_vectorize_with_200():
    try:
        data_set = pickle_handling.load_pickle('data_set', test=True)
    except IOError:
        data_set = query_all_db_Tweet200()
        pickle_handling.write_pickle(data_set, 'data_set', test=True)
    user_matrix, user_array, n = build_matrix_per_user(data_set)
    X, y, vocab = vectorize(user_matrix, user_array, n)
    assert len(X) == len(y)

@slow
def test_fit_with_200():
    try:
        data_set = pickle_handling.load_pickle('data_set', test=True)
    except IOError:
        data_set = query_all_db_Tweet200()
        pickle_handling.write_pickle(data_set, 'data_set', test=True)
    user_matrix, user_array, n = build_matrix_per_user(data_set)
    X, y, vocab = vectorize(user_matrix, user_array, n)
    clf = fit_classifier(X, y)
    assert clf.get_params()['alpha'] == 1.0
    assert clf.get_params()['fit_prior'] is True
    assert not clf.get_params()['class_prior']

if __name__ == '__main__':
    test_build_matrix_per_user_array_user_len()
