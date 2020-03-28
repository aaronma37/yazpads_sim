import numpy as np
import math
import inspect
import pickle
from scipy.interpolate import interp1d, Rbf,LinearNDInterpolator
import pylab as P
import os
from scipy.spatial.distance import cdist, pdist, squareform
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model


target = "md_ruin"
main_path=os.path.dirname(os.path.realpath(__file__))
datapath+='/'+target+'/data/'
os.chdir(data_path)

dist_list = np.arange(0,1.05,.05) 

fp_list=[]
for file in os.listdir(data_path):
    fp_list.append(file)
print(datapath+"file #: ", len(fp_list))

data = {}
num = len(fp_list)
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
            n[ind] = {"avg": 0, "dist": {}}
            for d in dist_list:
                n[ind][dist][d]=0
        n[ind]['avg']+=avg/10
        for k in n[ind]['dist'].keys():
            n[ind]['dist'][k]+=dist[k]/10


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

predict = [[473,.19,.85,4793,30]]

poly = PolynomialFeatures(degree=2)
X_ = poly.fit_transform(X)
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
# print(clf_avg.predict(predict_))
# print(predict_[0])
# ans=0
# for k in range(len(clf_avg.coef_)):
#     ans+=clf_avg.coef_[k]*predict_[0][k]
    # print(clf_avg.coef_[k],predict_[0][k],ans)
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
