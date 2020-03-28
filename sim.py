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
spec_properties['sm/ruin']={"shadow mod": 1.21, "imp": True, "succubus": False, "ruin":True, "isb_flag":True, "sb mana": 362}
spec_properties['ds/ruin']={"shadow mod": 1.27, "imp": False, "succubus": False, "ruin":True, "isb_flag":True, "sb mana": 355}
spec_properties['md/ruin']={"shadow mod": 1.21, "imp": False, "succubus": True, "ruin":True, "isb_flag":True, "sb mana": 362}

IMPROVED_IMP = 1.0
DOT_MITIGATION = .006
MITIGATION = .06
MOD = 1


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
    def __init__(self, spec, casts_corruption):
        self.statistics = {'damage':0,
                      'sb_hits':0,
                      'corr_hits':0,
                      'dmg_sb':0,
                      'dmg_corr':0,
                      'life_taps': 0}
        self.spec = spec
        #spec_properties['md/ruin']={"shadow mod": 1.27, "imp": False, "succubus": True, "ruin":True, "isb_flag":True}
        self.pets = [] 
        if spec_properties[spec]['succubus']:
            self.pets.append(Succubus())
        if spec_properties[spec]['imp']:
            self.pets.append(Imp())
        self.ruin = spec_properties[spec]['ruin']
        self.isb_flag = spec_properties[spec]['isb_flag']
        self.SHADOW_MOD = spec_properties[spec]['shadow mod']
        self.SB_MANA=spec_properties[spec]['sb mana']

        self.damage = 0
        self.casts_corruption = casts_corruption
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
        if spec == "sm":
            self.AFF_HIT = hit + .1
        else:
            self.AFF_HIT = hit
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
                if random.random() < .04 and nf_flag:
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
