# TIRADS_Annotator
An open-source tool to generate TI-RADS description for thyroid nodules


## Overview
This web-based application is designed for radiologists and researchers involved in thyroid nodule analysis. It enables users to generate annotations for thyroid nodules using TI-RADS descriptors and could provides automated TI-RADS reports using AI models. This tool aims to facilitate studies on the agreement between radiologist assessments and AI-generated evaluations.

## Features
- **Annotation Using TI-RADS Descriptors:** Users can manually annotate thyroid nodules based on TI-RADS descriptors. This toll will automatically calculate TI-RADS score. 
- **Automated TI-RADS Reporting:** Leverage AI models to generate TI-RADS reports automatically.
- **Comparison Studies:** Conduct studies to compare agreement rates between radiologists and AI assessments.

![TI-RADS annotator GUI](https://github.com/johnyquest7/TIRADS_Annotator/assets/22123236/1a494928-f008-467e-99e9-f584b5465a24)
## Summary of the tool

- **Purpose:** It’s designed to load or create annotations for thyroid nodule images, calculate TI-RADS scores, and navigate through images for annotation.
- **Requirements:** The app requires Python libraries - gradio, os, PIL, pandas, time, and sys.
- **Functionality:** It includes functions to handle file operations, retrieve and sort file lists, load/create annotation data, calculate TI-RADS, and save annotations.
- **Inputs:** The inputs are image files of thyroid nodules, stored in a specified directory, and user annotations for various attributes of the nodules.
- **Outputs:** The outputs are an updated CSV file with annotations and TI-RADS scores, and a user interface for navigating and annotating images.
  
The file uses global variables to manage the state of annotations and includes error handling for edge cases like the last image in the database. It also defines scoring criteria for calculating TI-RADS based on nodule characteristics.

## Usage
Before using the app, make sure the  "image_file_directory" variable point to your folder with thyroid ultrasound images.

## Contributions
Contributions to this project are welcome. Please reach out for more details on how to contribute or create a pull request.

## Reporting Issues
Please report any bugs or issues but creeating a new issue in the repository page. 

## Disclaimer
This application is intended for research and educational purposes only. It should be used with caution and at your own risk. The tools and reports generated by this application are not substitutes for professional medical advice or diagnostic services.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.
