# Created by Johnson Thomas https://github.com/johnyquest7

import gradio as gr
import os
from PIL import Image
import pandas as pd 
import time 
import sys 

# Global variable
annotations = None
file_pd = None 
curr_index = None 
annotation_file = 'thyroid_nodules_annotations.csv'
file_names_csv = 'file_names.csv'
current_directory = os.getcwd()
image_file_directory = str(current_directory)+"/"+"Final_Full_JT"

global annotations
global file_pd
global curr_index

extensions = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.bmp','.BMP']

def get_file_list(root_dir, extensions=None):
    """
    Retrieve a sorted list of files from the specified directory based on the given extensions.
    
    Parameters:
    - root_dir (str): The root directory to start the search from.
    - extensions (list, optional): A list of file extensions to filter the results. If None, all files are returned.
    
    Returns:
    - list: A sorted list of file paths that match the specified extensions.
    """
    
    # Handle the case where extensions is not provided.
    if extensions is None:
        extensions = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG', '.bmp','.BMP']

    file_list = []
    for root, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if any(ext in filename for ext in extensions):
                file_path = os.path.join(root, filename)
                file_list.append(file_path)

    return sorted(file_list)

def load_or_create_annotations(annotation_file, image_file_directory):
    """
    Load annotations from a CSV file if it exists, otherwise create a new DataFrame 
    with specified columns and save it to the CSV file.

    Parameters:
    - annotation_file (str): The path to the annotation CSV file.
    - image_file_directory (str): The directory containing image files.

    Returns:
    - DataFrame: A DataFrame containing annotations.
    """
    
    # Check if the annotation file exists
    if os.path.exists(annotation_file):
        annotations = pd.read_csv(annotation_file)
    else:
        columns = [
            'pd_filename', 'composition', 'echogenicity', 'nod_shape', 'margin',
            'echogenic_foci', 'tirads_points', 'tirads_score'
        ]
        annotations = pd.DataFrame(columns=columns)
        
        # Use the `get_file_list` function to populate filenames
        annotations['pd_filename'] = get_file_list(image_file_directory)
        
        # Save the new DataFrame to the CSV file
        annotations.to_csv(annotation_file, index=False)

    return annotations

annotations= load_or_create_annotations(annotation_file, image_file_directory)

def load_or_create_file_dataframe(file_names_csv, image_file_directory):
    """
    Load file names from a CSV file if it exists, otherwise create a new DataFrame 
    with filenames from the specified directory and save it to the CSV file.

    Parameters:
    - file_names_csv (str): The path to the CSV file that contains file names.
    - image_file_directory (str): The directory containing image files.

    Returns:
    - DataFrame: A DataFrame containing file names.
    """
    
    # Check if the CSV file exists
    if os.path.exists(file_names_csv):
        file_pd = pd.read_csv(file_names_csv)
    else:
        file_data = get_file_list(image_file_directory)
        file_pd = pd.DataFrame(file_data, columns=['file_name'])
        
        # Save the new DataFrame to the CSV file
        file_pd.to_csv(file_names_csv, index=False)

    return file_pd
    
file_pd = load_or_create_file_dataframe(file_names_csv, image_file_directory)

# idxmax() will return 0 if there are no NaN values 
if annotations['composition'].isna().any():
    curr_index = annotations['composition'].isna().idxmax()
else:
    curr_index = 0
first_image_to_display = str(file_pd.file_name[curr_index])

def get_current_index(img_file_name):
    """
    Retrieve the index of the specified image file name in the DataFrame.
    If the image is the last one or exceeds the length of the DataFrame, return -1.

    Parameters:
    - img_file_name (str): The name of the image file to search for.

    Returns:
    - int: The index of the image file name or -1 if it's the last one or exceeds the length.
    """
    curr_index_no = file_pd.loc[file_pd['file_name'] == img_file_name].index
    if curr_index_no[0] > (len(file_pd) - 2):
        c_index = -1  # reset to -1 if at the last image
    else:
        c_index = curr_index_no[0]
    return c_index

def calculate_TIRADS(composition, echogenicity, nod_shape, margin, echogenic_foci):
    # Initialize TI-RADS points
    tirads_points = 0
    
    # Define scoring criteria for each parameter
    composition_scores = {
        "Cystic or completely cystic": 0,
        "Spongiform": 0,
        "Mixed cystic and solid": 1,
        "Solid or completely solid": 2
    }
    
    echogenicity_scores = {
        "Anechoic": 0,
        "Hyperechoic or isoechoic": 1,
        "Hypoechoic": 2,
        "Very hypoechoic": 3
    }
    
    shape_scores = {
        "Wider than tall": 0,
        "Taller than wide": 3
    }
    
    margin_scores = {
        "Smooth": 0,
        "Ill defined": 0,
        "Lobulated or irregular": 2,
        "Extra thyroidal extension": 3
    }
    
    echogenic_foci_scores = {
        "None or large comet-tail artifacts": 0,
        "Macrocalcifications": 1,
        "Peripheral (rim) calcifications": 2,
        "Punctate echogenic foci": 3
    }
    
    # Calculate TI-RADS points based on the scoring criteria
    tirads_points += composition_scores.get(composition, 0)
    tirads_points += echogenicity_scores.get(echogenicity, 0)
    tirads_points += shape_scores.get(nod_shape, 0)
    tirads_points += margin_scores.get(margin, 0)
    
    # If there are multiple echogenic foci, sum their scores
    for foci in echogenic_foci:
        tirads_points += echogenic_foci_scores.get(foci, 0)
    
    # Determine TI-RADS level based on total points
    if tirads_points < 1:
        tirads_level = "TI-RADS 1"
    elif tirads_points < 3:
        tirads_level = "TI-RADS 2"
    elif tirads_points < 4:
        tirads_level = "TI-RADS 3"
    elif tirads_points < 7:
        tirads_level = "TI-RADS 4"
    else:
        tirads_level = "TI-RADS 5"
    
    return tirads_points, tirads_level

def save_current_annot(curr_index,composition, echogenicity,
                       shape,margin,echogenic_foci,tirads_points,tirads_score, fl_name):
    
    annotations.at[curr_index, 'pd_filename'] = fl_name
    annotations.at[curr_index, 'composition'] = composition
    annotations.at[curr_index, 'echogenicity'] = echogenicity
    annotations.at[curr_index, 'nod_shape'] = shape
    annotations.at[curr_index, 'margin'] = margin
    annotations.at[curr_index, 'echogenic_foci'] = echogenic_foci
    annotations.at[curr_index, 'tirads_points'] = tirads_points
    annotations.at[curr_index, 'tirads_score'] = tirads_score
    annotations.to_csv(annotation_file , index=False)

def forward(composition, echogenicity,shape,margin,echogenic_foci,
            tirads_points,tirads_score, fl_name):
    
    global curr_index
    global annotations
    global file_pd
    
    curr_index = get_current_index(fl_name)
    
    if curr_index == -1:
        index_tosave=len(file_pd)-1
        save_current_annot(index_tosave,composition, echogenicity,shape,margin,
                           echogenic_foci,tirads_points,tirads_score,fl_name)
        gr.Warning('This was the last image in the database. You have annotated all images.')
        time.sleep(2)
        #sys.exit(0)
    else:
        index_tosave = curr_index
        save_current_annot(index_tosave,composition, echogenicity,shape,margin,
                           echogenic_foci,tirads_points,tirads_score, fl_name)

    # Update UI with existing annotations if available
    if curr_index == -1:
        curr_index=len(file_pd)-1
    else:
        curr_index += 1
        
    filename_4_nxt_image = file_pd.file_name[curr_index]
 
    if str(annotations.composition[curr_index]) == 'nan':
        file_name= filename_4_nxt_image
        composition = "Solid or completely solid"
        echogenicity = "Hypoechoic"
        shape = "Wider than tall"
        margin = "Ill defined"
        echogenic_foci = "None or large comet-tail artifacts"
        tirads_points = 4
        tirads_score = "TI-RADS 4"
    else:
        composition = annotations.composition[curr_index]
        echogenicity = annotations.echogenicity[curr_index]
        shape = annotations.nod_shape[curr_index]
        margin = annotations.margin[curr_index]
        echogenic_foci = annotations.echogenic_foci[curr_index]
        tirads_points = annotations.tirads_points[curr_index]
        tirads_score = annotations.tirads_score[curr_index]
        
    if annotations['composition'].isna().any():
        progress_position = annotations['composition'].isna().idxmax()
    else:
        progress_position = len(annotations)

    progress = str(progress_position) + " out of " + str(len(file_pd)) + " done."
    
    return [Image.open(filename_4_nxt_image),progress, composition, 
            echogenicity,shape,margin,echogenic_foci, 
            filename_4_nxt_image, tirads_points, tirads_score]

def backward(composition, echogenicity,shape,margin,echogenic_foci,
            tirads_points,tirads_score, fl_name):
    
    global curr_index
    global annotations
    global file_pd
    
    curr_index = get_current_index(fl_name)
    
    if curr_index == 0:
        index_tosave=0
        save_current_annot(index_tosave,composition, echogenicity,shape,margin,
                           echogenic_foci,tirads_points,tirads_score,fl_name)
        gr.Warning('This was the first image in the database. Cannot move backwards. Reloading first image')
        #time.sleep(2)
        #sys.exit(0)
    elif curr_index == -1:
        index_tosave=len(file_pd)-1
        save_current_annot(index_tosave,composition, echogenicity,shape,margin,
                           echogenic_foci,tirads_points,tirads_score,fl_name)        
    else:
        index_tosave = curr_index
        save_current_annot(index_tosave,composition, echogenicity,shape,margin,
                           echogenic_foci,tirads_points,tirads_score, fl_name)

    # Update UI with existing annotations if available
    if curr_index == 0:
        curr_index = 0
    elif curr_index == -1:
        curr_index= len(file_pd)-2
    else:
        curr_index -= 1
        
    filename_4_nxt_image = file_pd.file_name[curr_index]
 
    if str(annotations.composition[curr_index]) == 'nan':
        file_name= filename_4_nxt_image
        composition = "Solid or completely solid"
        echogenicity = "Hypoechoic"
        shape = "Wider than tall"
        margin = "Ill defined"
        echogenic_foci = "None or large comet-tail artifacts"
        tirads_points = 4
        tirads_score = "TI-RADS 4"
    else:
        composition = annotations.composition[curr_index]
        echogenicity = annotations.echogenicity[curr_index]
        shape = annotations.nod_shape[curr_index]
        margin = annotations.margin[curr_index]
        echogenic_foci = annotations.echogenic_foci[curr_index]
        tirads_points = annotations.tirads_points[curr_index]
        tirads_score = annotations.tirads_score[curr_index]
    
    if annotations['composition'].isna().any():
        progress_position = annotations['composition'].isna().idxmax()
    else:
        progress_position = len(annotations)

    progress = str(progress_position) + " out of " + str(len(file_pd)) + " done."

    
    return [Image.open(filename_4_nxt_image),progress, composition, 
            echogenicity,shape,margin,echogenic_foci, 
            filename_4_nxt_image, tirads_points, tirads_score]
thyroid_tagger = gr.Blocks()

with thyroid_tagger:
    gr.Markdown(
        """
    # TI-RADS annotation generator
    """
    )
    with gr.Row():
        with gr.Column(scale=3):
            thyroid_image = gr.Image(value=first_image_to_display)
            progress= gr.Text(label="Progress")
        with gr.Column(scale=2):
            composition = gr.Dropdown(label="Composition", value ="Solid or completely solid",interactive = True,
                                      choices=["Solid or completely solid","Cystic or completely cystic", "Spongiform", "Mixed cystic and solid"])
            echogenicity =gr.Dropdown(label="Echogenicity",value ="Hypoechoic",interactive = True,
                                      choices=["Hypoechoic","Anechoic", "Hyperechoic or isoechoic", "Very hypoechoic"])
            nod_shape = gr.Dropdown(label="Shape",value ="Wider than tall",interactive = True,
                                choices=["Wider than tall", "Taller than wide"])
            margin = gr.Dropdown(label="Margin",value ="Ill defined",interactive = True,
                                 choices=["Ill defined","Smooth", "Lobulated or irregular", "Extra thyroidal extension"])
            echogenic_foci=gr.Dropdown(label="Echogenic foci",multiselect = True, value ="None or large comet-tail artifacts",interactive = True,
                                       choices= ["None or large comet-tail artifacts", "Macrocalcifications", 
                                                 "Peripheral (rim) calcifications","Punctate echogenic foci"])
            total_points = gr.Textbox(label="Total Points", value =4)
            tirads_level=gr.Textbox(label= "TI-RADS level", value ="TI-RADS 4")
            
            fwd_button = gr.Button(value="Next")
            bkd_button = gr.Button(value="Previous")
            
            img_file_name = gr.Textbox(label = "File name", value = first_image_to_display)
                
            
            input = [composition, echogenicity,nod_shape,margin,echogenic_foci,
                     total_points,tirads_level,img_file_name]
            
            output =[thyroid_image,progress, composition, echogenicity,
                     nod_shape,margin,echogenic_foci,img_file_name, total_points, tirads_level]

            ti_rads_input = [composition, echogenicity, nod_shape, margin, echogenic_foci]
            ti_rads_output = [total_points, tirads_level]
            
            composition.change(fn = calculate_TIRADS, inputs =ti_rads_input, outputs = ti_rads_output)
            echogenicity.change(fn = calculate_TIRADS, inputs = ti_rads_input, outputs = ti_rads_output)
            nod_shape.change(fn = calculate_TIRADS, inputs = ti_rads_input, outputs = ti_rads_output)
            margin.change(fn = calculate_TIRADS, inputs = ti_rads_input, outputs = ti_rads_output)
            echogenic_foci.change(fn = calculate_TIRADS, inputs = ti_rads_input, outputs = ti_rads_output)
            
            
            fwd_button.click(fn=forward, inputs=input, outputs=output)
            bkd_button.click(fn=backward, inputs=input, outputs=output)
            
thyroid_tagger.queue()

thyroid_tagger.launch(show_error=True)
