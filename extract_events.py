import csv
import pandas as pd
import subprocess
import os
import os.path

df = pd.read_csv('mapping.csv')

# current directory (hard to use __file__ in threads)
VIDEOS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'PIE_clips')

# Function to check if folder to save trimmed files in exists. If not, create these folders


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


# Function which chooses the correct file to trim
def choose_files(set_id, video_id):
    file_path = os.path.join(VIDEOS_DIR, 'set' + str(set_id))
    file_path = os.path.join(file_path, 'video_000' + str(video_id) + '.mp4')
    if os.path.isfile(file_path):
        return file_path
    else:
        return None


# Function that saves trimmed video in correct folder, with correct name
def save_file(row):
    # Check if directory already exists, otherwise create directory to put files in
    dir_path = 'trimmed/'

    file_name = (str(row['id_segment']) + '_' + str(row['set'])
                 + '_' + str(row['video']) + '.mp4')

    if row['traffic_rules'] == 'none':
        dir_path = dir_path + row['cross-look'] + '/' + file_name
    else:
        dir_path = (dir_path + row['traffic_rules'] + '/'
                    + row['cross-look'] + '_' + file_name)
    print('saved to ' + dir_path + ' with length of ' + str(get_length(dir_path)))
    return dir_path


def get_length(input_video):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_video], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return float(result.stdout)


"""Here Goes main function"""
if __name__ == "__main__":
    dir_check('trimmed/')
    # for over rows in mapping
    for index, row in df.iterrows():
        video_file = choose_files(row['set'], row['video'])
        if video_file:
            print('trimming ' + str(index) + ' with start='
                  + str(row['start']) + ' Duration = 15s')
            subprocess.call(['ffmpeg',
                             '-i', video_file,
                             '-y',
                             '-loglevel', 'quiet',
                             '-ss', row['start'],
                             '-t', '15',
                             '-c', 'copy',
                             save_file(row)])
        else:
            print('video ' + str(row['video']) + ' from set ' + str(row['set'])
                  + ' could not be loaded')
