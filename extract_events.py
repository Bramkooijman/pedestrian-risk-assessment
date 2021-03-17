import csv
import pandas as pd
import subprocess
import os
import os.path
import time

df = pd.read_csv('mapping.csv')

# current directory (hard to use __file__ in threads)
VIDEOS_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'PIE_clips')

# Function to check if folder to save trimmed files in exists. If not, create these folders

def dir_check(path):
    if os.path.exists(path):
        print('folder exists already!!')
    else:
        os.makedirs('trimmed/nonspecific')
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
    if video_id > 0 and video_id < 10:
        prefix = 'video_000'
    elif video_id >= 10 and video_id < 100:
        prefix = 'video_00'
    elif video_id >= 100 and video_id < 1000:
        prefix = 'video_0'
    else:
        print('wrong video_id given', video_id)
        return None

    file_path = os.path.join(file_path, prefix + str(video_id) + '.mp4')
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
    return dir_path


def get_length(input_video):
    result = subprocess.run(['ffprobe',
                             '-v', 'error',
                             '-show_entries', 'format=duration',
                             '-of', 'default=noprint_wrappers=1:nokey=1',
                             input_video],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    return float(result.stdout)

#Function for creating a 2 second black screen
def black_screen_check():
    if os.path.exists('black_screen.mp4'):
        print("black_screen.mp4 already exists!!")
    else:
        cmd = 'ffmpeg -t 1 -f lavfi -i color=c=black:s=1280x720:r=30/1 -c:v h264 black_screen.mp4'
        cmd = subprocess.Popen(cmd, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            shell=True)
        #out, err = cmd.communicate()

#Function that concatenates the blackscreen and the 
def concat_black_screen(concat_vid, output):
    #create temp file 1 of the black-screen file
    temp1 = 'ffmpeg -i black_screen.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts temp1.ts'
    temp1 = subprocess.Popen(temp1, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            shell=True)
    time.sleep(1)
    #Create temp file 2 of the vid on which you want to append
    temp2 = 'ffmpeg -i ' + concat_vid + ' -c copy -bsf:v h264_mp4toannexb -f mpegts temp2.ts'
    temp2 = subprocess.Popen(temp2, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            shell=True)
    time.sleep(1)
    #Code to concat the 2 files, and output in the same place as input is taken from.
    concat = 'ffmpeg -i "concat:temp1.ts|temp2.ts" -c copy -bsf:a aac_adtstoasc ' + output
    concat = subprocess.Popen(concat, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            shell=True)
    time.sleep(1)
    #remove temporary files
    os.remove('temp1.ts')
    os.remove('temp2.ts')

def add_audio(file_in, file_out):
    temp1 = 'ffmpeg -i ' + file_in + ' -i emptysound.mp3 -map 0:v:0 -map 1:a:0 ' + file_out
    temp1 = subprocess.Popen(temp1, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            shell=True)


"""Here Goes main function"""
if __name__ == "__main__":
    dir_check('trimmed/')
    black_screen_check()
    # for over rows in mapping
    for index, row in df.iterrows():
        if index > 79:
            file_in = choose_files(row['set'], row['video'])
            if file_in:
                print('trimming ' + str(index) + ' with start='
                    + str(row['start']) + ' Duration = 15s')
                file_out = save_file(row)
                subprocess.call(['ffmpeg',
                                '-y',
                                '-i', file_in,
                                '-ss', row['start'],
                                '-t', '00:00:15.000',
                                '-s', '1280x720',
                                '-crf', '28',
                                '-loglevel', 'quiet',
                                #'-c', 'copy',
                                file_out])

                #call function to add blackscreen
                trimmed_no_audio = 'noaudio/video_' + str(index) + '.mp4'
                trimmed_audio = 'Trimmed_final/video_' + str(index) + '.mp4'
                #add blackscreen
                concat_black_screen(file_out, trimmed_no_audio)
                #add low frequency audio
                add_audio(trimmed_no_audio, trimmed_audio)
                time.sleep(10)
                print('saved to ' + trimmed_audio + ' with length of ' + str(get_length(trimmed_audio)))
            else:
                print('video ' + str(row['video']) + ' from set ' + str(row['set'])
                    + ' could not be loaded')
