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
    for i in range(n - 1):
        s.append(data[inds[i]:inds[i + 1]])
    s.append(data[inds[n - 1]:])
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

    pos_data = read_data_train(train_file_name + '.txt')
    sent_inds = read_data_ind(train_file_name + '.ind')

    ####################
    n = len(sent_inds)
    prior = np.zeros(N_tags)
    transition = np.zeros((N_tags, N_tags))
    emission = {}
    sentences = split_data(pos_data, sent_inds)
    # temp = [0] * N_tags

    for sentence in sentences:
        for i in range(N_tags):
            if sentence[0][1] == UNIVERSAL_TAGS[i]:
                prior[i] = prior[i] + 1
    prior = np.divide(prior, n)
    prior = np.log(prior)

    lens = np.zeros(N_tags)

    for sentence in sentences:
        for i in range(len(sentence) - 1):
            tag1 = sentence[i][1]
            tag2 = sentence[i + 1][1]
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
                transition[i][j] = np.log(transition[i][j] / lens[i])
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
        emission[key] = np.log(emission[key] / lengths[key[0]])

    return prior, transition, emission
    ####################

    # return prior, transition, emission
    return None


def tag(train_file_name, test_file_name):
    """
    Train your HMM model, run it on the test data, and finally output the tags.

    Your code should write the output tags to (test_file_name).pred, where each line contains a POS tag as in UNIVERSAL_TAGS
    """

    prior, transition, emission = train_HMM(train_file_name)

    pos_data = read_data_test(test_file_name + '.txt')
    sent_inds = read_data_ind(test_file_name + '.ind')

    ####################
    # STUDENT CODE HERE
    ####################


    start = time.time()

    next_sent_inds = 1

    probability_saved = [[] for z in range(len(UNIVERSAL_TAGS))]
    results = []
    is_last = False

    for i in range(len(pos_data)):

        # If i == nex_sent_inds, then this is a new start of a sentence
        if not is_last and i == sent_inds[next_sent_inds]:
            # BUG is around here! regarding i! When i is stopping to calculate?

            if next_sent_inds == len(sent_inds) - 1:
                is_last = True
            else:
                next_sent_inds += 1

            # Append everything to the file if finished the first sentence
            if next_sent_inds > 1:
                # Find the best path
                max_index = 0

                for j in range(len(probability_saved)):
                    if probability_saved[j][0] > probability_saved[max_index][0]:
                        max_index = j

                for j in range(1, len(probability_saved[max_index]), 1):
                    curr_indx = probability_saved[max_index][j]
                    results.append(UNIVERSAL_TAGS[curr_indx])

            # Restore all probabilities_saved
            probability_saved = [[] for z in range(len(UNIVERSAL_TAGS))]
            # print(len(results))

            # Find the highest probability of being this word at the front
            for j in range(len(UNIVERSAL_TAGS)):
                probability_saved[j] = [[]]

                # Replace with the
                if (UNIVERSAL_TAGS[j], pos_data[i]) not in emission.keys():
                    probability_saved[j][0] = np.double(prior[j] + (10**(-10)))  ## NOTE HERE
                else:
                    probability_saved[j][0] = np.double(prior[j] + emission[(UNIVERSAL_TAGS[j], pos_data[i])])
                probability_saved[j].append(j)

        else:
            # Initialize if current is the first sentence
            if i == 0:
                # Find the highest probability of being this word at the front
                for j in range(len(UNIVERSAL_TAGS)):
                    probability_saved[j] = [[]]

                    if (UNIVERSAL_TAGS[j], pos_data[i]) not in emission.keys():
                        emission[(UNIVERSAL_TAGS[j], pos_data[i])] = 10**(-10)
                        probability_saved[j][0] = np.double(prior[j] + 10**(-10))  ## NOTE HERE
                    else:
                        probability_saved[j][0] = np.double(prior[j] + emission[(UNIVERSAL_TAGS[j], pos_data[i])])
                    probability_saved[j].append(j)

            else:
                # pos_data[i] is not one of the starting of the sentence
                # print(probability_saved)
                for j in range(len(probability_saved)):
                    all_prob = []
                    all_prob_inds = []
                    for k in range(len(UNIVERSAL_TAGS)):

                        curr_prob = probability_saved[j][0]

                        curr_prob += transition[j][k]

                        if (UNIVERSAL_TAGS[k], pos_data[i]) not in emission.keys():
                            curr_prob += 10**(-10)## NOTE HERE
                        else:
                            curr_prob += np.double(emission[(UNIVERSAL_TAGS[k], pos_data[i])])

                        all_prob.append(curr_prob)
                        all_prob_inds.append(k)

                    all_prob = list(enumerate(all_prob))
                    max_pair = max(all_prob, key=(lambda x: x[1]))  # max_pair is (max_values_index, value)

                    #print(np.array(probability_saved))
                    # print(len(probability_saved))
                    # print(j)
                    probability_saved[j][0] = max_pair[1]
                    probability_saved[j].append(max_pair[0])

    # print(len(results))
    # For the last sentence only
    # Find the best path
    max_index = 0
    for j in range(len(probability_saved)):
        if probability_saved[j][0] > probability_saved[max_index][0]:
            max_index = j

    for j in range(1, len(probability_saved[max_index]), 1):
        curr_indx = probability_saved[max_index][j]
        # print(curr_indx)
        results.append(UNIVERSAL_TAGS[curr_indx])

    # print(len(results))

    end = time.time()

    print(end-start)
    # print(results)
    write_results(test_file_name + '.pred', results)

if __name__ == '__main__':
    # Run the tagger function.
    print("Starting the tagging process.")

    # Tagger expects the input call: "python3 tagger.py -d <training file> -t <test file>"
    # E.g. python3 tagger.py -d data/train-public -t data/test-public-small
    t = time.time()
    parameters = sys.argv
    train_file_name = parameters[parameters.index("-d") + 1]
    test_file_name = parameters[parameters.index("-t") + 1]

    # Start the training and tagging operation.
    tag(train_file_name, test_file_name)
    print(time.time() - t)