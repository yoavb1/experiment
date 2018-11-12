from Experiment_Human import Experiment
import mysql.connector as mdb
import random
import numpy as np

class Server():
    def __init__(self):
        self.ip = '127.0.0.1'
        self.N = 20 + 1
        self.sessions = 5

    def connect_to_DB(self):
        self.con = mdb.connect(host = self.ip, user='root', passwd='1234', db='experiment')
        self.cur = self.con.cursor()

    def close_connection(self):
        self.con.close()

    def write_to_DB(self, Answer, dictionary):
        self.connect_to_DB()
        if Answer == 'Investment':
            self.cur.execute(
                "UPDATE Actions SET Firewall_investment = ('%d'), IDSs_investment = ('%d'), Insurance_investment = ('%d')\
                 WHERE id = ('%d') and user_name = ('%s') and user_action_id = ('%d');"
                % (dictionary['Firewall_Investment'], dictionary['IDSs_Investment'], dictionary['Insurance_Investment'], \
                   dictionary['id'], dictionary['user_name'], dictionary['user_action_id']))
        elif Answer == 'Hit':
            self.cur.execute(
                "UPDATE Actions SET Hit = 1 WHERE id = ('%d') and user_name = ('%s') and user_action_id = ('%d');"
                % (dictionary['id'], dictionary['user_name'], dictionary['user_action_id']))
        elif Answer == 'Miss':
            self.cur.execute(
                "UPDATE Actions SET Miss = 1 WHERE id = ('%d') and user_name = ('%s') and user_action_id = ('%d');"
                % (dictionary['id'], dictionary['user_name'], dictionary['user_action_id']))
        elif Answer == 'FA':
            self.cur.execute(
                "UPDATE Actions SET FA = 1 WHERE id = ('%d') and user_name = ('%s') and user_action_id = ('%d');"
                % (dictionary['id'], dictionary['user_name'], dictionary['user_action_id']))
        elif Answer == 'CR':
            self.cur.execute(
                "UPDATE Actions SET CR = 1 WHERE id = ('%d') and user_name = ('%s') and user_action_id = ('%d');"
                % (dictionary['id'], dictionary['user_name'], dictionary['user_action_id']))
        if Answer != 'End':
            self.cur.execute(
                "UPDATE Actions SET\
                 Firewall_investment = %d, IDSs_investment = %d, Insurance_Investment = %d,\
                 Pm = %s, dprime = %s, compensate = %s,\
                 score = %d, malicious_or_not = ('%s')\
                 WHERE id = %d and user_name = ('%s') and user_action_id = %d;"
                % (dictionary['Firewall_Investment'], dictionary['IDSs_Investment'], dictionary['Insurance_Investment'], \
                   dictionary['Pm'], dictionary['dprime_alarm'], dictionary['compensate'], \
                   dictionary['score'], dictionary['malicious_or_not'],\
                   int(dictionary['id']), dictionary['user_name'], int(dictionary['user_action_id'])))
            self.cur.execute(
                "UPDATE Actions SET\
                 optimal_threshold = %s\
                 WHERE id = %d and user_name = ('%s') and user_action_id = %d;"
                % (dictionary['optimal threshold'],\
                   int(dictionary['id']), dictionary['user_name'], int(dictionary['user_action_id'])))

        else:
            self.connect_to_DB()
            # insert user to actions table

            self.cur.execute("UPDATE Users SET end_page = 'True' WHERE user_name = ('%s') and id = (%d);" \
                               % (dictionary['user_name'], dictionary['id']))
        self.con.commit()
        self.close_connection()

    def insert_to_dictionary(self, dictionary, Experiment):
        dictionary['Ps'] = Experiment.Ps
        dictionary['Vhit'] = Experiment.Vhit
        dictionary['Vmiss'] = Experiment.Vmiss
        dictionary['Vfa'] = Experiment.Vfa
        dictionary['Vcr'] = Experiment.Vcr
        dictionary['P_hit'] = Experiment.P_hit_alarm
        dictionary['P_fa'] = Experiment.P_fa_alarm
        dictionary['percentage'] = Experiment.percentage
        dictionary['Firewall_Investment'] = 0
        dictionary['Firewall_Level'] = 0
        dictionary['IDSs_Investment'] = 0
        dictionary['IDSs_Level'] = 0
        dictionary['Insurance_Investment'] = 0
        dictionary['Insurance_Level'] = 0
        dictionary['malicious_or_not'] = ''
        dictionary['Pm'] = 1
        dictionary['dprime_alarm'] = 0
        dictionary['dprime_human'] = 2
        dictionary['compensate'] = 0
        dictionary['score'] = 0
        dictionary['number'] = 0
        dictionary['suspicion'] = 0

        return dictionary

    def check_alarm(self, dictionary):
        # Alarm might be raised just if the user have IDSs (invest in the Alarm System)
        if dictionary['dprime_alarm'] > 0:
            alarm_or_not = np.random.uniform(0, 1)
            # the event is malicious
            if dictionary['malicious_or_not'] == 'Malicious':
                # Alarm will raised
                if alarm_or_not < dictionary['P_hit']:
                    dictionary['Alarm'] = 'True'
                # Alarm will not raised
                else:
                    dictionary['Alarm'] = 'False'
            # The event is non malicious
            else:
                # Alarm will raised
                if alarm_or_not < dictionary['P_fa']:
                    dictionary['Alarm'] = 'True'
                # Alarm will not raised
                else:
                    dictionary['Alarm'] = 'False'
        # The IDSs doesn't work
        else:
            dictionary['Alarm'] = 'False'

        # define colors to the rectangle
        if dictionary['Alarm'] == 'True':
            dictionary['color'] = 'red'
        else:
            dictionary['color'] = 'green'

        return dictionary

    def change_investments(self,Firewall_gap, IDSs_gap, Insurance_gap, dictionary):
        # create new experiment object
        exp = Experiment(dprime_human=2, FWinvestment = dictionary['Firewall_Investment'], \
                                     IDSinvestment = dictionary['IDSs_Investment'],\
                                     InsuranceInvestment =  dictionary['Insurance_Investment'],\
                                     experiment_type = dictionary['experiment_type'])
        # update the user environment after his invstment
        dictionary['Ps'] = exp.Ps
        dictionary['Vhit'] = exp.Vhit
        dictionary['Vmiss'] = exp.Vmiss
        dictionary['Vfa'] = exp.Vfa
        dictionary['Vcr'] = exp.Vcr
        dictionary['P_hit'] = exp.P_hit_alarm
        dictionary['P_fa'] = exp.P_fa_alarm
        dictionary['Pm'] = round(exp.Pm, 4)
        dictionary['dprime_alarm'] = round(exp.dprime_alarm, 4)
        dictionary['compensate'] = round(exp.compensate, 4)

        dictionary['Firewall_Level'] = int((1 - dictionary['Pm']) * 10.0)
        dictionary['IDSs_Level'] = int(dictionary['dprime_alarm'])
        dictionary['Insurance_Level'] = int(dictionary['compensate'] * 100.0)
        dictionary['score'] = dictionary['score'] - (Firewall_gap + IDSs_gap + Insurance_gap)

        dictionary['optimal threshold'] = float(float(dictionary['Ps']) / float(1 - dictionary['Ps'])) * \
                                          (float(dictionary['Vfa'] - dictionary['Vcr']) /
                                           float(dictionary['Vmiss'] - dictionary['Vhit']))
        dictionary['optimal threshold'] = round(dictionary['optimal threshold'], 4)
        return dictionary

    def check_investment(self, name, check, dictionary):
        # Return the Pm
        if name == 'Firewall':
            exp = Experiment(dprime_human=2, FWinvestment=check, \
                       IDSinvestment=dictionary['IDSs_Investment'], \
                       InsuranceInvestment=dictionary['Insurance_Investment'], \
                       experiment_type=dictionary['experiment_type'])
            return exp.FW_function(float(check))
        # Return the d' alarm
        elif name == 'IDSs':
            exp = Experiment(dprime_human=2, FWinvestment=dictionary['Firewall_Investment'], \
                       IDSinvestment=check, \
                       InsuranceInvestment=dictionary['Insurance_Investment'], \
                       experiment_type=dictionary['experiment_type'])
            return exp.IDS_function(float(check))
        # Return the compensate
        elif name == 'Insurance':
            exp = Experiment(dprime_human=2, FWinvestment=dictionary['Firewall_Investment'], \
                       IDSinvestment=dictionary['IDSs_Investment'], \
                       InsuranceInvestment=check, \
                       experiment_type=dictionary['experiment_type'])
            return exp.Insurance_function(float(check))

