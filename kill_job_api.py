#!/usr/bin/python

import os , sys , requests , subprocess 
from flask import render_template , Flask #render_template is for useing html file in displaying static page 
from flask import request


app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')	#need to create inside /template/ folder 

@app.route('/kill' , methods=['GET' , 'POST'])
def killjob():
	oid = request.args.get('oid')  #fatching the oid from url 
	oid = str(oid)			# converting it to string format may be optional 
	cmd = ('/home/ctmstest/bmcperl/perl force_end_job.pl ' +oid+ ' N < answer.txt')  #answer.txt content Y to run native command without interruption
	p=subprocess.Popen( cmd , stdout=subprocess.PIPE , stderr=subprocess.PIPE , stdin=subprocess.PIPE , shell=True)
	out,err = p.communicate()
	return out

if __name__ == "__main__":
	app.run(host="ctmtest.mylab.com",port=9050)


	
