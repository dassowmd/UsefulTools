import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer(analyzer = "word",   \
                             tokenizer = None,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             min_df = 0,          \
                             max_features = 50)

text = raw_input("Please enter the text you would like counted\n")
text = [text]

# Count
train_data_features = vectorizer.fit_transform(text)
vocab = vectorizer.get_feature_names()

# Sum up the counts of each vocabulary word
dist = np.sum(train_data_features.toarray(), axis=0)

# For each, print the vocabulary word and the number of times it
# appears in the training set
for tag, count in zip(vocab, dist):
    print count, tag