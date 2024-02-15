
# SecureVision Project

**Student ID:** 210296620

**Project Name:** SecureVision

***

## System Information 

The project was developed with following technologies.

- Operating System: MacOS Ventura 13.6.4 (c)

- Source-code Editor: Visual Studio Code

- Python Version: Python 3.10.9

- Flask version: Flask 2.3.0

- Database: SQLite3

- API: Gmail API v1 and Google Drive API

*** 

## Browser Compatibility 

If you are using the Chrome browser, you must manually enable microphone and video in Chrome Settings. This is due to the localhost not being a secure host. Chrome requires HTTPS. To enable camera and microphone, navigate to the  [Chrome settings page](chrome://settings/content/siteDetails?site=http%3A%2F%2F127.0.0.1%3A5003).

#### Note: The project was only tested with Chrome and Safari.

***

## Project Setup and Installation using Terminal:

1. Unzip the project folder

2. Navigate to the project directory
	    
        cd [ADD YOUR DIRECTORY HERE]

3. Create a virtual environment (Python 3.10.9)
	
        /usr/local/bin/python3.10 -m venv venv

4. Activate the virtual environment

        source venv/bin/activate

5. Install the dependencies
	
        pip install --use-pep517 -r requirements.txt

6. Verifying Installed Packages
	
        pip list

*Note that if "object-detection==0.1" appears in the requirements.txt, you will be unable to install dependencies. This could happen if you installed dependencies, added more, and then ran pip freeze > requirements.txt. This will include "object-detection==0.1", which will prevent you from installing dependencies from that file again. If this happens, manually remove "object-detection==0.1" from requirements.txt and try again.*


7. TensorFlow Model Setup

    *The TensorFlow model must run at all times. You must run TensorFlow before starting development server.*

Navigate to the TensorFlow models research directory:
	
    cd models/research

Compile Protocol Buffers:
	
    protoc object_detection/protos/*.proto --python_out=.

Set the PYTHONPATH:

	export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim

Verify Object Detection API Setup:
	
    python object_detection/builders/model_builder_tf2_test.py

Remember to navigate back to the correct folder (twice):
	    
    cd ..

8. In order to initialize Gmail API tokens, please visit the [Google PlayGround](https://developers.google.com/oauthplayground/)

- Scroll down to: ***Gmail API v1***. In the dropdown select: 

		https://www.googleapis.com/auth/gmail.send

- Click ***Authorize APIs***. You will be redirected to ***Google OAuth 2.0 Playground wants to access your Google Account***, click allow. Please use login instructions provided in the report to authenticate.

- Click on ***Step 2 Exchange authorization code for tokens*** and in the dropdown click on ***Exchange authorization code for tokens***. 


In terminal enter:

	    flask init-gmail-tokens

*You will be asked to enter access and refresh tokens, and expiration of token.*


9. Start the development server:
	
        flask run --host=0.0.0.0 --port=5003

10. Visit localhost to view the project:

	    http://127.0.0.1:5003



11. User Registration: 

    You will first be directed to Setup Page that will describe how to use the project. Then you will need to click the complete button to be redirected to the Registration page. You will be asked to enter First Name, Last Name, Email and Password, then you will be redirected to login page where you will need to enter email and password.

12. User Login:

    You may use pre-registered User login. Please see report.

***

## Audio Troubleshooting

If you are unable to run the project due to an audio device indexing issue. Please check your device index with one of the commands below before manually changing it.

on Mac
    
    system_profiler SPAudioDataType

on Windows

    Get-WmiObject Win32_SoundDevice

***

## Admin Login

Flask Admin Login

    email: SEE REPORT
    password: SEE REPORT

In case of login issues, please create a new superuser and follow terminal instructions.

Create superuser:

	flask create-superuser


Make an existing user an admin:


	flask make-admin-user

***

## Running Scripts

Navigate to the scripts directory:
	
    cd scripts

Init database:

	python init_db.py

Generate secret key:

	python generate_secret_key.py

***

## Metadata Verification

To verify metada encoding, please use: 

	ffprobe -i '[FULL PATH TO MP4 FILE NAME HERE]'

***

## Running Unit Tests

To run all tests:

    pytest tests

To run individual tests:

	pytest tests/test_video_camera.py
	pytest tests/test_email.py
	pytest tests/test_lukas_kanade_orb_method.py
	pytest tests/test_mckenna_method.py
	pytest tests/test_object_detection.py
	pytest tests/test_three_frame_difference.py
	pytest tests/test_views.py

***

## Database Commands

To initialize, migrate and upgrade the database with Flask:

	flask db init
	flask db migrate -m "MESSAGE HERE"
	flask db upgrade


***
## CLI Commands

Please make sure you are in the root directory and virtual environment is activated.

Initialize Database (CLI):

	flask init-database


Initialize Default Roles:

	flask init-default-roles


Initialize Default Data for Position and MotionSize tables:

	flask init-default-position-size

Initialize Object Types:

	flask init-default-object-types

***

## Cashe

If you need to clear cashe, please use these commands.


	clear cashe


	find . -name "__pycache__" -exec rm -r {} +



***

##### readme file was created with the help of [readme.so](https://readme.so/editor)

##### Documentation and research materials were used in the development of the code, including but not limited to academic papers, articles, blog posts, and YouTube video tutorials. Please see referenced links. Some parts were copied and closely adopted, some parts were copied as-is, and others written on general understanding of documentation and research.

***