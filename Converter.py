from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine

import docx2txt

from odf import odf2xhtml

class Converter(object):

	# convert pdf
	def pdfToText(self, file):
		result = ""
		parser = PDFParser(file)
		doc = PDFDocument()
		parser.set_document(doc)
		doc.set_parser(parser)
		doc.initialize('')
		rsrcmgr = PDFResourceManager()
		laparams = LAParams()
		device = PDFPageAggregator(rsrcmgr, laparams=laparams)
		interpreter = PDFPageInterpreter(rsrcmgr, device)
		for page in doc.get_pages():
		    interpreter.process_page(page)
		    layout = device.get_result()
		    for lt_obj in layout:
		        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
		            result += lt_obj.get_text()

		return result

	# convert docx
	def docxToText(self, file):
		return docx2txt.process(file)

	# convert odt to plain text
	def odtToText(self, file):
		data = odf2xhtml.load(file)
		return str(data.text)
