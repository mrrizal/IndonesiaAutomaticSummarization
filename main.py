from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug import secure_filename
from models.Summarization import Summarization
from models.Converter import Converter
from numpy import absolute, sqrt
import models.models
from models.models import Admin, Evaluation
import sqlalchemy
import hashlib
import math

app = Flask(__name__)
app.secret_key = 'rizalGanteng'

# index
@app.route('/')
def index():
	return render_template('index.html')

# login page 
@app.route('/login', methods = ['GET','POST'])
def login():
	if 'id' in session or 'username' in session or 'superAdmin' in session:
		return redirect(url_for('admin'))
	if 'username' in request.form and 'password' in request.form:
		m = hashlib.md5()
		m.update(request.form['password'].encode('utf-8'))
		username = request.form['username']
		password = m.hexdigest()
		database = models.models.Session()
		admin = database.query(Admin).filter(Admin.username==username).filter(Admin.password==password).all()
		if len(admin) == 1:
			session['id'] = admin[0].id
			session['username'] = admin[0].username
			session['superAdmin'] = admin[0].superAdmin
			return redirect(url_for('admin'))
		else:
			return render_template('admin_page/login.html', errMessage='Invalid Username or Password')
	return render_template('admin_page/login.html')

# logout
@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('login'))

# index admin page
@app.route('/admin')
def admin():
	if 'id' in session and 'username' in session and 'superAdmin' in session:
		return render_template('admin_page/index.html')
	return redirect(url_for('login'))

# evaluation page
@app.route('/admin/evaluation_data')
def evaluation_data():
	if 'id' in session and 'username' in session and 'superAdmin' in session:
		return render_template('admin_page/evaluation_data.html')
	return redirect(url_for('login'))

# page for add admin
@app.route('/admin/add', methods = ['GET', 'POST'])
def add_admin():
	if 'id' in session and 'username' in session and 'superAdmin' in session:
		if session['superAdmin'] != True:
			return redirect(url_for('admin'))

		if request.is_xhr:
			if (request.form is not None and request.form['username'].strip() != "" and request.form['password'].strip() != ""):
				m = hashlib.md5()
				result = {}
				username = request.form['username']
				m.update(request.form['password'].encode('utf-8'))
				password = m.hexdigest()
				superAdmin = True if request.form['superAdmin'] == '1' else False
				try :
					admin = Admin(username=username, password=password, superAdmin=superAdmin)
					database = models.models.Session()
					database.add(admin)
					database.commit()
					result['message'] = 'success'
					result['username'] = request.form['username']
				except sqlalchemy.exc.IntegrityError:
					result ['message'] = 'username already axist'

				return jsonify(result)

		return render_template('admin_page/add.html')
	return redirect(url_for('login'))

# get data admin
@app.route('/admin/dataAdmin', methods=['GET', 'POST'])
def getDataAdmin():
	if 'id' in session and 'username' in session and 'superAdmin' in session:
		if session['superAdmin'] != True:
			return redirect(url_for('admin'))
		
		session['page'] = request.form['page'] if 'page' in request.form else 1
		database = models.models.Session()
		page = session['page']
		
		if 'username' in request.form:
			datas = database.query(Admin).filter(Admin.username.like('%'+request.form['username']+'%')).all()
		else:
			datas = database.query(Admin).limit(10).offset((int(page)-1)*10).all()
		#datas = database.query(Admin).limit(10).offset((int(page)-1)*10).all()
		admin = []
		for data in datas:
			tmp = {}
			tmp['id'] = data.id
			tmp['username'] = data.username
			tmp['superAdmin'] = data.superAdmin
			admin.append(tmp)
		
		return jsonify(admin)
	return redirect(url_for('login'))

# page for show list of admin
@app.route('/admin/admin_data', methods = ['GET', 'POST'])
def admin_data():
	if 'id' in session and 'username' in session and 'superAdmin' in session:
		if session['superAdmin'] != True:
			return redirect(url_for('admin'))
		
		database = models.models.Session()
		totalPage = math.ceil(database.query(Admin).count()/10)
		return render_template('admin_page/admin_data.html', totalPage=totalPage)
	return redirect(url_for('login'))

# for delete admin
@app.route('/admin/delete', methods = ['GET', 'POST'])
def admin_delete():
	if 'id' in session and 'username' in session and 'superAdmin' in session:
		if session['superAdmin'] != True:
			return redirect(url_for('admin'))
		
		if request.is_xhr:
			if request.form is not None and request.form['id'].strip() != "":
				id = request.form['id']
				database = models.models.Session()
				try:
					database.query(Admin).filter(Admin.id==id).delete(synchronize_session=False)
					database.commit()
					return "success"
				except e:
					pass
		return "failed"
	return redirect(url_for('login'))

# setting summarization
@app.route('/settings', methods = ['GET', 'POST'])
def settings():
	if request.is_xhr:
		if request.form is not None:
			session['ratio'] = abs(int(round(float(request.form['ratio']))))
			session['dtm'] = request.form['dtm']
			session['sentenceSelection'] = request.form['sentenceSelection']
			session['formatFile'] = request.form['formatFile']
			if 'id' in session and 'username' in session and 'superAdmin' in session:
				session['evaluate'] = request.form['evaluate']
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
		tmpdtm = session['dtm'] if 'dtm' in session else 'tf'
		dtmMethod = tmpdtm
		sentenceSelectionMethod = session['sentenceSelection'] if 'sentenceSelection' in session else 'SteinbergerJezek2'
		if dtmMethod == 'boolean':
			dtmMethod = 'tf'
			binary = True
		else :
			binary = False
		
		# summarization
		try :
			summary = Summarization()
			sentences = summary.getSentence(request.form['text'])
			if len(sentences) < 3:
				return jsonify({'result':'Sorry, at least 3 sentences ...'})
				
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

			result = {}
			
			if 'evaluate' in session and int(session['evaluate']) == 1 and 'id' in session and 'username' in session and 'superAdmin' in session:
				# evaluation main topic
				dtmSummary = summary.getDTM(summaryResult, mode=dtmMethod)
				uSummary, sigmaSummary, vtSummary = summary.getSVD(dtmSummary, summaryResult)
				uf = [i[0] for i in u]
				ue = [i[0] for i in uSummary]
				evaluationMainTopic = summary.getEvaluationMainTopic(sorted(absolute(uf)), sorted(absolute(ue)))

				# evaluation term significace
				uf = summary.getTermVector(u, sigma)
				ue = summary.getTermVector(uSummary, sigmaSummary)
				evaluationTermSignificance = summary.getEvaluationMainTopic(sorted(absolute(uf)), sorted(absolute(ue)))

				result['evaluationMainTopic'] = evaluationMainTopic
				result['evaluationTermSignificance'] = evaluationTermSignificance
				result['ratio'] = ratio 
				result['dtmMethod'] = tmpdtm
				result['sentenceSelectionMethod'] = sentenceSelectionMethod

				# insert data to evaluation table
				database = models.models.Session()
				evaluation = Evaluation(idAdmin=session['id'], dtmMethod=tmpdtm, sentenceSelectionMethod=sentenceSelectionMethod, 
					aspectRatio=ratio, mainTopic=evaluationMainTopic, termSignificance=evaluationTermSignificance)
				database.add(evaluation)
				database.commit()


			result['result'] = "\n".join(summaryResult)
			# print(result)
			return jsonify(result)
		except:
			return jsonify({'result':'Sorry something wrong ...'})
	return "request is not ajax"
	
if __name__ == "__main__":
	app.run(debug=True,threaded=True)
