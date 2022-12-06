import os
import shutil

path = 'C:\\Users\\guilh\\OneDrive\\Desktop\\mInfProject\\miniRGB_dataset\\MINI-RGBD_web'
targetPath = 'C:\\Users\\guilh\\Documents\\bb3DPoseVisualizer\\joints3D'

entries = os.listdir(path)

for i in range(6):
    entries.pop()

for entry in entries:
    try:
        os.mkdir(os.path.join('joints3D', entry))
        tmp_target_folder = targetPath+'\\'+entry
        tmp_joints_path   = path+'\\'+entry+'\\joints_3D' #path for dataset joint data.
        tmp_plane_path    = path+'\\'+entry+'\\bg_plane.txt'
        print('Loading data...')
        shutil.copytree(tmp_joints_path, tmp_target_folder, dirs_exist_ok=True)
        shutil.copy(tmp_plane_path, tmp_target_folder)
    except OSError as e:
        if e.errno != 17:
            print("Error", e)
print('Data loaded.')

def giveDataEntries():
    return entries