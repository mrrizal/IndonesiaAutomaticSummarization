from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, after_this_request
from werkzeug import secure_filename
from models.Summarization import Summarization
from models.Converter import Converter
from numpy import absolute, sqrt
import models.models
from models.models import Admin, Evaluation
import sqlalchemy
import hashlib
import math
from sqlalchemy import func
import pdfkit
import os

app = Flask(__name__)
app.secret_key = 'rizalGanteng'


#=========================================FOR EVALUATION======================================
# index (isinya evaluation gan)
# index admin page
@app.route('/admin')
def admin():
	if 'id' in session and 'username' in session and 'superAdmin' in session:
		database = models.models.Session()
		totalPage = math.ceil(database.query(Evaluation.dtmMethod, Evaluation.sentenceSelectionMethod, Evaluation.aspectRatio,
		func.max(Evaluation.mainTopic).label('max_mainTopic'), func.min(Evaluation.mainTopic).label('min_mainTopic'), func.avg(Evaluation.mainTopic) \
		.label('avg_mainTopic'), func.max(Evaluation.termSignificance).label('max_termSignificance'), func.min(Evaluation.termSignificance) \
		.label('min_termSignificance'), func.avg(Evaluation.termSignificance).label('avg_termSignificance')) \
		.group_by(Evaluation.dtmMethod).group_by(Evaluation.sentenceSelectionMethod).group_by(Evaluation.aspectRatio).count()/10)
		
		return render_template('admin_page/index.html', totalPage=totalPage)
	return redirect(url_for('login'))

@app.route('/admin/evaluationResult', methods=['GET', 'POST'])
def getEvaluationResult():
	if 'id' in session and 'username' in session:
		#session['page'] = request.form['page'] if 'page' in request.form else 1
		#page = session['page']
		page = request.form['page'] if 'page' in request.form else 1
		dtmMethod = request.form['dtmMethod'] if request.form['dtmMethod'] != '0' else '%'
		sentenceSelectionMethod = request.form['sentenceSelectionMethod'] if request.form['sentenceSelectionMethod'] != '0' else '%'
		aspectRatio = int(request.form['aspectRatio']) if request.form['aspectRatio'] != '0' else 0
		
		database = models.models.Session()

		if(aspectRatio==0):
			totalPage = math.ceil(database.query(Evaluation.dtmMethod, Evaluation.sentenceSelectionMethod, Evaluation.aspectRatio,
			func.max(Evaluation.mainTopic).label('max_mainTopic'), func.min(Evaluation.mainTopic).label('min_mainTopic'), func.avg(Evaluation.mainTopic) \
			.label('avg_mainTopic'), func.max(Evaluation.termSignificance).label('max_termSignificance'), func.min(Evaluation.termSignificance) \
			.label('min_termSignificance'), func.avg(Evaluation.termSignificance).label('avg_termSignificance')) \
			.group_by(Evaluation.dtmMethod).group_by(Evaluation.sentenceSelectionMethod).group_by(Evaluation.aspectRatio).filter(Evaluation.dtmMethod.like(dtmMethod)).filter(Evaluation.sentenceSelectionMethod.like(sentenceSelectionMethod)).count()/10)

			if 'getTotalPage' in request.form and request.form['getTotalPage'] != '0':
				return jsonify({'totalPage':totalPage})

			datas = database.query(Evaluation.dtmMethod, Evaluation.sentenceSelectionMethod, Evaluation.aspectRatio,
			func.max(Evaluation.mainTopic).label('max_mainTopic'), func.min(Evaluation.mainTopic).label('min_mainTopic'), func.avg(Evaluation.mainTopic) \
			.label('avg_mainTopic'), func.max(Evaluation.termSignificance).label('max_termSignificance'), func.min(Evaluation.termSignificance) \
			.label('min_termSignificance'), func.avg(Evaluation.termSignificance).label('avg_termSignificance')) \
			.group_by(Evaluation.dtmMethod).group_by(Evaluation.sentenceSelectionMethod).group_by(Evaluation.aspectRatio)\
			.filter(Evaluation.dtmMethod.like(dtmMethod)).filter(Evaluation.sentenceSelectionMethod.like(sentenceSelectionMethod))\
			.order_by(func.avg(Evaluation.termSignificance).desc(), func.avg(Evaluation.mainTopic).desc()).limit(10).offset((int(page)-1)*10).all()
		
		else:
			totalPage = math.ceil(database.query(Evaluation.dtmMethod, Evaluation.sentenceSelectionMethod, Evaluation.aspectRatio,
			func.max(Evaluation.mainTopic).label('max_mainTopic'), func.min(Evaluation.mainTopic).label('min_mainTopic'), func.avg(Evaluation.mainTopic) \
			.label('avg_mainTopic'), func.max(Evaluation.termSignificance).label('max_termSignificance'), func.min(Evaluation.termSignificance) \
			.label('min_termSignificance'), func.avg(Evaluation.termSignificance).label('avg_termSignificance')) \
			.group_by(Evaluation.dtmMethod).group_by(Evaluation.sentenceSelectionMethod).group_by(Evaluation.aspectRatio).filter(Evaluation.dtmMethod.like(dtmMethod)).filter(Evaluation.sentenceSelectionMethod.like(sentenceSelectionMethod)). \
			filter(Evaluation.aspectRatio==aspectRatio).count()/10)

			if 'getTotalPage' in request.form and request.form['getTotalPage'] != '0':
				return jsonify({'totalPage':totalPage})

			datas = database.query(Evaluation.dtmMethod, Evaluation.sentenceSelectionMethod, Evaluation.aspectRatio,
			func.max(Evaluation.mainTopic).label('max_mainTopic'), func.min(Evaluation.mainTopic).label('min_mainTopic'), func.avg(Evaluation.mainTopic) \
			.label('avg_mainTopic'), func.max(Evaluation.termSignificance).label('max_termSignificance'), func.min(Evaluation.termSignificance) \
			.label('min_termSignificance'), func.avg(Evaluation.termSignificance).label('avg_termSignificance')) \
			.group_by(Evaluation.dtmMethod).group_by(Evaluation.sentenceSelectionMethod).group_by(Evaluation.aspectRatio)\
			.filter(Evaluation.dtmMethod.like(dtmMethod)).filter(Evaluation.sentenceSelectionMethod.like(sentenceSelectionMethod)). \
			filter(Evaluation.aspectRatio==aspectRatio).order_by(func.avg(Evaluation.termSignificance).desc(), 
				func.avg(Evaluation.mainTopic).desc())\
			.limit(10).offset((int(page)-1)*10).all()
			
		evaluation = [{'totalPage' : totalPage }]
		for data in datas:
			tmp = {}
			tmp['dtmMethod'] = data.dtmMethod
			tmp['sentenceSelectionMethod'] = data.sentenceSelectionMethod
			tmp['aspectRatio'] = data.aspectRatio
			tmp['min_mainTopic'] = data.min_mainTopic
			tmp['max_mainTopic'] = data.max_mainTopic
			tmp['avg_mainTopic'] = data.avg_mainTopic
			tmp['min_termSignificance'] = data.min_termSignificance
			tmp['max_termSignificance'] = data.max_termSignificance
			tmp['avg_termSignificance'] = data.avg_termSignificance
			evaluation.append(tmp)

		return jsonify(evaluation)

	return 'hello world'


# evaluation page
@app.route('/admin/evaluation_data')
def evaluation_data():
	if 'id' in session and 'username' in session and 'superAdmin' in session:
		database = models.models.Session()
		totalPage = math.ceil(database.query(Evaluation).count()/10)
		return render_template('admin_page/evaluation_data.html', totalPage=totalPage)
	return redirect(url_for('login'))

# for get evaluation data
@app.route('/admin/evaluationdata', methods=['GET', 'POST'])
def getDataEvaluation():
	if 'id' in session and 'username' in session:
		#session['page'] = request.form['page'] if 'page' in request.form else 1
		#page = session['page']
		page = request.form['page'] if 'page' in request.form else 1
		dtmMethod = request.form['dtmMethod'] if request.form['dtmMethod'] != '0' else '%'
		sentenceSelectionMethod = request.form['sentenceSelectionMethod'] if request.form['sentenceSelectionMethod'] != '0' else '%'
		aspectRatio = int(request.form['aspectRatio']) if request.form['aspectRatio'] != '0' else 0
		
		database = models.models.Session()

		if(aspectRatio==0):
			totalPage = math.ceil(database.query(Evaluation).filter(Evaluation.dtmMethod.like(dtmMethod)).filter(Evaluation.sentenceSelectionMethod.like(sentenceSelectionMethod)).count()/10)

			if 'getTotalPage' in request.form and request.form['getTotalPage'] != '0':
				return jsonify({'totalPage':totalPage})

			datas = database.query(Evaluation).filter(Evaluation.dtmMethod.like(dtmMethod)).filter(Evaluation.sentenceSelectionMethod.like(sentenceSelectionMethod)).limit(10).offset((int(page)-1)*10).all()
		else:
			totalPage = math.ceil(database.query(Evaluation).filter(Evaluation.dtmMethod.like(dtmMethod)).filter(Evaluation.sentenceSelectionMethod.like(sentenceSelectionMethod)). \
			filter(Evaluation.aspectRatio==aspectRatio).count()/10)

			if 'getTotalPage' in request.form and request.form['getTotalPage'] != '0':
				return jsonify({'totalPage':totalPage})

			datas = database.query(Evaluation).filter(Evaluation.dtmMethod.like(dtmMethod)).filter(Evaluation.sentenceSelectionMethod.like(sentenceSelectionMethod)). \
			filter(Evaluation.aspectRatio==aspectRatio).limit(10).offset((int(page)-1)*10).all()
			
		evaluation = [{'totalPage' : totalPage }]
		for data in datas:
			tmp = {}
			tmp['id'] = data.id
			tmp['admin'] = database.query(Admin.username).filter(Admin.id==data.idAdmin).first()[0]
			tmp['dtmMethod'] = data.dtmMethod
			tmp['sentenceSelectionMethod'] = data.sentenceSelectionMethod
			tmp['aspectRatio'] = data.aspectRatio
			tmp['mainTopic'] = data.mainTopic
			tmp['termSignificance'] = data.termSignificance
			evaluation.append(tmp)

		return jsonify(evaluation)

	return 'hello world'

@app.route('/admin/evaluation_delete', methods=['GET', 'POST'])
def evaluation_delete():
	if 'id' in session and 'username' in session:
		if session['superAdmin'] != True:
			return redirect(url_for('admin'))
		
		if request.is_xhr:
			if request.form is not None and request.form['id'].strip() != "":
				id = request.form['id']
				database = models.models.Session()
				try:
					database.query(Evaluation).filter(Evaluation.id==id).delete(synchronize_session=False)
					database.commit()
					return str(math.ceil(database.query(Evaluation).count()/10))
				except e:
					pass
		return "failed"
	return redirect(url_for('login'))


#===============================================ADMIN================================================
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

# change password
@app.route('/admin/change_password', methods = ['GET', 'POST'])
def change_password():
	if 'id' in session and 'username' in session and 'superAdmin' in session:
		if request.is_xhr and request.form is not None:
			database = models.models.Session()
			if database.query(Admin).filter(Admin.username==session['username']).count() and request.form['newPassword'].strip() != "":
				try:
					m = hashlib.md5()
					m.update(request.form['newPassword'].encode('utf-8'))
					database.query(Admin).filter(Admin.username==session['username']).update({'password' : m.hexdigest()})
					database.commit()
					return jsonify({'message':'success'})
				except:
					return jsonify({'message':'failed'})
		return render_template('admin_page/change_password.html')
	return redirect(url_for('admin'))

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
@app.route('/admin/admindata', methods=['GET', 'POST'])
def getAdminData():
	if 'id' in session and 'username' in session and 'superAdmin' in session:
		if session['superAdmin'] != True:
			return redirect(url_for('admin'))
		
		#session['page'] = request.form['page'] if 'page' in request.form else 1
		database = models.models.Session()
		page = request.form['page'] if 'page' in request.form else 1
		
		if 'username' in request.form and request.form['username'].strip() != "":
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
		if request.is_xhr:
			return str(totalPage)

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
					return str(math.ceil(database.query(Admin).count()/10))
				except e:
					pass
		return "failed"
	return redirect(url_for('login'))

#==============================================SUMMARIZATION/FRONT-END=====================================

@app.route('/')
def index():
	return render_template('index.html')

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
				return "upload failed"
		else:
			return "upload failed"
	return redirect(url_for('index'))

@app.route('/save_evaluation', methods = ['GET', 'POST'])
def saveEvaluation():
	if 'id' in session and 'username' in session and 'superAdmin' in session and request.is_xhr:
		idAdmin = session['id']
		dtmMethod = request.form['dtmMethod']
		sentenceSelectionMethod = request.form['sentenceSelectionMethod']
		aspectRatio = request.form['aspectRatio']
		mainTopic = request.form['evaluationMainTopic']
		termSignificance = request.form['evaluationTermSignificance']
		# insert data to evaluation table
		database = models.models.Session()
		evaluation = Evaluation(idAdmin=idAdmin, dtmMethod=dtmMethod, sentenceSelectionMethod=sentenceSelectionMethod, 
			aspectRatio=aspectRatio, mainTopic=mainTopic, termSignificance=termSignificance)
		database.add(evaluation)
		database.commit()
		return "success"

	return redirect(url_for('index'))

@app.route('/saveResult', methods = ['GET', 'POST'])
def saveResult():
	if request.is_xhr:
		# print(request.form['result'])
		pdfkit.from_string(request.form['result'], request.form['fileName'])
		# pdf = open("out.pdf")
		# response = make_response(unicode(pdf.read(), errors='ignore'))
		# response.headers['Content-Disposition'] = "attachment; filename='out.pdf"
		# response.mimetype = 'application/pdf'
		# pdf.close()
		# response = send_file("out.pdf", as_attachment=True)
		return "success"
	return redirect(url_for('index'))

file = ""
@app.route('/getPDF/<fileName>', methods = ['GET', 'POST'])
def getPDF(fileName):
	@after_this_request
	def deletePDF(response):
		try:
			os.remove(file)
		except:
			pass
		return response
	try:
		response = send_file(fileName, as_attachment=True)
		file = fileName
		return response
	except:
		return redirect(url_for('index')) 

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
				# evaluationMainTopic = summary.getEvaluationMainTopic(sorted(absolute(uf)), sorted(absolute(ue)))
				evaluationMainTopic = summary.getEvaluationMainTopic(sorted(uf), sorted(ue))

				# evaluation term significace
				uf = summary.getTermVector(u, sigma)
				ue = summary.getTermVector(uSummary, sigmaSummary)
				# evaluationTermSignificance = summary.getEvaluationMainTopic(sorted(absolute(uf)), sorted(absolute(ue)))
				evaluationTermSignificance = summary.getEvaluationMainTopic(uf, ue)

				result['evaluationMainTopic'] = evaluationMainTopic
				result['evaluationTermSignificance'] = evaluationTermSignificance
				result['ratio'] = ratio 
				result['dtmMethod'] = tmpdtm
				result['sentenceSelectionMethod'] = sentenceSelectionMethod

			result['success'] = True
			result['result'] = "\n".join(summaryResult)
			# print(result)
			return jsonify(result)
		except:
			return jsonify({'result':'Evaluation Failed, Please change the aspect ratio ...'})
	return "request is not ajax"
	
if __name__ == "__main__":
	app.run(debug=True,threaded=True)
