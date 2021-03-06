# Collection LEDs
This project is meant to control an individually adressable led strip directly connected to the GPIO pins of a Raspberry Pi. It is specifically build for highlighting a collection on a series of shelves for example. This is most apearant in the picker functionality which can be used to randomly pick a single led in a section of leds preseded by a chosing animation.  

Personally, I use this to randomly select the next whiskey I drink from my collection, however you can also use it to let faith deside which My Little Pony next to play with.

**NOTE:** When you want to run control the LEDs using Google Home voice commands or simply want an easy setup use the docker-compose project to setup this project:  
https://github.com/sakoarts/collection_leds_docker

## Functionality
The project has the following base Functionality.
* Interation with a LED strip via de GPIO headers of a Raspberry Pi
* Several animations to illuminate and highlight your collection
* A sequience that randomly picks a LED (item) of your collection
* A HTTP API that allows you to activate the animations, picker or directly control the LEDs
* A very basic web page that allows you to control some of the above
* Some utilities that support the execution and termination of the animations

## Settings
In config/settings.json the basic settings for the server can be found that should be adapted to your specific setup. As of now the following things need to be set:
* The number of LEDs on your LED strip
* Which LEDs to exclude from the picking process
* Which GPIO header you connected the data line of the strip to
* The order of the color channels (depend on your strip type)
* The segments of your strip. (I have three shelves with different classes of whiskeys)

## Installation and Running
Firstly the project has to be ran as root, otherwide the GPIO pins will not be availeble to the project. I highly recommend using Docker to run the project, but you can also directly run the project with python.
### Docker installation
You can simply run this project using the supplied Dockerfile in the root of the project as instructed below. However I reccomend using a docker compose with supporting services. 
#### Docker Compose
For running this project in a docker compose environment I provided a seperate project that loads this project as a submodule. Besides the obious advantages of running the project in a docker environment, this compose project adds additnal functionality to the project like the option for Google Home intergration resulting in voice control for the Colleciton LEDs. More information and installation instructions can be found in de README.md of said project:  
https://github.com/sakoarts/collection_leds_docker
#### Docker
Make sure you have docker installed, then:
 ```
git clone "https://github.com/sakoarts/collection_leds"
cd collection_leds
docker build .
```

### Running it with Python
NOTE: This is almost fully written out of my head and I did not test it, if it doesn't work, let me know. 
 I you run it as simple python project you have to install python and the project requirements. After which you can either run it in something like screen but I recommend adding it to startup using systemd for example(newer versions of Ubuntu and Debian). I'll give an example of installing and running it in Rasbian Buster:
 ```
sudo apt update && sudo apt install python3 python3-dev
git clone "https://github.com/sakoarts/collection_leds"
cd collection_leds
python3 -m pip install --user virtualenv
python3 -m venv collectionvenv
source collectionvenv/bin/activate
python3 -m pip install -r requirements.txt

# Optionally run the application
python3 app.py
 ```
Additionally you would want to add it as a service thar runs on startup.
```
sudo nano /etc/systemd/system/collectionled.service

# Paste everything from the block below in nano after replacing at least USER_NAME to your username or change the paths all together.

# Press Ctrl-X followed by Enter to save, then execute

sudo systemctl start collectionled.service
sudo systemctl enable collectionled.service
```
```
[Unit]
Description=Flask Server for Collection LED strip
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/home/USER_NAME/led_server
Environment="PATH=/home/USER_NAME/led_server/collectionenv/bin"
ExecStart=/home/USER_NAME/led_server/collectionvenv/bin/python3 /home/USER_NAME/led_server/app.py
# ExecStart=/home/USER_NAME/led_server/collectionvenv/bin/gunicorn --workers 1  --bind unix:ledserver.sock -m 007 app:app --log-level=warning --error-logfile=/home/USER_NAME/led_server/logs/gunicorn.log
Restart=always

[Install]
WantedBy=multi-user.target
```

## Controlling
You can control the LED server using any apllication you like via the HTTP API. Although in some cases you will need to expose the API externally on what point I strongly recommend adding more security. The simplest way of controlling it after installing and running the project is from the browser of a device in the same netwerk. For this you need to find the IP of your raspberry pi. As an example, we use 192.168.1.33 

The simple web page can be found on: http://192.168.1.33:5000/collection

You can also directly control the strip via the browser by activating specific APIs and passing the arguments as GET parameters. Here are some examples:
* http://192.168.1.33:5000/collection/collection-pixel?r=28&g=155&b=155&p=5
* http://192.168.1.33:5000/collection/chase?r=28&g=155&b=155&speed=0.001&sled=0&eled=140
* http://192.168.1.33:5000/collection/rainbow
* http://192.168.1.33:5000/collection/fire?sled=0&eled=140&factor=0.75
* http://192.168.1.33:5000/collection/all-off
* http://192.168.1.33:5000/collection/leds?r=28&g=155&b=155&sled=0&eled=140&color=goldenrod

## Recommendations
* Personlly I like to control the LEDs using Google Home voice commands. This can be done in several ways amongst which Trello or building a google action project, however I recommend using NodeRed in combination with NORA. When installing this on the same raspberry (or anywhere else in your local netwerk) you will not have to expose the API. Installation instructions can be found below here: https://flows.nodered.org/node/node-red-contrib-nora
