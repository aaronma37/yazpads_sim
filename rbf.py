import numpy as np
import math
import inspect
import pickle
from scipy.interpolate import interp1d, Rbf,LinearNDInterpolator
import pylab as P
import os
from scipy.spatial.distance import cdist, pdist, squareform



main_path=os.path.dirname(os.path.realpath(__file__))
main_path+='/data_sm/'
fp_list=[]
os.chdir(main_path)

for file in os.listdir(main_path):
    fp_list.append(file)
print(main_path+"file #: ", len(fp_list))

data = {}
num = len(fp_list)
print(len(fp_list))
# exit()
n={}
for fp in fp_list:
    try:
        results=pickle.load(open(fp,"rb"))
    except:
        continue
    for k in results: #k[0] = ind.var, k[1] = [avg, dist]
        ind = k[0]
        avg = k[1][0]
        dist = k[1][1]
        if n.get(ind) is None:
            n[ind] = {"avg": 0, "dist": {.1: 0, .2:0, .3:0, .4:0, .5:0, .6:0, .7:0, .8:0, .9:0}}
        n[ind]['avg']+=avg/10
        for k in n[ind]['dist'].keys():
            n[ind]['dist'][k]+=dist[k]/10


# for k,v in n.items():
#     print(k,v)
# exit()

#x = []
#sp = []
#crit = []
#hit = []
#y = []

#data_dict = {}
#for d in data:
#    data_dict[(d[0],d[1],d[2])]=(d[3],d[4])
#    sp.append(d[0])
#    crit.append(d[1])
#    hit.append(d[2])
#    y.append(d[3])
#for i in range(600,650,5):
#    print(data_dict[(i,0.10,0.85)])

## create interpolator
## rbf_interp = Rbf(sp,crit,hit, y, function='cubic')
#rbf_interp = Rbf(sp,crit,hit, y, function='linear')
## print(rbf_interp.nodes)
## print(len(y))
## print(rbf_interp.xi[1],"D")
## print(len(rbf_interp.nodes))

#sp_ = 600
#crit_ = .16
#hit_ = .91
#print(rbf_interp([sp_],[crit_],[hit_]),data_dict[(sp_,crit_,hit_)])

#sp_ = 601
#print(rbf_interp([sp_],[crit_],[hit_]))

#sp_ = 602.5
#print(rbf_interp([sp_],[crit_],[hit_]))

#sp_ = 604
#print(rbf_interp([sp_],[crit_],[hit_]))

#sp_ = 604.5
#print(rbf_interp([sp_],[crit_],[hit_]))

#sp_ = 605
#crit_ = .16
#hit_ = .91
#print(rbf_interp([sp_],[crit_],[hit_]),data_dict[(sp_,crit_,hit_)])

#sp_ = 605
#crit_ = .1
#hit_ = .87
#print(rbf_interp([sp_],[crit_],[hit_]),data_dict[(sp_,crit_,hit_)])

#hit_ = .86
#print(rbf_interp([sp_],[crit_],[hit_]))

#hit_ = .93
#print(rbf_interp([sp_],[crit_],[hit_]),data_dict[(sp_,crit_,hit_)])

#def norm(a,b):
#    v = 0
#    for i in range(len(a)):
#        v+=(b[i]-a[i])**2
#    v=math.sqrt(v)
#    return v


#def norm2(x1, x2):
#        return cdist(x1.T, x2.T, rbf_interp.norm)

#hit_ = .94
#v=0
#args = [np.asarray(x) for x in [sp_,crit_,hit_]]
#xa = np.asarray([a.flatten() for a in args], dtype=np.float_)
#for i in range(len(y)):
#    xb = np.asarray([a.flatten() for a in [rbf_interp.xi[0][i],rbf_interp.xi[1][i],rbf_interp.xi[2][i]]], dtype=np.float_)
#    n = norm(xb,xa)
#    # n2 = norm2(xb,xa)
#    # print(n,n2)
#    # print(n)
#    v+=n*rbf_interp.nodes[i]

##Export for sheets
#import csv

#with open('xi0.csv', 'w') as myfile:
#    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
#    wr.writerow(rbf_interp.xi[0])

#np.savetxt("xi0n.csv", rbf_interp.xi[0], delimiter=',', fmt='%d')
#np.savetxt("xi1n.csv", rbf_interp.xi[1], delimiter=',', fmt='%f')

#with open('xi1.csv', 'w') as myfile:
#    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
#    wr.writerow(rbf_interp.xi[1])

#with open('xi2.csv', 'w') as myfile:
#    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
#    wr.writerow(rbf_interp.xi[2])

#with open('nodes.csv', 'w') as myfile:
#    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
#    wr.writerow(rbf_interp.nodes)

from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model

# X = [[0.44, 0.68], [0.99, 0.23]]
X = []
y_avg = []
y_dist = {}
y_dist =  {.1: [], .2:[], .3:[], .4:[], .5:[], .6:[], .7:[], .8:[], .9:[]}
for k,v in n.items():
    # X.append([sp[i],crit[i],hit[i]])
    X.append([k[0],k[1],k[2],k[3],k[4]])
    y_avg.append(v['avg'])
    for k in y_dist.keys():
        y_dist[k].append(v['dist'][k])
# print(X)
# print("HERE")

# vector = [109.85, 155.72]
# predict= [0.49, 0.18]
predict = [[473,.19,.85,4793,30]]

poly = PolynomialFeatures(degree=2)
X_ = poly.fit_transform(X)
# poly.powers_.remove([3,0,0])
# print(X)
# print(poly.powers_)
predict_ = poly.fit_transform(predict)


###
clf_avg = linear_model.LinearRegression(fit_intercept=False)
clf_avg.fit(X_, y_avg)
np.savetxt("coeff/coef_avg.csv", clf_avg.coef_, delimiter=',', fmt='%f')

clf_dist = {}
for k in y_dist.keys():
    clf_dist[k] = linear_model.LinearRegression(fit_intercept=False)
    clf_dist[k].fit(X_, y_dist[k])
    np.savetxt("coeff/coef_dist"+str(k)+".csv", clf_dist[k].coef_, delimiter=',', fmt='%f')


# print(input_text)
print(clf_avg.predict(predict_))
print(predict_[0])
ans=0
for k in range(len(clf_avg.coef_)):
    ans+=clf_avg.coef_[k]*predict_[0][k]
    print(clf_avg.coef_[k],predict_[0][k],ans)
# print(ans+clf.intercept_)



ident_dict = {0: "cSP", 1: "cCrit", 2: "cHIT", 3:"cMANA", 4:"cTIME"}
name = "coeff_ds_nc_avg"
input_text = "="
for i in range(len(poly.powers_)):
    # input_text+="$A$"+str(i+1)
    input_text+="index("+name+","+str(i+1)+",0)"
    for j in range(len(poly.powers_[i])):
        for k in range(poly.powers_[i][j]):
            input_text+="*"+ident_dict[j]
    # if i != len(poly.powers_)-1:
    input_text+="+"

# input_text+=str(clf.intercept_)
print(input_text)

ident_dict = {0: "cSP", 1: "cCRIT", 2: "cHIT", 3:"cMANA", 4:"cTIME"}
name = "c"
input_text = "="
for i in range(len(poly.powers_)):
    # input_text+="$A$"+str(i+1)
    input_text+="c["+str(i)+"][0]"
    for j in range(len(poly.powers_[i])):
        for k in range(poly.powers_[i][j]):
            input_text+="*"+ident_dict[j]
    if i != len(poly.powers_)-1:
        input_text+="+"

# input_text+=str(clf.intercept_)
print(input_text)
