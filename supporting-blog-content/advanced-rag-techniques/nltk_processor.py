import networkx as nx
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from itertools import combinations
from nltk.corpus import wordnet

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('wordnet')

class NLTKProcessor:
    def __init__(self):
        pass

    def get_word_pos(self, word):
        # Tokenize the word (this step is necessary even for a single word)
        tokens = word_tokenize(word)
        
        # Perform part-of-speech tagging
        tagged = pos_tag(tokens)
        
        # Return the tag (we're assuming there's only one word)
        return tagged[0][1]
    
    def get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return 'a'
        else:
            # As default pos in lemmatization is Noun
            return wordnet.NOUN
        
    def split_into_sentences(self, text):
        return sent_tokenize(text)
        
    def textrank_phrases(self, text, top_n=10, phrase_length=3, mode='phrase'):
        lemmatizer = WordNetLemmatizer()

        # Tokenize the text into sentences
        sentences = sent_tokenize(text)

        # Tokenize sentences into words and remove stopwords
        stop_words = set(stopwords.words('english'))
        words = [word_tokenize(sentence.lower()) for sentence in sentences]
        words = [[lemmatizer.lemmatize(word, pos=self.get_wordnet_pos(self.get_word_pos(word))) for word in sentence if word.isalnum() and word not in stop_words] for sentence in words]

        # Part-of-speech tagging
        tagged = [pos_tag(sentence) for sentence in words]

        # Extract nouns and adjectives
        if mode == 'phrase':
            keywords = [[word for word, pos in sentence if pos.startswith('NN') or pos.startswith('JJ')] for sentence in tagged]
        else:  # mode == 'sentence'
            keywords = [' '.join(sentence) for sentence in words]

        # Generate phrases
        if mode == 'phrase':
            phrases = []
            for sentence in keywords:
                phrases.extend([' '.join(phrase) for phrase in zip(*[sentence[i:] for i in range(phrase_length)])])
        else:
            phrases = keywords

        # Build the graph
        graph = nx.Graph()
        if mode == 'phrase':
            # For phrases, use co-occurrence within sentences
            for sentence_phrases in [phrases[i:i+len(keywords[j])-phrase_length+1] for j, i in enumerate([sum(len(k)-phrase_length+1 for k in keywords[:j]) for j in range(len(keywords))])]:
                for pair in combinations(sentence_phrases, 2):
                    if graph.has_edge(*pair):
                        graph[pair[0]][pair[1]]['weight'] += 1
                    else:
                        graph.add_edge(*pair, weight=1)
        else:
            # For sentences, use similarity between sentences
            for pair in combinations(range(len(phrases)), 2):
                similarity = len(set(phrases[pair[0]].split()) & set(phrases[pair[1]].split())) / \
                            (len(set(phrases[pair[0]].split()) | set(phrases[pair[1]].split())) + 1e-6)
                if similarity > 0:
                    graph.add_edge(pair[0], pair[1], weight=similarity)

        # Apply PageRank
        scores = nx.pagerank(graph)

        # Sort by score and return top n
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if mode == 'phrase':
            return [item for item, score in sorted_items[:top_n]]
        else:
            return [sentences[idx] for idx, score in sorted_items[:top_n]]