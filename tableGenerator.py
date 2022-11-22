import math
import pandas as pd
import numpy as np
import os
from IPython.display import display



def setup_indexes(n_frames, axis=[str]):
    iterables = [np.arange(0,n_frames), axis]
    index = pd.MultiIndex.from_product(iterables, names=['frame','axis'])
    return index
def setup_columns():

    leftLeg = ['leftThigh', 'leftCalf', 'leftFoot', 'leftToes']
    rightLeg = ['rightThigh', 'rightCalf', 'rightFoot', 'rightToes'] 
    leftArm = ['leftShoulder', 'leftUpperArm', 'leftForeArm', 'leftHand', 'leftFingers']
    rightArm = ['rightShoulder', 'rightUpperArm', 'rightForeArm', 'rightHand', 'rightFingers']
    torso = ['global', 'spine', 'spine1', 'spine2', 'neck']
    head = ['head', 'noseVertex']
    arrays = [['leftLeg', leftLeg],
              ['rightLeg', rightLeg],
              ['leftArm', leftArm],
              ['rightArm', rightArm],
              ['torso', torso],
              ['head', head]]
 
    list_of_cats = [subarr[0] for subarr in arrays]
    list_of_joints = [subarr[1] for subarr in arrays]

    single_lvl_columns = leftLeg+rightLeg+leftArm+rightArm+torso+head
    repeated_categories = []
    for j in range(len(list_of_joints)):
        for i in range(len(list_of_joints[j])):
            repeated_categories.append(list_of_cats[j])
    multi_lvl_columns = [repeated_categories, single_lvl_columns]
    multi_lvl_columns = pd.MultiIndex.from_arrays(multi_lvl_columns, names=('category', 'joints'))
    return single_lvl_columns, multi_lvl_columns
def generateTable(path, sequence):

    #get list of files containing joint data and delete unwanted files. Also
    path_sequence = path+'\\'+sequence
    list = os.listdir(path_sequence)
    list.remove('bg_plane.txt')

    #setup indexes and columns:
    n_frames = 1000
    axis = ['x','y','z']
    index = setup_indexes(n_frames, axis)
    cols, multicols = setup_columns()

    #columns has the original non-ordered data. Needed for properly inserting data.
    with open(path+'\\jointList') as file:
        columns = [line.rstrip() for line in file]

    #reshape np.array to final shape and insert dummy data.
    reshape_to = (int(n_frames*len(axis)), len(cols))
    data = np.zeros(math.prod(reshape_to)).reshape(*reshape_to)

    #populate data.
    it = 0
    for frame in list:
        with open(path_sequence+'\\'+frame) as file:
            x = [line.rstrip().split(' ')[0] for line in file]
            data[it] = x
            it+=1
        with open(path_sequence+'\\'+frame) as file:
            y = [line.rstrip().split(' ')[1] for line in file]
            data[it] = y
            it+=1
        with open(path_sequence+'\\'+frame) as file:
            z = [line.rstrip().split(' ')[2] for line in file]
            data[it] = z
            it+=1

    #configure dataframe for proper MultiIndex columns.
    df = pd.DataFrame(data, index, columns)
    df = df.reindex(columns=cols)
    df = df.reindex(columns=multicols, level=1)

    #with open(ind_path+'\\bg_plane.txt') as file:
    #    bg_plane = file.readline().split()[1:]
    
    
    return df