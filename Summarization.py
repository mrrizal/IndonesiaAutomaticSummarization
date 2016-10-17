import nltk.data

class Summarization(object):

	def getSentence(self, text):
		tokenizer = nltk.data.load('tokenizers/punkt/PY3/indonesia.pickle')
		sentences = tokenizer.tokenize(text)
		return sentences

# file = open('test.txt', 'r')
# data = file.read()
# print(data)
# summary = Summarization()
# sentences = summary.getSentence(data)
# print(sentences[0])
