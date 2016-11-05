from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///summarization.sqlite3', echo=True)
Session = sessionmaker(bind=engine)

class Admin(Base):
	__tablename__ = 'admin'

	id = Column(Integer, primary_key=True)
	username = Column(String(30), unique=True)
	password = Column(String(32))
	superAdmin = Column(Boolean(), default=0)

	def __repr__(self):
		return "<User(username='%s', password='%s', superAdmin='%s')>" % (self.username, self.password, self.superAdmin)

class Evaluation(Base):
	__tablename__ = 'evaluation'

	id = Column(Integer, primary_key=True)
	idAdmin = Column(Integer, ForeignKey(Admin.id), nullable=False)
	dtmMethod = Column(String(30))
	sentenceSelectionMethod = Column(String(30))
	aspectRatio = Column(Float())
	mainTopic = Column(Float())
	termSignificance = Column(Float())
	
	def __repr__(self):
		return "<Evaluation(idAdmin='%s', dtmMethod='%s'. sentenceSelectionMethod='%s', aspectRation='%s', mainTopic='%s', termSignificance='%s')> " % \
		(self.idAdmin, self.dtmMethod, self.sentenceSelectionMethod, self.aspectRatio, self.mainTopic, self.termSignificance)

# for create database
def main():
	Base.metadata.create_all(engine)

'''
if __name__ == "__main__":
	main()
'''
