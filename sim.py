import random
import datetime
import os
import numpy as np
import pickle
import time
from copy import deepcopy

GCD = 1.5
SB_CAST_TIME=2.5
SB_BASE=481
SB_COEF=.857
CORR_MANA=290
CORR_BASE=666
CORR_COEF = 1.0
CORR_CAST_TIME=1.5
LT_BASE=424
LT_COEF=.8
LT_MOD=1.2
LT_CAST_TIME=1.5

spec_properties = {} 
spec_properties['sm_ruin_w_corruption']={"shadow mod": 1.21, "imp": True, "succubus": False, "ruin":True, "isb_flag":True, "sb mana": 362, "casts corruption":True, 'extra aff hit':.1, 'nf_flag': True}
spec_properties['md_ruin_wo_corruption']={"shadow mod": 1.21, "imp": False, "succubus": True, "ruin":True, "isb_flag":True, "sb mana": 362, "casts corruption":False, 'extra aff hit':0, 'nf_flag': False}
spec_properties['ds_ruin_w_corruption']={"shadow mod": 1.27, "imp": False, "succubus": False, "ruin":True, "isb_flag":True, "sb mana": 355, "casts corruption":True, 'extra aff hit':0, 'nf_flag': False}
spec_properties['md_ruin']={"shadow mod": 1.21, "imp": False, "succubus": True, "ruin":True, "isb_flag":True, "sb mana": 362}

IMPROVED_IMP = 1.0
DOT_MITIGATION = .006
MITIGATION = .06
MOD = 1


class Succubus:
    def __init__(self):
        self.statistics = {'damage':0, 'hits':0}
        self.damage = 0
        self.t = 0
        self.auto_attack_cd = 2
        self.BB_TIMES = [0,0]
        self.lash_of_pain_cd = 7.0
        self.log = []
        self.HIT=0
        self.CRIT=0
        self.SP=0
        self.mana = 1898
        self.LASH_MANA_COST= 115
        self.LASH_OF_PAIN_BASE = 160
        self.MD_BONUS = 1.0
        self.CRIT = .0608
        self.HIT = .83
        self.SHADOW_MOD = 0
        self.BB_BONUS = 1.0
        self.isb_times = []
        self.MELEE_MISS = .08
        self.MELEE_DODGE = .065
        self.MELEE_CRIT = .084
        self.MELEE_GLANCING = .40
        self.MELEE_BLOCK = 0
        
    def set_values(self,encounter_time, isb_times, shadow_mod, md_bonus, bb_times):
        self.ENCOUNTER_TIME=encounter_time
        self.SHADOW_MOD = shadow_mod
        self.isb_times = isb_times
        self.MD_BONUS = md_bonus
        self.BB_TIMES = bb_times

    def outside_interval(self,t):
        for interval in self.isb_times:
            if t > interval[0] and t < interval[1]:
                return interval[1]-t
        return 0

    def castLashOfPain(self):
        '''
            Only casts outside of ISB intervals
        '''
        until_outside_interval = self.outside_interval(self.t)
        if until_outside_interval <= 0:
            self.mana -= self.LASH_MANA_COST
            if random.random() < self.HIT:
                self.statistics['hits']+=1
                dmg = self.LASH_OF_PAIN_BASE*self.SHADOW_MOD*(1-MITIGATION)*self.MD_BONUS*self.BB_BONUS
                if random.random() < self.CRIT:
                    self.statistics['damage']+=dmg*1.5
                else:
                    self.statistics['damage']+=dmg
            return self.lash_of_pain_cd
        else:
            return until_outside_interval


    def castAutoAttack(self):
            dmg = random.randint(100,135)
            carry_over = 0 
            roll = random.random()
            if roll < self.MELEE_MISS + carry_over:
                return self.auto_attack_cd
            carry_over+=self.MELEE_MISS

            if roll < self.MELEE_DODGE + carry_over:
                return self.auto_attack_cd
            carry_over+=self.MELEE_DODGE

            if roll < self.MELEE_GLANCING + carry_over:
                self.statistics['damage']+=dmg*self.MD_BONUS*self.BB_BONUS*.65
                return self.auto_attack_cd
            carry_over+=self.MELEE_GLANCING

            if roll < self.MELEE_BLOCK + carry_over:
                return self.auto_attack_cd
            carry_over+=self.MELEE_BLOCK

            if roll < self.MELEE_CRIT + carry_over:
                self.statistics['damage']+=dmg*self.MD_BONUS*self.BB_BONUS*2.0
                return self.auto_attack_cd

            #NORMAL
            self.statistics['damage']+=dmg*self.MD_BONUS*self.BB_BONUS
            return self.auto_attack_cd

    def end(self):
        return 1000

    def getAction(self):
        if self.mana > self.FB_MANA_COST:
            return self.castFirebolt()
        else:
            return self.end()

    def run(self):
        #Auto attacks
        self.t=0
        delta_t = 0
        self.BB_BONUS=1
        while self.t < self.ENCOUNTER_TIME:
          if self.t > self.BB_TIMES[0] and self.t <= self.BB_TIMES[1]:
            self.BB_BONUS = 2
          else:
            self.BB_BONUS = 1
          delta_t = self.castAutoAttack()
          self.t+=delta_t

        #Lashes of pain
        self.t = 0
        delta_t = 0
        self.BB_BONUS=1
        while self.t < self.ENCOUNTER_TIME:
          if self.t > self.BB_TIMES[0] and self.t <= self.BB_TIMES[1]:
            self.BB_BONUS = 2
          else:
            self.BB_BONUS = 1
          delta_t = self.castLashOfPain()
          self.t+=delta_t

        self.statistics['dps']=self.statistics['damage']/self.ENCOUNTER_TIME

        return self.statistics

class Imp:
    def __init__(self):
        self.statistics = {'damage':0,
                      'hits':0,
                      'dmg':0}
        self.damage = 0
        self.t = 0
        self.log = []
        self.HIT=0
        self.CRIT=0
        self.SP=0
        self.mana = 1898
        self.FB_MANA_COST= 115
        self.CRIT = .0608
        self.HIT = .83
        self.FIRE_MOD = 1.1
        
    def set_values(self,encounter_time):
        self.ENCOUNTER_TIME=encounter_time

    def castFirebolt(self):
        self.mana -= self.FB_MANA_COST
        if random.random() < self.HIT:
            self.statistics['hits']+=1
            dmg = 96*self.FIRE_MOD*(1-MITIGATION)*MOD*IMPROVED_IMP
            if random.random() < self.CRIT:
                self.statistics['damage']+=dmg*1.5
            else:
                self.statistics['damage']+=dmg
        return 2.0

    def end(self):
        return 1000

    def getAction(self):
        if self.mana > self.FB_MANA_COST:
            return self.castFirebolt()
        else:
            return self.end()

    def run(self):
        self.t=0
        delta_t = 0
        while self.t < self.ENCOUNTER_TIME:
          delta_t = self.getAction()
          self.t+=delta_t
        self.statistics['dps']=self.statistics['damage']/self.ENCOUNTER_TIME
        return self.statistics

class Player:
    def __init__(self, spec):
        self.statistics = {'damage':0,
                      'sb_hits':0,
                      'corr_hits':0,
                      'dmg_sb':0,
                      'dmg_corr':0,
                      'life_taps': 0}
        self.spec = spec
        #spec_properties['md/ruin']={"shadow mod": 1.27, "imp": False, "succubus": True, "ruin":True, "isb_flag":True}
        self.imp = spec_properties[spec]['imp']
        self.succubus = spec_properties[spec]['succubus']
        self.ruin = spec_properties[spec]['ruin']
        self.isb_flag = spec_properties[spec]['isb_flag']
        self.SHADOW_MOD = spec_properties[spec]['shadow mod']
        self.SB_MANA=spec_properties[spec]['sb mana']
        self.AFF_HIT_PLUS = spec_properties[spec]['extra aff hit']
        self.nf_flag = spec_properties[spec]['nf_flag']

        self.damage = 0
        self.casts_corruption = spec_properties[spec]['casts corruption']
        self.db_corruption = False
        self.db_isb = False
        self.talisman_ticks = 1
        self.talisman_reset = 0
        self.talisman_buff = 0 
        self.isb_reset = 0 
        self.isb_ticks = 4
        self.nightfall_proc = False
        self.isb = 1
        self.gcd = 0
        self.corruption_ticks = []
        # self.mana = MAX_MANA
        self.t = 0
        self.log = []

        self.dmg_sb = 0
        self.dmg_corr = 0 
        self.sb_hits = 0
        self.corr_hits = 0
        self.AFF_HIT=0
        self.DES_HIT=0
        self.CRIT=0
        self.SP=0
        self.SHADOW_SP=0
        
    def set_values(self,sp,hit,crit,mana,encounter_time):
        self.SP=sp
        self.CRIT=crit
        self.AFF_HIT = hit + self.AFF_HIT_PLUS
        self.DES_HIT = hit 
        self.mana=mana
        self.ENCOUNTER_TIME=encounter_time

    def castCorruption(self):
        self.mana -= CORR_MANA
        if random.random() < self.AFF_HIT:
            self.statistics['corr_hits']+=1
            self.corruption_ticks = [self.t+3,self.t+6,self.t+9,self.t+12,self.t+15,self.t+18]
            self.db_corruption = True
        return CORR_CAST_TIME

    def castShadowBolt(self):

        log = str("Cast shadowbolt")

        self.mana-=self.SB_MANA
        self.statistics['sb_hits']+=1
        if random.random() < self.DES_HIT:
            self.isb_ticks-=1
            if random.random() < self.CRIT:
                if self.ruin==True:
                    self.statistics['damage']+=(SB_BASE+(self.SP+self.SHADOW_SP+self.talisman_buff)*SB_COEF)*self.SHADOW_MOD*(1-MITIGATION)*MOD*2*self.isb;
                    self.statistics['dmg_sb']+=(SB_BASE+(self.SP+self.SHADOW_SP+self.talisman_buff)*SB_COEF)*self.SHADOW_MOD*(1-MITIGATION)*MOD*2*self.isb;
                else:
                    self.statistics['damage']+=(SB_BASE+(self.SP+self.SHADOW_SP+self.talisman_buff)*SB_COEF)*self.SHADOW_MOD*(1-MITIGATION)*MOD*1.5*self.isb;
                    self.statistics['dmg_sb']+=(SB_BASE+(self.SP+self.SHADOW_SP+self.talisman_buff)*SB_COEF)*self.SHADOW_MOD*(1-MITIGATION)*MOD*1.5*self.isb;
                if self.isb_flag:
                    self.isb = 1.2
                    self.isb_reset = self.t + 12
                    self.isb_ticks = 4
            else:
              self.statistics['damage']+=(SB_BASE+(self.SP+self.SHADOW_SP)*SB_COEF)*self.SHADOW_MOD*(1-MITIGATION)*MOD*self.isb;
              self.statistics['dmg_sb']+=(SB_BASE+(self.SP+self.SHADOW_SP)*SB_COEF)*self.SHADOW_MOD*(1-MITIGATION)*MOD*self.isb;
            if self.nightfall_proc:
                self.nightfall_proc = False
                return 1.5
        return SB_CAST_TIME


    def lifeTap(self):
        log = "Casts lifetap: " + str(self.mana) + ","
        self.statistics['life_taps']+=1
        self.mana+=(LT_BASE+(self.SP+self.SHADOW_SP+self.talisman_buff)*LT_COEF)*LT_MOD
        log += str(self.mana)
        self.log.append(log)
        return LT_CAST_TIME

    def getAction(self):
        self.talisman_ticks = 0 
        if self.talisman_ticks > 0 and self.talisman_reset < t:
            self.talisman_ticks-=1;
            self.talisman_reset = t + 15
            self.talisman_buff = 175
        if self.casts_corruption and self.db_corruption is False:
            if self.mana > CORR_MANA:
                return self.castCorruption()
            else:
                return self.lifeTap()
        else:
            if self.mana > self.SB_MANA:
                return self.castShadowBolt()
            else:
                return self.lifeTap()

    def processEvents(self,delta_t):
        if self.db_corruption:
            if self.corruption_ticks[0] >= self.t and self.corruption_ticks[0] < self.t+delta_t:
                if random.random() < .04 and self.nf_flag:
                    self.nightfall_proc = True
                    # print("NF")
                temp_tb = 0
                temp_isb = 1
                if self.corruption_ticks[0] <= self.talisman_reset:
                    temp_tb = self.talisman_buff
                if self.corruption_ticks[0] <= self.isb_reset:
                    temp_isb = self.isb

                self.statistics['damage']+=(CORR_BASE+(self.SP+self.SHADOW_SP+temp_tb)*CORR_COEF)*self.SHADOW_MOD*(1-DOT_MITIGATION)*MOD/6*temp_isb
                self.statistics['dmg_corr']+=(CORR_BASE+(self.SP+self.SHADOW_SP+temp_tb)*CORR_COEF)*self.SHADOW_MOD*(1-DOT_MITIGATION)*MOD/6*temp_isb
                self.corruption_ticks.remove(self.corruption_ticks[0])
                if len(self.corruption_ticks) == 0:
                    self.db_corruption=False
        if self.isb_ticks <= 0 or self.isb_reset < self.t + delta_t:
            self.isb = 1
        if self.talisman_reset < self.t + delta_t:
            self.talisman_buff = 0 

    def run(self):
        self.t=0
        delta_t = 0
        while self.t < self.ENCOUNTER_TIME:
          delta_t = self.getAction()
          self.processEvents(delta_t)
          self.t+=delta_t
        self.statistics['dps']=self.statistics['damage']/self.ENCOUNTER_TIME
        return self.statistics
