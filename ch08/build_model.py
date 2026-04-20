import csv
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import get_scorer
import numpy as np
import emlearn

current_window = []
windows = []
window_res = []
window_size = 10
rolling_flick = []
data = []
multiplier=1000

def to_int(data_list):
    output = []
    for datum in data_list:
        output.append(int(float(datum)*multiplier))
    return output

def rolling_av(data, index):
    total = 0
    for item in range(index-window_size, index):
        total = total + int(data[item][4])
     
    if total/window_size < 0.5:
        return 1
    return 0

with open('wand_data.csv') as csvfile:
    flickreader = csv.reader(csvfile, delimiter=',')
    counter = 0
    for row in flickreader:
        data.append(row)
     
for index in range(10, len(data)):
    windows.append(
        to_int([data[index-10][1], data[index-9][1], 
           data[index-8][1],data[index-7][1],data[index-6][1],
           data[index-5][1],data[index-4][1],data[index-3][1],
           data[index-2][1],data[index-1][1],data[index][1],
           data[index-10][2],data[index-9][2],data[index-8][2],
           data[index-7][2],data[index-6][2],data[index-5][2],
           data[index-4][2],data[index-3][2],data[index-2][2],
           data[index-1][2],data[index][2],data[index-10][3],
           data[index-9][3],data[index-8][3],data[index-7][3],
           data[index-6][3],data[index-5][3],data[index-4][3],
           data[index-3][3],data[index-2][3],data[index-1][3],
           data[index][3]]))
    window_res.append(rolling_av(data, index))

estimator = RandomForestClassifier(n_estimators=20, 
                max_depth=15, max_features=7, random_state=1)
estimator.fit(windows[0:800], window_res[0:800])

score = get_scorer('f1')(estimator, windows, window_res)
print("score is: ",score)

# Convert model using emlearn
cmodel = emlearn.convert(estimator, method='inline')

# Save as loadable .csv file
path = 'flick_model.csv'
cmodel.save(file=path, name='flick', format='csv')
print('Wrote model to', path)