# The tagger.py starter code for CSC384 A4.
import os
import sys
import time
import numpy as np
from collections import Counter

UNIVERSAL_TAGS = [
    "VERB",
    "NOUN",
    "PRON",
    "ADJ",
    "ADV",
    "ADP",
    "CONJ",
    "DET",
    "NUM",
    "PRT",
    "X",
    ".",
]

N_tags = len(UNIVERSAL_TAGS)

def read_data_train(path):
    return [tuple(line.split(' : ')) for line in open(path, 'r').read().split('\n')[:-1]]

def read_data_test(path):
    return open(path, 'r').read().split('\n')[:-1]

def read_data_ind(path):
    return [int(line) for line in open(path, 'r').read().split('\n')[:-1]]

def write_results(path, results):
    with open(path, 'w') as f:
        f.write('\n'.join(results))

def split_data(data, inds):
    s = []
    n = len(inds)
    for i in range(n-1):
        s.append(data[inds[i]:inds[i+1]])
    s.append(data[inds[n-1]:])
    return s

def train_HMM(train_file_name):
    """
    Estimate HMM parameters from the provided training data.

    Input: Name of the training files. Two files are provided to you:
            - file_name.txt: Each line contains a pair of word and its Part-of-Speech (POS) tag
            - fila_name.ind: The i'th line contains an integer denoting the starting index of the i'th sentence in the text-POS data above

    Output: Three pieces of HMM parameters stored in LOG PROBABILITIES :
 
            - prior:        - An array of size N_tags
                            - Each entry corresponds to the prior log probability of seeing the i'th tag in UNIVERSAL_TAGS at the beginning of a sequence
                            - i.e. prior[i] = log P(tag_i)

            - transition:   - A 2D-array of size (N_tags, N_tags)
                            - The (i,j)'th entry stores the log probablity of seeing the j'th tag given it is a transition coming from the i'th tag in UNIVERSAL_TAGS
                            - i.e. transition[i, j] = log P(tag_j|tag_i)

            - emission:     - A dictionary type containing tuples of (str, str) as keys
                            - Each key in the dictionary refers to a (TAG, WORD) pair
                            - The TAG must be an element of UNIVERSAL_TAGS, however the WORD can be anything that appears in the training data
                            - The value corresponding to the (TAG, WORD) key pair is the log probability of observing WORD given a TAG
                            - i.e. emission[(tag, word)] = log P(word|tag)
                            - If a particular (TAG, WORD) pair has never appeared in the training data, then the key (TAG, WORD) should not exist.

    Hints: 1. Think about what should be done when you encounter those unseen emission entries during deccoding.
           2. You may find Python's builtin Counter object to be particularly useful 
    """

    pos_data = read_data_train(train_file_name+'.txt')
    sent_inds = read_data_ind(train_file_name+'.ind')

    ####################
    n = len(sent_inds)
    prior = np.zeros(N_tags)
    transition = np.zeros((N_tags, N_tags))
    emission = {}
    sentences = split_data(pos_data, sent_inds)
    #temp = [0] * N_tags

    for sentence in sentences:
        for i in range(N_tags):
            if sentence[0][1] == UNIVERSAL_TAGS[i]:
                prior[i] = prior[i] + 1
    prior = np.divide(prior, n)
    prior = np.log(prior)

    lens = np.zeros(N_tags)

    for sentence in sentences:
        for i in range(len(sentence)-1):
            tag1 = sentence[i][1]
            tag2 = sentence[i+1][1]
            for j in range(N_tags):
                if UNIVERSAL_TAGS[j] == tag1:
                    lens[j] += 1
                    ind1 = j
                if UNIVERSAL_TAGS[j] == tag2:
                    ind2 = j
            transition[ind1][ind2] += 1
    for i in range(N_tags):
        for j in range(N_tags):
            if transition[i][j] != 0:
                transition[i][j] = np.log(transition[i][j]/lens[i])
            else:
                transition[i][j] = float('-inf')

    lengths = {}
    for tag in UNIVERSAL_TAGS:
        lengths[tag] = 0

    for sentence in sentences:
        for item in sentence:
            tup = (item[1], item[0])
            lengths[item[1]] = lengths[item[1]] + 1
            if tup in emission:
                emission[tup] += 1
            else:
                emission[tup] = 1
    for key in emission.keys():
        emission[key] = np.log(emission[key]/lengths[key[0]])

    return prior, transition, emission
    ####################


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name+'.txt')
    sent_inds = read_data_ind(test_file_name+'.ind')

    ####################
    sentences = split_data(pos_data, sent_inds)
    results = []
    eps = np.log(10**-11)
    for sentence in sentences:
        len_s = len(sentence)
        prob_trellis = np.zeros((N_tags, len_s))
        path_trellis = np.zeros((N_tags, len_s), dtype=object)
        for s in range(N_tags):
            if (UNIVERSAL_TAGS[s],sentence[0]) in emission:
                value = emission[(UNIVERSAL_TAGS[s], sentence[0])]
            else:
                value = eps
            prob_trellis[s][0] = prior[s] + value
            path_trellis[s][0] = [s]
        for o in range(1, len_s):
            for s in range(N_tags):
                if (UNIVERSAL_TAGS[s], sentence[o]) in emission:
                    value = emission[(UNIVERSAL_TAGS[s], sentence[o])]
                else:
                    value = eps
                sum = prob_trellis[:, o-1] + np.array(transition)[:, s]
                x = np.argmax(sum)
                prob_trellis[s][o] = sum[x] + value
                path_trellis[s][o] = path_trellis[x][o-1]+[s]
        column = prob_trellis[:, len_s-1]
        ind = np.argmax(column)
        path = path_trellis[ind][len_s-1]
        for item in path:
            results.append(UNIVERSAL_TAGS[item])
    ####################
    write_results(test_file_name+'.pred', results)

if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    t = time.time()
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d")+1]
    test_file_name = parameters[parameters.index("-t")+1]

    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)
    print(time.time()-t)