import csv
import pandas as pd
import subprocess
import os

df = pd.read_csv('mapping.csv')

#Function to check if folder to save trimmed files in exists. If not, create these folders
def dir_check(path):
    if os.path.exists(path):
        print('folder exists already!!')
    else:
        os.makedirs('trimmed/C_L')
        os.makedirs('trimmed/C_nL')
        os.makedirs('trimmed/nC_L')
        os.makedirs('trimmed/nC_nL')
        os.makedirs('trimmed/ped_crossing')
        os.makedirs('trimmed/traffic_lights')
        os.makedirs('trimmed/stop_sign')


#Function which chooses the correct file to trim
def choose_files(row):
    #path of PIE dataset map
    clips_dir = 'PIE_clips/'
    clips_path = os.listdir(clips_dir)
    set_counter = 1
    vid_counter = 1
    
    #Loop through folders of PIE dataset
    for folder in clips_path:
        if row['set'] == set_counter:
            clips_dir = clips_dir + folder
            clips_path = os.listdir(clips_dir)
            
            #Find correct video to trim within selected folder
            for vid in clips_path:
                if row['video'] == vid_counter:
                    clips_dir = clips_dir + '/' + vid
                    return clips_dir
                vid_counter += 1

        set_counter += 1

#Function that saves trimmed video in correct folder, with correct name
def save_file(row):

    #Check if directory already exists, otherwise create directory to put files in
    dir_path = 'trimmed/'
    dir_check(dir_path)

    file_name = (str(row['id_segment']) + '_' + str(row['set']) 
                 + '_' + str(row['video']) + '.mp4')

    if row['traffic_rules'] == 'none':
        dir_path = dir_path + row['cross-look'] + '/' + file_name 
    else:
        dir_path = (dir_path + row['traffic_rules'] + '/' 
                    + row['cross-look'] + '_'+ file_name)
    return dir_path
        

#for over rows in mapping
for index, row in df.iterrows():
    print('trimming ' + str(index) + ' with start=' +
          str(row['start']) + ' Duration = 15s')

    subprocess.call(['ffmpeg',
                     '-y',
                     '-loglevel', 'quiet',
                     '-ss', row['start'],
                     '-t', '15',  
                     '-i', choose_files(row),
                     '-c', 'copy',
                     save_file(row)])