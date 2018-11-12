import numpy as np
from scipy.stats import norm

class Experiment():
    def __init__(self, dprime_human = 2, FWinvestment = 0, IDSinvestment = 0, InsuranceInvestment = 0, experiment_type = 4):
        self.experiment_type = experiment_type
        # parameter of the trial
        self.gamma = 0
        self.N = 100
        self.epsilon = 30
        self.percentage = float(self.epsilon)/float(self.N)

        self.FWinvestment = FWinvestment
        self.Pm = self.FW_function(self.FWinvestment)

        self.IDSinvestment = IDSinvestment
        self.dprime_alarm = self.IDS_function(self.IDSinvestment)

        self.InsuranceInvestment = InsuranceInvestment
        self.compensate = self.Insurance_function(self.InsuranceInvestment)

        self.Ps = (self.percentage * self.Pm) / ((1-self.percentage) + self.percentage * self.Pm)
        self.Pn = 1 - self.Ps

        # Erase
        self.Vcr = 1
        self.Vfa = 0
        self.Vhit = 0
        self.Vmiss = -2 * (1 - self.compensate)
        self.U = (float(self.Vfa - self.Vcr) / float(self.Vmiss - self.Vhit))

        # variables
        self.dprime_human = dprime_human

        try:
            # The Agent invest in IDS and not invest 100% in Firewall and not invest 100% in Insurance
            if self.Pm != 0 and self.dprime_alarm != 0 and self.compensate != 1:
                self.calculate_beta_alarm()
                self.find_zhit_zfa_alarm()
                self.calculate_beta_human()
                self.find_zhit_zfa_alarm_raised()
                self.find_zhit_zfa_alarm_notraised()
            # the agent didn't invest in IDS or invest 100% in the firewall\insurance
            else:
                # The Agent invest 100% in Firewall or 100% in insurance (Regardless of investment in IDS)
                # he will not experience any attack - the EV will be just hit investments
                if self.Pm == 0 or self.compensate == 1.0:
                    self.P_hit_alarm = 0
                    self.P_miss_alarm = 1 - self.P_hit_alarm
                    self.P_fa_alarm = 0
                    self.P_cr_alarm = 1 - self.P_fa_alarm

                # The Agent didn't invest in IDS at all- This is SDT with no alarm system - just agent SDT
                elif self.dprime_alarm == 0:
                    # calculate just with human (no alarm system)
                    self.beta = (float(self.Pn) / float(self.Ps)) * self.U
                    if self.beta < 0:
                        self.beta = self.beta * -1
                    lnbeta = np.log(self.beta)
                    self.lnbeta = lnbeta
                    self.Z_hit = (float(self.dprime_human ** 2) - 2.0 * float(lnbeta)) / (
                                2.0 * float(self.dprime_human))
                    self.Z_fa = self.Z_hit - self.dprime_human
                    self.P_hit_alarm = norm.cdf(self.Z_hit)
                    self.P_miss_alarm = 1 - self.P_hit_alarm
                    self.P_fa_alarm = norm.cdf(self.Z_fa)
                    self.P_cr_alarm = 1 - self.P_fa_alarm
                    self.EV = \
                        + self.Ps * (self.P_hit_alarm * self.Vhit + self.P_miss_alarm * self.Vmiss) \
                        + self.Pn * (self.P_cr_alarm * self.Vcr + self.P_fa_alarm * self.Vfa) \
                        - (self.InsuranceInvestment + self.FWinvestment + self.IDSinvestment)
        except:
            print 'Something Wrong'

    def FW_function(self, x):
        if self.experiment_type == 1:
            if x >= 4:
                return 0.3
            return 1
        elif self.experiment_type == 2 or self.experiment_type == 4:
            if x >= 9:
                return 0.9
            return 1
        elif self.experiment_type == 3:
            if x >= 4:
                return 0.8
            return 1

    def IDS_function(self, x):
        if self.experiment_type == 1:
            if x >= 9:
                return 2
            return 0

        elif self.experiment_type == 2:
            if x >= 4:
                return 4
            return 0

        elif self.experiment_type == 3:
            if x >= 4:
                return 2
            return 0

        elif self.experiment_type == 4:
            if x >= 9:
                return 1
            return 0

    def Insurance_function(self, x):
        if self.experiment_type == 1:
            if x >= 9:
                return 0.8
            return 0

        elif self.experiment_type == 2 or self.experiment_type == 3:
            if x >= 4:
                return 0.8
            return 0

        elif self.experiment_type == 4:
            if x >= 9:
                return 0.2
            return 0

    # calculate the optimal beta of the alarm system
    def calculate_beta_alarm(self):
        self.beta_alarm_system = (float(self.Pn) / float(self.Ps)) * self.U
        if self.beta_alarm_system < 0:
            self.beta_alarm_system = self.beta_alarm_system * -1

    # get the probabilities of the P_false_alarm and P_hit for the alarm system
    # and than find the PPV, NPV, P_alarm, P_no_alarm
    def find_zhit_zfa_alarm(self):
        lnbeta = np.log(self.beta_alarm_system)
        self.lnbeta = lnbeta
        self.Z_hit_alarm = (float(self.dprime_alarm ** 2) - 2.0 * float(lnbeta)) / (2.0 * float(self.dprime_alarm))
        self.Z_fa_alarm = self.Z_hit_alarm - self.dprime_alarm
        self.P_hit_alarm = norm.cdf(self.Z_hit_alarm)
        self.P_miss_alarm = 1 - self.P_hit_alarm
        self.P_fa_alarm = norm.cdf(self.Z_fa_alarm)
        self.P_cr_alarm = 1 - self.P_fa_alarm
        if self.P_hit_alarm == 0.0 and self.P_fa_alarm == 0.0:
            self.PPV = 0.0
        else:
            self.PPV = (self.P_hit_alarm * self.Ps)/(self.P_hit_alarm * self.Ps + self.P_fa_alarm * self.Pn)
        self.NPV = (self.P_cr_alarm * self.Pn)/(self.P_cr_alarm * self.Pn + self.P_miss_alarm * self.Ps)
        self.P_alarm = self.P_hit_alarm * self.Ps + self.P_fa_alarm * self.Pn
        self.P_noalarm = 1 - (self.P_hit_alarm * self.Ps + self.P_fa_alarm * self.Pn)

    # calculate the optimal beta for the human monitoring
    # in 2 situations - alarm raised and alarm not raised
    def calculate_beta_human(self):
        # alarm raised
        self.beta_alarm_raised = (float(1-self.PPV)/float(self.PPV)) * self.U
        if self.beta_alarm_raised < 0:
            self.beta_alarm_raised = self.beta_alarm_raised * -1
        # alarm not raised
        self.beta_alarm_notraised = (float(self.NPV)/float(1-self.NPV)) * self.U
        if self.beta_alarm_notraised < 0:
            self.beta_alarm_notraised = self.beta_alarm_notraised * -1

    # get the probabilities of the P_false_alarm and P_hit for the human monitoring when alarm was raised
    def find_zhit_zfa_alarm_raised(self):
        if self.beta_alarm_raised != 0.0:
            lnbeta = np.log(self.beta_alarm_raised)
        else:
            lnbeta = -1 * 10**6
        self.Z_hit_human_alarm_raised  = (float(self.dprime_human ** 2) - 2.0 * float(lnbeta)) / (2.0 * float(self.dprime_human))
        self.Z_fa_human_alarm_raised   = self.Z_hit_human_alarm_raised - self.dprime_human
        self.P_hit_human_alarm_raised  = norm.cdf(self.Z_hit_human_alarm_raised)
        self.P_miss_human_alarm_raised = 1 - self.P_hit_human_alarm_raised
        self.P_fa_human_alarm_raised   = norm.cdf(self.Z_fa_human_alarm_raised)
        self.P_cr_human_alarm_raised   = 1 - self.P_fa_human_alarm_raised


    # get the probabilities of the P_false_alarm and P_hit for the human monitoring when alarm was not raised
    def find_zhit_zfa_alarm_notraised(self):
        lnbeta = np.log(self.beta_alarm_notraised)
        self.Z_hit_human_alarm_notraised = (float(self.dprime_human ** 2) - 2.0 * float(lnbeta)) / (2.0 * float(self.dprime_human))
        self.Z_fa_human_alarm_notraised = self.Z_hit_human_alarm_notraised - self.dprime_human
        self.P_hit_human_alarm_notraised = norm.cdf(self.Z_hit_human_alarm_notraised)
        self.P_miss_human_alarm_notraised = 1 - self.P_hit_human_alarm_notraised
        self.P_fa_human_alarm_notraised = norm.cdf(self.Z_fa_human_alarm_notraised)
        self.P_cr_human_alarm_notraised = 1 - self.P_fa_human_alarm_notraised

