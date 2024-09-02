## Performance Analysis in the Squat

## Description.

Prototype application based on computer vision to track the trajectory of the barbell while performing weight exercises. This project focuses on squat movement analysis using computer vision techniques and the OpenCV library. The main objective is to extract and quantify key parameters, such as barbell trajectory, range of movement (ROM), and execution speed. The system is designed to be used in uncontrolled environments and offers a non-invasive method of assessing and improving performance during training, through the use of a marker.

## Key Features.

- **Video Capture**: Records movement in an uncontrolled environment.
- **Bar Tracking**: Tracks the trajectory of the barbell in space.
- **Calculation of Training Parameters**: Determines the ROM and speed of squat execution.

## Installation.

1. Clone repository:
   ```bash
   git clone https://github.com/tuo-username/analisi-squat.git
   ```
2. Access the project directory:
   ```bash
   cd analysis-squat
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place the capture device on a tripod, making sure the marker is visible.
2. Start video recording while performing the squat.
3. Use the script to analyze the video:
   ```bash
   python analyze_squat.py --video path_to_video
   ```
4. The results, including the barbell trajectory and training parameters, will be displayed on the screen.

## Requirements.

- Python 3.7+
- OpenCV
- Numpy

## Credits.

Project developed by Gian Marco Lelli as part of a term paper on Computer Vision. Freshman ID: 305298.

Translated with DeepL.com (free version)
