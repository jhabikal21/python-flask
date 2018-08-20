#!/bin/usr/python3.5
from flask import Flask, request, render_template, Markup

app = Flask(__name__)
app.debug = True

import socket
import os
import sys
import socket
import subprocess
import json

@app.route("/")
def mainpg():
    return render_template('index.html')

@app.route('/hello')
def hello():
    return 'Hello, World'


def abort_if_invalid_ip_shared(ipadd):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
           return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False
    return True

def abort_if_no_checkbox_selected(value):
    if value[0] == 0:
       os.abort(message="No checkBox Selected")
#       sys.exit("No checkBox Selected")

#def result(todo_id, ipadd):
#    if todo_id == 'ping':
#       c_result = subprocess.run(['ping', ipadd, '-c 2'], stdout=subprocess.PIPE)
#    elif todo_id == 'mtr':
#       c_result = subprocess.run(['mtr -n --report', str(ipadd), '-o "LSRD NBWA JXIM V"'], stdout=subprocess.PIPE)
#    elif todo_id == 'traceroute':
#       c_result = subprocess.run(['traceroute -n ', str(ipadd)], stdout=subprocess.PIPE)
#    else:
#        c_result = subprocess.run(['telnet -d ', str(ipadd)], stdout=subprocess.PIPE)
#    return c_result

@app.route('/result.html',methods=['GET', 'POST'])
def button_clicked():
    ipadd = request.form['ipadd']
    value = request.form.getlist("test")
    abort_if_no_checkbox_selected(value)
#    c_result = subprocess.run(['ping', ipadd, '-c 2'], stdout=subprocess.PIPE)
    c_result_ping = c_result_mtr = c_result_tra = c_result_tel = None
    for i in range(len(value)):
#        todo_id = value[i]
#        c_result_ping = c_result_mtr = c_result_tra = c_result_tel = None
        if value[i] == 'ping':
            c_result = subprocess.run(['ping', ipadd, '-c 2'], stdout=subprocess.PIPE)
            c_result_ping = c_result.stdout.decode('utf-8')
        elif value[i] == 'mtr':
#            cmd = "mtr -c 1 -r " + str(ipadd)
#            c_result = subprocess.run(['mtr', str(ipadd), '-o "LSRD NBWA JXIM V"'], stdout=subprocess.PIPE)
#            output = subprocess.Popen(cmd, shell=True,  stdout=subprocess.PIPE)
#            c_result = output.communicate()
            c_result = subprocess.run(['mtr','-c', '1', '-r', str(ipadd)], stdout=subprocess.PIPE)
            c_result_mtr = c_result.stdout.decode('utf-8')
#           c_result = subprocess.run([ cmd ], stdout=subprocess.PIPE)
        elif value[i] == 'traceroute':
            c_result = subprocess.run(['traceroute', str(ipadd)], stdout=subprocess.PIPE)
            c_result_tra = c_result.stdout.decode('utf-8')
#            c_result1 = [x.decode('utf8') for x in c_result.stdout.readlines()]
        else:
            c_result = subprocess.run(['telnet', str(ipadd)], stdout=subprocess.PIPE)
            c_result_tel = c_result.stdout.decode('utf-8')
    return render_template('result.html', value_ping=c_result_ping, value_mtr=c_result_mtr, value_tel=c_result_tel, value_tra=c_result_tra, ipadd=ipadd)

if __name__ == "__main__":
    app.run()
