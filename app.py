from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, SelectField, TextAreaField, validators
#from data import Forms
from flask_mysqldb import MySQL
field_label=""
app = Flask(__name__)
#Config Mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'opqJy241'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#init Mysql
mysql = MySQL(app)
#Forms = Forms()
@app.route('/')
def index():
	return render_template('home.html')

@app.route('/list')
def forms():

	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM forms")

	Forms = cur.fetchall()
	
	if result>0:
		return render_template('list.html', forms = Forms)
	else:
		msg = 'No Forms Created Yet'
		return render_template('list.html', msg=msg)

	cur.close()

@app.route('/submission/<string:name>/')
def submission(name):

	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM answers WHERE form_name = %s", [name])

	Submissions = cur.fetchall()
	
	if result>0:
		return render_template('submission.html', forms = Submissions, name=name)
	else:
		msg = 'No Forms Created Yet'
		return render_template('submission.html', msg=msg)

	cur.close()

class fill_form(Form):
	ans = StringField("Answer", [validators.length(min=1, max=255)])
@app.route('/list/<string:name>/', methods=['GET', 'POST'])
def form(name):
	cur = mysql.connection.cursor()

	result = cur.execute("SELECT * FROM field WHERE form_name = %s", [name])
	
	fields = cur.fetchall()
	form = fill_form(request.form)
	for field in fields:
	#	ans = StringField(field['field_label'], [validators.length(min=1, max=255)])
		
		if request.method == 'POST' and form.validate():
			ans = form.ans.data
			#Create Cursor
			cur = mysql.connection.cursor()
			cur.execute("INSERT INTO answers(form_name, field_label, answer) VALUES(%s, %s, %s)", ([name], field['field_label'], ans))
			cur.execute("UPDATE forms SET submissions = submissions + 1 WHERE form_name = %s", [name])
			#commit to DB
			mysql.connection.commit()

			cur.close()
			ans = StringField("Answer", [validators.length(min=1, max=255)])
		#	return redirect(url_for('form', name=name))
#		print "%s" % (field['form_name'])
#	print {form}
#	result = cur.execute("SELECT * FROM field WHERE form_name = %s", [form])

#	fields = cur.fetchall()
	return render_template("form.html", form=form, fields = fields, name=name)


class build_form(Form):
	field_label = StringField('field_label', [validators.length(min=1, max=255)])
	input_name = StringField('input_name', [validators.length(min=1, max=255)])
	input_type = SelectField('input_type',choices=[('text', 'text'),('color', 'color'),('date', 'date'),('email', 'email'),('tel', 'tel'),('number', 'number')])

@app.route('/builder', methods=['GET', 'POST'])
def build():
	form = build_form(request.form)
	if request.method == 'POST' and form.validate():
		field_label = form.field_label.data
		input_name = form.input_name.data
		input_type = form.input_type.data
		empty = ""
		
		#Create Cursor
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO field(field_label, input_name, input_type, form_name) VALUES(%s, %s, %s, %s)", (field_label, input_name, input_type, empty))

		#commit to DB
		mysql.connection.commit()

		cur.close()

		flash('Field was added to form', 'success')
	return render_template('builder.html', form=form)

class finish_form(Form):
	name = StringField('Form Name', [validators.length(min=1, max=20)])

@app.route('/finish', methods=['GET', 'POST'])
def finish():
	form = finish_form(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		zero = 0
		empty = ""
		cur = mysql.connection.cursor()
#		SET FOREIGN_KEY_CHECKS = 0
		cur.execute("INSERT INTO forms(form_name, submissions) VALUES(%s, %s)",(name, zero))
		cur.execute("UPDATE field SET form_name = %s WHERE form_name = %s",(name, empty))
#		SET FOREIGN_KEY_CHECKS=1			
		mysql.connection.commit()
		cur.close()

		flash('Form Created', 'success')
		return redirect(url_for('finish'))
	return render_template('finish.html', form=form)

@app.route('/submit')
def submit():
	return render_template('submit.html')



if __name__ == '__main__':
	app.secret_key='secret123'
	app.run(debug=True)
