import nltk.corpus
from nltk.corpus import stopwords
import json
import argparse
from collections import Counter
import random

class Corpus():
    def __init__(self, args):
        self.documents = {}
        self.document_id = 0

        self.documents['docs'] = {}
        self.documents['top_100'] = []
        self.documents['details'] = {}

        self.all_words = []
        self.thresholded_words = []

        self.num_peers = args.num_peers

    # generate the intial corpus with preprocessed documents
    def generate_corpus(self): 
        penn_treebank = nltk.corpus.treebank

        # preprocess each document
        for index, fileid in enumerate(penn_treebank.fileids()):
            doc = penn_treebank.words(fileids=fileid) # using penn treebank
            words = [word.lower() for word in doc if word.isalpha()]
            filtered_words = [word for word in words if word not in stopwords.words('english')]

            self.all_words.extend(filtered_words)

            self.documents['docs']['Doc_' + str(self.document_id)] = filtered_words
            self.document_id += 1

    # choose words that occur at least 5 times in entire corpus
    def threshold(self, threshold_num):
        counter = Counter(self.all_words)

        documents = self.documents['docs']
        for doc in documents:
            documents[doc] = [word for word in documents[doc] if counter[word] >= threshold_num]

            self.thresholded_words.extend(documents[doc])

    # generate top 100 words from which we will synthesize queries
    def generate_top_100(self):
        counter = Counter(self.thresholded_words)

        # details about document dimension and num_docs
        self.documents['details']['dimension'] = len(counter)
        self.documents['details']['num_docs'] = len(self.documents['docs'])

        self.documents['top_100'] = [elem[0] for elem in counter.most_common(100)]

    def export(self, file_name):
        with open(file_name, "w") as f:
            json.dump(self.documents, f, indent=4)

    def random_distribute(self, graph_input, graph_output):
        document_ids = list(self.documents['docs'].keys()) # shuffle documents
        random.shuffle(document_ids)

        # assign documents to nodes 
        node_num_with_docs = {}
        idx = 0
        for doc in document_ids:
            node_num_with_docs[idx % 50] = node_num_with_docs.get(idx % 50, [])
            node_num_with_docs[idx % 50].append(doc)

            idx += 1

        final_node_with_docs = []
        # update graph_ks_nodes to include node and doc info at the same time
        with open(graph_input) as f:
            graph_ks = json.load(f)
            for i, node in enumerate(node_num_with_docs.keys()):
                graph_details = graph_ks[i]
                graph_details['docs'] = node_num_with_docs[node]

                final_node_with_docs.append(graph_details)

        # node with documents file
        with open(graph_output, "w") as f:
            json.dump(final_node_with_docs, f, indent=4)


def parse():
    # instantiate a ArgumentParser object
    parser = argparse.ArgumentParser(description="Create document corpus.")

    parser.add_argument("-f", "--file_name", type=str,
                        default="documents.json", help="Output file containing list of documents and document ids")

    parser.add_argument("-gi", "--graph_input", type=str,
                        default="graph_ks.json", help="Input file containing node links")

    parser.add_argument("-go", "--graph_output", type=str,
                        default="graph_ks_docs.json", help="Output file containing node links and document ids")

    parser.add_argument("-n", "--num_peers", type=int,
                        default="50", help="Number of peers that we will randomly distribute documents to")

    parser.add_argument("-t", "--threshold_num", type=int,
                        default="5", help="Minimum frequency in corpus required to be used in final set")

    return parser.parse_args()

def main():
    try:
        args = parse()

        # generate documents with document ids 
        corpus = Corpus()
        corpus.generate_corpus()
        corpus.threshold(args.threshold_num)
        corpus.generate_top_100()

        # export document json 
        corpus.export(args.file_name)

        # use graph json to create graph with node links and document ids
        corpus.random_distribute(args.graph_input, args.graph_output)

    except Exception as e:
        print("Exception caught in main - {}".format(e))
        return

if __name__ == "__main__":
    main()