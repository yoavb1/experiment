from flask import Flask, render_template, request, redirect
from Experiment_Human import Experiment
from Server import Server
from DB_content import *

import random
import numpy as np
import ast

app = Flask(__name__)

######

# Login Page - the user need to enter his user name
@app.route('/', methods=['GET', 'POST'])
def login():
    dictionary = {}
    dictionary['experiment_type'] = random.randint(1, 4)
    trial = Experiment(dictionary['experiment_type'])
    dictionary = server.insert_to_dictionary(dictionary, trial)
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        # Get user data from db in order to plot it on the page
        user_name = request.form['user_name']
        dictionary['user_name'] = user_name
        app.logger.warning('In login')

        if len(user_name) >= 2:
            server.connect_to_DB()
            server.cur.execute("INSERT INTO Users (user_name, experiment_type) VALUES ('%s', %d);"
                        % (dictionary['user_name'], dictionary['experiment_type']))  # Inserts user input to database
            server.cur.execute("select id from Users Where user_name = ('%s') order by id desc limit 1;;"
                        % (dictionary['user_name']))  # Inserts user input to database
            dictionary['id'] = server.cur.fetchall()[0][0]
            dictionary['user_action_id'] = dictionary['id'] * 1000
            server.con.commit()
            server.close_connection()
            return redirect("/instruction_1/%s" % (dictionary))
        else:
            return redirect("/error/")

# First Instruction page - we will show the user some instruction
@app.route('/instruction_1/<dictionary>', methods=['GET','POST'])
def instrucation_1(dictionary):
    dictionary = ast.literal_eval(dictionary)
    if request.method == 'GET':
        app.logger.warning('In Instruction page 1')
        return render_template('instruction_1.html', user = dictionary['user_name'])
    elif request.method == 'POST':
        server.connect_to_DB()
        # update that the user read the instructions
        server.cur.execute("UPDATE Users SET instruction_1 = 'True' WHERE user_name = ('%s') and id = (%d);"\
                           % (dictionary['user_name'], dictionary['id']))
        server.con.commit()
        server.close_connection()
        return redirect("/instruction_2/%s" % (dictionary))

# Second Instruction page - we will show the user the payoff matrix
@app.route('/instruction_2/<dictionary>', methods=['GET','POST'])
def instrucation_2(dictionary):
    dictionary = ast.literal_eval(dictionary)
    if request.method == 'GET':
        app.logger.warning('In Instruction page 2')
        return render_template('instruction_2.html', user = dictionary['user_name'], Vhit = dictionary['Vhit'], \
                               Vmiss = dictionary['Vmiss'], Vfa = dictionary['Vfa'], \
                               Vcr = dictionary['Vcr'])
    else:
        server.connect_to_DB()
        # update that the user read the instructions
        server.cur.execute("UPDATE Users SET instruction_2 = 'True' WHERE user_name = ('%s') and id = (%d);"\
                           % (dictionary['user_name'], dictionary['id']))
        server.con.commit()
        server.close_connection()
        return redirect("/questions/%s" % (dictionary))

# question page - we will ask the user some question about the instruction
@app.route('/questions/<dictionary>', methods=['GET','POST'])
def questions(dictionary):
    dictionary = ast.literal_eval(dictionary)
    if request.method == 'GET':
        app.logger.warning('In questions page')
        return render_template('questions.html', user = dictionary['user_name'])
    else:
        server.connect_to_DB()
        # update that the user read the instructions
        server.cur.execute("UPDATE Users SET question = 'True' WHERE user_name = ('%s') and id = (%d);"\
                           % (dictionary['user_name'], dictionary['id']))
        server.con.commit()
        server.close_connection()
        return redirect("/Game/%s" % (dictionary))

# Game page - the gameloop occurs here
@app.route('/Game/<dictionary>', methods=['GET','POST'])
def Game(dictionary):
    dictionary = ast.literal_eval(dictionary)
    if request.method == 'GET':
        server.connect_to_DB()
        # insert user to Actions table
        server.cur.execute("INSERT INTO Actions (id, user_name, user_action_id, experiment_type) VALUES (%d,'%s',%d, %d);"
                           % (dictionary['id'], dictionary['user_name'], dictionary['user_action_id'], dictionary['experiment_type']))  # Inserts user input to database
        server.con.commit()
        server.close_connection()
        app.logger.warning('In game page - GET')

        # The game end
        if dictionary['number'] == server.N * server.sessions:
            return redirect("/End/%s" % (dictionary))

        # Investment Time
        if dictionary['number'] % server.N == 0:
            return render_template('Game.html', score = dictionary['score'],  Firewall_Investment = dictionary['Firewall_Investment'], \
                                   IDSs_Investment=dictionary['IDSs_Investment'],\
                                   Insurance_Investment = dictionary['Insurance_Investment'],\
                                   Firewall_Level = dictionary['Firewall_Level'], IDSs_Level = dictionary['IDSs_Level'],\
                                   Insurance_Level = dictionary['Insurance_Level'], enable = 'True',\
                                   malicious = dictionary['malicious_or_not'],\
                                   suspicious = 0, Alarm = "False", message = '', Set = [0, 0, 0])
        # Play Time
        else:
            # check if the event is malicious or not
            def check_malicious(dictionary):
                malicious_or_not = np.random.uniform(0, 1)
                # malicious event
                if malicious_or_not < dictionary['percentage']:
                    dictionary['malicious_or_not'] = 'Malicious'
                    while dictionary['suspicion'] <= 1 or dictionary['suspicion'] >= 13:
                        dictionary['suspicion'] = round(np.random.normal(7 + dictionary['dprime_human'], 2), 2)
                    # did not pass the firewall
                    if malicious_or_not <= dictionary['Ps']:
                        pass
                    # pass the firewall
                    else:
                        dictionary['number'] = dictionary['number'] + 1
                        dictionary['user_action_id'] = dictionary['user_action_id'] + 1
                        dictionary = check_malicious(dictionary)
                # non malicious event
                else:
                    'this is not malicious event'
                    dictionary['malicious_or_not'] = 'Non Malicious'
                    while dictionary['suspicion'] <= 1 or dictionary['suspicion'] >= 13:
                        dictionary['suspicion'] = round(np.random.normal(7, 2), 2)

                # check if to raise alarm or not
                dictionary = server.check_alarm(dictionary)
                return dictionary

            dictionary = check_malicious(dictionary)
        # render the gape HTML without investment option - user classification time
        return render_template('Game.html', score=dictionary['score'],
                               Firewall_Investment=dictionary['Firewall_Investment'], \
                               IDSs_Investment=dictionary['IDSs_Investment'], \
                               Insurance_Investment=dictionary['Insurance_Investment'], \
                               Firewall_Level=dictionary['Firewall_Level'], IDSs_Level=dictionary['IDSs_Level'], \
                               Insurance_Level=dictionary['Insurance_Level'],\
                               enable='False', malicious=dictionary['malicious_or_not'],\
                               message = dictionary['malicious_or_not'],\
                               suspicious = dictionary['suspicion'], Alarm = dictionary['Alarm'],\
                               width = dictionary['suspicion'] * 15, height = dictionary['suspicion'] * 30,\
                               color = dictionary['color'],\
                               dictionary = dictionary)

    # The user Invest or check investment options
    elif request.method == 'POST':
        try:
            # The user invest
            if request.form['submit_button'] == 'submit':
                # save the pre investment amount
                dictionary['Firewall_Investment_Before'] = dictionary['Firewall_Investment']
                dictionary['IDSs_Investment_Before'] = dictionary['IDSs_Investment']
                dictionary['Insurance_Investment_Before'] = dictionary['Insurance_Investment']

                # save the investment amount
                dictionary['Firewall_Investment'] = int(request.form.get('Firewall'))
                dictionary['IDSs_Investment'] = int(request.form.get('IDSs'))
                dictionary['Insurance_Investment'] = int(request.form.get('Insurance'))

                # calculate the gap between investments
                Firewall_gap = dictionary['Firewall_Investment'] - dictionary['Firewall_Investment_Before']
                IDSs_gap = dictionary['IDSs_Investment'] - dictionary['IDSs_Investment_Before']
                Insurance_gap = dictionary['Insurance_Investment'] - dictionary['Insurance_Investment_Before']

                dictionary = server.change_investments(Firewall_gap, IDSs_gap, Insurance_gap, dictionary)

                # write the new investment to the DB
                server.write_to_DB('Investment', dictionary)
                dictionary['number'] = dictionary['number'] + 1

                dictionary['user_action_id'] = dictionary['user_action_id'] + 1

                return redirect("/Game/%s" % (dictionary))

            # The user just check investments
            elif request.form['submit_button'] == 'set_firewall' or request.form['submit_button'] == 'set_IDSs' or request.form['submit_button'] == 'set_insurance':
                investment = [dictionary['Firewall_Investment'], dictionary['IDSs_Investment'], dictionary['Insurance_Investment']]
                quality = [dictionary['Pm'], dictionary['dprime_alarm'], dictionary['compensate']]
                # User want to check the firewall
                if request.form['submit_button'] == 'set_firewall':
                    Firewall_Investment = int(request.form.get('Firewall'))
                    investment[0] = int(Firewall_Investment)
                    quality[0] = server.check_investment('Firewall', investment[0], dictionary)

                elif request.form['submit_button'] == 'set_IDSs':
                    IDSs_Investment = int(request.form.get('IDSs'))
                    investment[1] = int(IDSs_Investment)
                    quality[1] = server.check_investment('IDSs', investment[1], dictionary)

                elif request.form['submit_button'] == 'set_insurance':
                    Insurance_Investment = int(request.form.get('Insurance'))
                    investment[2] = int(Insurance_Investment)
                    quality[2] = server.check_investment('Insurance', investment[2], dictionary)

                return render_template('Game.html', score=dictionary['score'],
                                       Firewall_Investment=investment[0], \
                                       IDSs_Investment=investment[1], \
                                       Insurance_Investment=investment[2], \
                                       Firewall_Level=dictionary['Firewall_Level'], IDSs_Level=dictionary['IDSs_Level'], \
                                       Insurance_Level=dictionary['Insurance_Level'], \
                                       enable='True', malicious=dictionary['malicious_or_not'], \
                                       suspicious=0, Alarm='False', message='', \
                                       Set=[1, 1, 1], \
                                       Pm = quality[0], IDSs = quality[1], \
                                       Insurance = int(quality[2]*100), dictionary = dictionary)

        # The user classify the events
        except:
            try:
                if request.form['Hit'] == 'Malicious':
                        dictionary['malicious_or_not'] = 'Malicious'
                        dictionary['score'] = dictionary['score'] + dictionary['Vhit']
                        server.write_to_DB('Hit', dictionary)
            except:
                pass

            try:
                if request.form['FA'] == 'Malicious':
                    dictionary['malicious_or_not'] = 'Non Malicious'
                    dictionary['score'] = dictionary['score'] + dictionary['Vfa']
                    server.write_to_DB('FA', dictionary)
            except:
                pass

            try:
                if request.form['Miss'] == 'Non Malicious':
                    dictionary['malicious_or_not'] = 'Malicious'
                    dictionary['score'] = dictionary['score'] + dictionary['Vmiss']
                    server.write_to_DB('Miss', dictionary)
            except:
                pass

            try:
                if request.form['CR'] == 'Non Malicious':
                    dictionary['malicious_or_not'] = 'Non Malicious'
                    dictionary['score'] = dictionary['score'] + dictionary['Vcr']
                    server.write_to_DB('CR', dictionary)
            except:
                pass

            dictionary['number'] = dictionary['number'] + 1
            dictionary['user_action_id'] = dictionary['user_action_id'] + 1
            return redirect("/Game/%s" % (dictionary))

@app.route('/error/', methods=['GET', 'POST'])
def error():
    if request.method == 'GET':
        return render_template('error.html')
    else:
        return redirect("/")

@app.route('/End/<dictionary>', methods=['GET','POST'])
def End(dictionary):
    dictionary = ast.literal_eval(dictionary)
    server.write_to_DB('End', dictionary)
    if request.method == 'GET':
        return render_template('End.html', score = dictionary['score'], name = dictionary['user_name'])

if __name__ == '__main__':
    server = Server()
	create_db = DB()
    app.run(debug=True)
