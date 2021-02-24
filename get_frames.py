import csv
import pandas as pd
import os
from bs4 import BeautifulSoup as bs

def choose_files_annotations(row):
    #path of annotations  map
    clips_dir = 'annotations/'
    clips_path = os.listdir(clips_dir)
    set_counter = 1
    vid_counter = 1
    
    #Loop through folders of annotations dataset
    for folder in clips_path:
        if row['set'] == set_counter:
            clips_dir = clips_dir + folder
            clips_path = os.listdir(clips_dir)
            
            #Find correct annotations to search through within selected folder
            for vid in clips_path:
                if row['video'] + 1 == vid_counter:
                    clips_dir = clips_dir + '/' + vid
                    return clips_dir
                vid_counter += 1

        set_counter += 1

def choose_files_attributes(row):
    clips_dir = 'annotations_attributes/'
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

def find_pedestrian(bs_annot,bs_attr, int_frame):
    look_array = []
    cross_array = []
    #retrieve the full pedestrian object from the data
    ped_frame = bs_annot.find_all('box', attrs={'frame': int_frame}) #make this find_all??

    #check if the frame found in XML file belongs to a pedestrian
    for entity in ped_frame:
        if entity.parent.attrs['label'] == 'pedestrian':
            pedestrian = entity.parent

            #get pedestrian id and check if crossing moment exists
            cross_frame = get_cross_frame(pedestrian, bs_attr)

            #using find box function filters out newline in children element
            frames = pedestrian.find_all('box')
    
            for frame in frames:
                looking = frame.find('attribute', attrs={'name':'look'}).string
                if looking == 'looking':
                    
                    #this returns the first frame (in ms) on which somebody is looking
                    frame_to_sec = int(float(frame['frame'])*1000/30)
                    look_array.append(frame_to_sec)
                    break
            
            cross_array.append(cross_frame)

    ped_array = [look_array,cross_array]       
    return ped_array   

def concat_array(array):
    concat_str = 'Frames found: '

    if len(array) == 0:
        concat_str = 'no frames found'
    else:
        for element in array:
            concat_str = concat_str + str(element) + '+'
    
    return concat_str

def get_cross_frame(ped, bs_attr):
    ped_cross_id = ped.find('attribute', attrs={'name':'id'}).string
    ped_cross_match = bs_attr.find('pedestrian', attrs={'id': ped_cross_id})
    #Match pedestrian attributes and annotations, and check if crossing = 1 (meaning pedestrian is crossing)
    #if so, save the frame on which pedestrian starts crossing
    if (ped_cross_id == ped_cross_match['id']) and bs_attr.pedestrian['crossing'] == '1':
        cross_frame = ped_cross_match['crossing_point']
        #get crossing frame (in ms)
        cross_frame = int(float(cross_frame)*1000/30)
    else:
        cross_frame = 'no crossing'

    return cross_frame




"""Here Goes main function"""
df = pd.read_csv('mapping.csv')

#for over rows in mapping
for index, row in df.iterrows():
    
    #Create beautifulsoup objects of xml files annotations and attributes
    xml_annotations = choose_files_annotations(row)
    xml_attributes = choose_files_attributes(row)
    #open xml file as readable and create Beautifulsoup object
    xml_annot_content = open(xml_annotations,'r')
    bs_annot_content = bs(xml_annot_content, 'lxml')

    xml_attr_content = open(xml_attributes, 'r')
    bs_attr_content = bs(xml_attr_content, 'lxml')

    #Get interaction frame from csv file, and use it to get the frame of looking + crossing
    int_frame = row['interaction_frame']

    #Save looking + crossing moment in one array
    ped_array = find_pedestrian(bs_annot_content, bs_attr_content, int_frame)
    
    #Create strings of arrays and save into csv file
    look_frame = concat_array(ped_array[0])
    cross_frame = concat_array(ped_array[1])
    df.loc[index,'look_moment']=look_frame
    df.loc[index,'cross_moment']=cross_frame

    # row['look_moment']=find_pedestrian(bs_content, int_frame)
    df.to_csv('modified_mapping.csv', index=False)
    #if index == 29:
    #    print('lets stop this')
