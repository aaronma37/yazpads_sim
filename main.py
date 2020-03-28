import random
import datetime
import os
import numpy as np
import pickle
import time
from sims import Player, Imp, Succubus
from copy import deepcopy

process_name = str(os.getpid()) + str(
    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+str(random.random())
)

spec = "md_ruin"
dist_list = np.arange(0,1.05,.05)
main_path=os.path.dirname(os.path.realpath(__file__))
save_path = main_path+'/'+spec+'/data/'


params = {"sp": range(400,650,20), "crit": np.arange(0.0, .25, 0.03), "hit": np.arange(.83, .99, 0.02), "mana": np.arange(4500,7000,500), "time": np.arange(10,100,20)}
# params = {"sp": range(630,650,20), "crit": np.arange(.22, .25, 0.03), "hit": np.arange(.85, .87, 0.02), "mana": np.arange(5750,6000,250), "time": np.arange(80,100,20)}
val = []
now = time.time()
for sp_ in params["sp"]:
    for crit_ in params["crit"]:
        for hit_ in params["hit"]:
            for mana_ in params["mana"]:
                for time_ in params["time"]:
                    dps_list = []
                    for i in range(1000):
                        player = Player()
                        player.set_values(sp_,hit_,crit_,mana_,time_)
                        player.run()
                        dps_list.append(player.statistics['dps'])
                        if player.imp:
                            imp = Imp()
                            imp.set_values(time_)
                            imp.run()
                            dps_list[-1]+=imp.statistics['dps']
                        if player.succubus:
                            succubus = Succubus()
                            succubus.set_values(time_)
                            succubus.run()
                            dps_list[-1]+=succubus.statistics['dps']
                    dps_list.sort()
                    dist = {}
                    for d in dist_list:
                        if d == 1:
                            dist[d]=dps_list[-1]
                        else:
                            dist[d]=dps_list[int(d*len(dps_list))]
                    avg = sum(dps_list)/len(dps_list)
                    val.append([(sp_,crit_,hit_,mana_,time_),(avg,dist)])

with open(save_path+process_name+'.pickle','wb') as fp:
    pickle.dump(val,fp,pickle.HIGHEST_PROTOCOL)
