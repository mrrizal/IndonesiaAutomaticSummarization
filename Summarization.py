import nltk.data
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
import pandas as pd
from numpy import linalg, sqrt, absolute
from stem import IndonesianStemmer 

class Summarization(object):

	def getSentence(self, text):
		tokenizer = nltk.data.load('tokenizers/punkt/PY3/indonesia.pickle')
		sentences = tokenizer.tokenize(text)
		return sentences

	# stemming
	def stemmed_words(self, doc):
		stemmer = IndonesianStemmer() 
		return (stemmer.stem(w) for w in self.stopWordIndonesia(doc))

	# remove stop word (indonesia stop word)
	def stopWordIndonesia(self, doc):
		analyzer = CountVectorizer().build_analyzer()
		f = open('static/stopwords_id.txt')
		stopwords = [word.rstrip('\n') for word in f.readlines()]
		return (word for word in analyzer(doc) if word not in stopwords)
	
	def getDTM(self, sentences, binaryMode=False, mode='tfidf'):
		if(mode=='tf'):
			self.vectorize = CountVectorizer(min_df=0.0, analyzer=self.stemmed_words, binary=binaryMode, max_df=1.0)
		elif(mode=='tfidf'):
			self.vectorize = TfidfVectorizer(min_df=0.0, analyzer=self.stemmed_words, max_df=1.0)
		
		dtm = self.vectorize.fit_transform(sentences)
		# print(pd.DataFrame(dtm.toarray(), index=sentences, columns=self.vectorize.get_feature_names()))
		# print()
		return dtm

	def getSVD(self, documentTermMatrix, sentences):
		try :
			lsa = TruncatedSVD(len(sentences), algorithm='randomized')
		except :
			lsa = TruncatedSVD(100, algorithm='randomized')

		dtm_lsa = lsa.fit_transform(documentTermMatrix)
		dtm_lsa = Normalizer(copy=False).fit_transform(dtm_lsa)
		u = lsa.components_.T
		sigma = lsa.explained_variance_ratio_
		vt = dtm_lsa.T
		return u, sigma, vt

	'''
	sentences selection
	bisa menggunakan 3 metode:
	1. GongLiu 
	2. SteinbergerJezek
	3. cross
	aspect ration digunakan untuk mengatur berapa banyak kalimat di ambil (dalam %)
	contoh 50 -> berarti 50% kalimat diambil
	lebih jelas mengenai senten selection bisa dilihat di 
	https://www.researchgate.net/publication/220195824_Text_summarization_using_Latent_Semantic_Analysis
	'''
	def getSummary(self, u=0, sigma=0, vt=0, approach='GongLiu', aspectRatio=50):
		value = {}
				
		self.aspectRatio = int((aspectRatio/100)*len(vt))

		if(len(vt)>=3):
			# metode milik Gong dan Liu
			if approach == 'GongLiu':
				# banyaknya kalimat yang di ambil
				for i in range(self.aspectRatio): 
					maxvalue = 0
					index = 0
					index1 = 0
					for i in range(len(vt)):
						for j in range(len(vt[i])):
							if vt[i][j] > maxvalue:
								maxvalue = vt[i][j]
								index = i
								index1 = j
					vt[index][index1] = 0
					value[index1] = maxvalue

			# metode milik Steinberger dan Jezek
			elif approach == 'SteinbergerJezek':
				for i in range(len(vt)):
					vt[i].append(sqrt(sum([vt[i][j]*sigma[i] for j in range(len(vt[i]))])))

				# print(pd.DataFrame(vt, index=[i+1 for i in range(len(vt))], columns=[i+1 for i in range(len(vt)+1)]))

				data = []
				for i in range(len(vt)):
					data.append(vt[i][len(vt[i])-1])
					
				# banyaknya kalimat yang di ambil
				for i in range(self.aspectRatio): 
					value[data.index(max(data))] = max(data)
					data[data.index(max(data))] = 0

			# copied from summy
			elif approach == 'SteinbergerJezek2':
				MIN_DIMENSIONS = 3
				REDUCTION_RATIO = 1/1
				dimensions = max(MIN_DIMENSIONS,int(len(sigma)*REDUCTION_RATIO))
				powered_sigma = tuple(s**2 if i < dimensions else 0.0 for i, s in enumerate(sigma))
				data = []

				for column_vector in vt:
					tmp = sum(s*v**2 for s, v in zip(powered_sigma, column_vector))
					data.append(sqrt(tmp))
				
				for i in range(self.aspectRatio): 
					value[data.index(max(data))] = max(data)
					data[data.index(max(data))] = 0

			# metode cross 
			elif approach == 'cross':
				lengthOfSentences = [0 for i in range(len(vt))]
				for i in range(len(vt)):
					average = sum(vt[i])/len(vt[i])
					for j in range(len(vt[i])):
						if vt[i][j] < average:
							vt[i][j] = 0
					vt[i].append(average)
					tmp = vt[i][:-1]
					lengthOfSentences = [sum(y) for y in zip([tmp[x]*sigma[x] for x in range(len(tmp))], lengthOfSentences)]
					# print(vt[i])

				vt.append(lengthOfSentences)
				# for i in range(len(vt)):
				# 	print(vt[i])
				data = vt[len(vt)-1]

				# banyak kalimat yang di pilih
				for i in range(self.aspectRatio):
					value[data.index(max(data))] = max(data)
					data[data.index(max(data))] = 0

		else:
			value[0] = 0
			value[1] = 0

		return value

	# untuk evaluation main topic
	def getEvaluationMainTopic(self, ue, uf):
		evaluation = []
		for i in range(len(ue)):
			try:
				evaluation.append(abs(ue[i]*uf[i]))
			except IndexError:
				pass

		return sum(evaluation) 

	# untuk evaluation term significace
	def getTermVector(self, u, sigma):
		result = []
		for i in range(len(u)):
			result.append(sqrt(sum((j*k)**2 for j, k in zip(absolute(u[i]), absolute(sigma)))))
		return result


# KEU ENGKE GAN
# main program
# def main():
# 	file = open('teks_indonesia.txt', 'r')
# 	data = file.read()

# 	summary = Summarization()
	
# 	sentences = summary.getSentence(data)
# 	dtm = summary.getDTM(sentences, mode='tf')
# 	u, sigma, vt = summary.getSVD(dtm, sentences)
# 	print("Panjang kalimat : %i " % len(sentences))
# 	print("Matrix sigma : %i " % (len(sigma)))
# 	print("Matrix U(mxn) :  %i x %i " % (len(u), len(u[0])))
# 	print("Matrix VT(nxn) : %i x %i " % (len(vt), len(vt[0])))
	
# 	# menampilkan hasil summary
# 	keys = summary.getSummary(sigma=absolute(sigma), vt=absolute(vt).tolist(), approach='SteinbergerJezek2').keys()
# 	keys = sorted(keys)
# 	summaryResult = []
# 	for key in keys:
# 		try:
# 			summaryResult.append(sentences[key])
# 		except:
# 			pass

# 	for i in summaryResult:
# 		print(i)

# 	# print()
# 	# print("Panjang kalimat : %i " % len(sentences))
# 	# print("Matrix sigma : %i " % (len(sigma)))
# 	# print("Matrix U(mxn) :  %i x %i " % (len(u), len(u[0])))

	#  menampilkan hasil evaluasi(lsa-based)
	# dtmSummary = summary.getDTM(summaryResult, mode='CountVectorizer')
	# uSummary, sigmaSummary, vtSummary = summary.getSVD(dtmSummary, summaryResult)
	# evaluation = summary.getEvaluation(sorted(u[0]), sorted(uSummary[0]))
	# print("Evaluation : ", evaluation) 
	
	
	
# 	# print()

# if __name__ == "__main__":
# 	main()	