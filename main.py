from flask import Flask, render_template, request, jsonify, session
from werkzeug import secure_filename
from Converter import Converter
from Summarization import Summarization
from numpy import absolute
app = Flask(__name__)
app.secret_key = 'rizalGanteng'

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/settings', methods = ['GET', 'POST'])
def settings():
	if request.is_xhr:
		if request.form is not None:
			session['ratio'] = abs(int(round(float(request.form['ratio']))))
			session['dtm'] = request.form['dtm']
			session['sentenceSelection'] = request.form['sentenceSelection']
			session['formatFile'] = request.form['formatFile']
			print(session)
			return 'sukses'
		return 'sukses'
	return 'sukses'

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
	if request.is_xhr:
		if request.files is not None:
			f = request.files['file']
			filename = f.filename
			if filename.endswith('.txt'):
				return f.read().decode('utf-8')
			elif filename.endswith('.pdf'):
				# call converter class
				data = Converter()
				result = data.pdfToText(f)
				if result != "":
					return result
				return "Convert to plain text failed"
			elif filename.endswith('.docx'):
				data = Converter()
				result = data.docxToText(f)
				if result != "":
					return result
				return "Convert to plain text failed"
			elif filename.endswith('.odt'):
				data = Converter()
				result = data.odtToText(f)
				if result != "":
					return result
				return "Convert to plain text failed"
			else:
				return "tes"
		else:
			return "upload failed"
	return 'request is not ajax'

@app.route('/summarization', methods = ['GET', 'POST'])
def summarization():
	if request.is_xhr:
		# untuk setting
		ratio = session['ratio'] if 'ratio' in session else 50
		dtmMethod = session['dtm'] if 'dtm' in session else 'tf'
		sentenceSelectionMethod = session['sentenceSelection'] if 'sentenceSelection' in session else 'SteinbergerJezek2'
		if dtmMethod == 'boolean':
			dtmMethod = 'tf'
			binary = True
		else :
			binary = False
		
		summary = Summarization()
		sentences = summary.getSentence(request.form['text'])
		if len(sentences) < 3:
			return "Sorry, at least 3 sentences ..."
		dtm = summary.getDTM(sentences, binaryMode=binary, mode=dtmMethod)
		u, sigma, vt = summary.getSVD(dtm, sentences)
		keys = summary.getSummary(sigma=absolute(sigma), vt=absolute(vt).tolist(), approach=sentenceSelectionMethod, aspectRatio=ratio).keys()
		keys = sorted(keys)
		summaryResult = []
		for key in keys:
			try:
				summaryResult.append(sentences[key])
			except:
				pass
		
		result = "\n".join(summaryResult)
		return result
	return "request is not ajax"
	
if __name__ == "__main__":
	app.run(debug=True,threaded=True)
