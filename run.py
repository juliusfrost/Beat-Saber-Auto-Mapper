# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 02:56:44 2019

@author: Julius
"""

import json
import os
import numpy as np

files = os.listdir()
filename = ''
for i in files:
    if '.json' in i:
        filename = i

data = json.load(open(filename))

print(data.keys())


def pretty_print(data):
    print(json.dumps(data, indent=4))


note_data = data['_notes']

# 0 is cut up, 1 is cut down, 2 is cut left, 3 is cut right, 4 is cut up left,
# 5 is cut up right, 6 is cut down left, 7 is cut down right,
# 8 is cut any direction
directions = {0:[0,1], 1:[0,-1], 2:[-1,0], 3:[1,0], 4:[-1,1], 5:[1,1], 
              6:[-1,-1], 7:[1,-1], 8:[0,0]}

unit_vectors = []
for i in range(8):
    v = directions[i]
    cut_vector = np.array(v)
    cut_vector = cut_vector / np.linalg.norm(cut_vector)
    unit_vectors.append(cut_vector)

print(unit_vectors)

angle = 30

print(len(note_data))

def coordinates(lineIndex, lineLayer):
    # 0, 1, 2, 3
    x = lineIndex - 1.5
    # 0, 1, 2
    y = lineLayer - 1
    return np.array([x,y])

w1 = 1
w2 = 0.5
w3 = 1
w4 = 0.1

last_visited = np.zeros((4,3))

prev_position = np.array([0,0])
prev_direction = np.array([0,1])
prev_time = 0
for i, note in enumerate(note_data):
    time = note['_time']
    #lineIndex = note['_lineIndex']
    #lineLayer = note['_lineLayer']
    noteType = note['_type']
    if noteType == 1:
        continue
    #cutDirection = note['_cutDirection']
    
    #cut_vector = unit_vectors[cutDirection]
    #position = coordinates(lineIndex, lineLayer)
    
    scores = []
    log = []
    for lineIndex in range(4):
        for lineLayer in range(3):
            if (lineIndex == 1 or lineIndex == 2) and lineLayer == 1:
                continue
            for cutDirection in range(8): #let's not deal with no direction
                cut_vector = unit_vectors[cutDirection]
                position = coordinates(lineIndex, lineLayer)
                
                perimeter_angle = np.arccos((position@cut_vector) / (np.linalg.norm(position) * np.linalg.norm(cut_vector)))
                #print(angle)
                if perimeter_angle > np.pi / 2:
                    #print('illegal note')
                    continue
                
                u = prev_position + prev_direction - position
                v = - cut_vector
                a = np.arccos((u @ v) / (np.linalg.norm(u) * np.linalg.norm(v)))
                if not (0 <= a and a <= np.pi / 6):
                    continue
                
                angle = np.arccos((prev_direction@cut_vector) / (np.linalg.norm(prev_direction) * np.linalg.norm(cut_vector)))
                if angle < np.pi / 2:
                    continue
                
                distance = np.linalg.norm(position - prev_position)
                time_difference = time - prev_time
                urge = time - last_visited[lineIndex,lineLayer]
                
                score = 0
                score += w1 * angle
                score += w2 * urge
                score += w3 * 1/(a+0.2)
                score += w4 * np.log(time_difference + 1) * (np.linalg.norm(prev_position + prev_direction - position))
                
                scores.append(score)
                log.append((lineIndex, lineLayer, cutDirection))
    
    x = np.array(scores)
    #print(x)
    softmax = np.exp(x)/np.sum(np.exp(x))
    idx = np.random.choice(len(log), p=softmax)
    lineIndex, lineLayer, cutDirection = log[idx]
    last_visited[lineIndex,lineLayer]=time

    #print(lineIndex, lineLayer, cutDirection)      
    #print(last_visited)
    
    note['_lineIndex'] = lineIndex
    note['_lineLayer'] = lineLayer
    note['_cutDirection'] = cutDirection
    
    #assert data['_notes'][i]['_lineIndex'] == lineIndex
    
    prev_position = coordinates(lineIndex, lineLayer)
    prev_direction = unit_vectors[cutDirection]
    prev_time = time

json.dump(data, open('Expert.json', 'w'))