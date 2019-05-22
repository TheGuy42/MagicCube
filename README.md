# Magic Cube
this project is a wireless cube made with raspberry pi zero w and a mpu-6050 sensor.
the cube connects to the computer, and an app on the computer controls it according to the movement of each of the cube faces.

The project was written and tested with **python 3**. make sure to use it on the raspberry pi and pc.

You can see pictures for reference on [imgur](https://imgur.com/a/eOWr2kO).

## preparing pc
1. Make sure you have python 3 installed
2. Inside the `MagicCube.py` file you will find the class `AppDefaultSettings` from there you will need to set the `pi_hostname` according to what you set. If you set a static ip you can also change it to the ip address of the pi(as a string). you can also change the threshold for each function, change functions and add new ones.
3. in the end of the `MagicCube.py` file you will find commented code, you can uncomment it and comment the code above it to run it in GUI mode but it still has bugs.

## preparing the raspberry pi
Note that the project uses the raspberry pi zero w because of it's form factor but other ones should work as well. (RPi 3b+ also tested and worked).
Parts list:
1) Raspberry pi zero w
2) 2X 18650 batteries
3) individual WS2812B leds, can be found on [AliExpress](https://www.aliexpress.com/item/10-1000pcs-4-Pin-WS2812B-WS2812-LED-Chip-Heatsink-5V-5050-RGB-WS2811-IC-Built-in/32634454437.html?spm=a2g0s.9042311.0.0.45aa4c4dOVI5Jz)
4) TP4056 charger
5) A switch(see picture for reference)
6) 8X about 1.5x0.5mm magnets

Steps for configuring the pi:
1. Install Debian OS from the raspberry pi website.
2. Connect to your wifi network(same one as pc).
Note: better if you set your ip to be static. if you do so you will be able to connect to it via ip rather then hostname
3. Change your pi's Hostname to "MagicCube".
4. Enable i2c, vnc and ssh. vnc and ssh are for remote control, one is sufficient.
5. change i2c bus speed too 400000.
   you can see how here: [change i2c speed on raspi](https://www.raspberrypi-spy.co.uk/2018/02/change-raspberry-pi-i2c-bus-speed/)
6. Install the adafruit neopixel library  `sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel`
7. Install samba `sudo apt-get -y install samba`
   samba is needed in order to find the pi via it's hostname, witch let's us have dhcp insted of static ip, if you are using static ip you can skip this step 
8. change the default password of the pi
9. change the boot option to boot to CLI instead of Desktop
10. copy the MagicCube files to the pi
11.  connect the mpu-6050 to the pi(make sure vcc is connected to to 3.3v)
12. connect the neopixels(also to 3.3v), the data pin goes to BCM18. according to this [pinout](https://pinout.xyz/)

After the raspberry pi is working you can connect the battery, switch and charger
the pi connects to the switch and the battery and led's directly to the charger out pins.

In the config file(inside the MagicCube folder) you will be able to change settings such as led preset colors, thresholds and add new colors. also note you **will need to change** the led's order in the presets as it will change if you solder/glue them differently than i did.

## The physical cube
The cube itself is 80x80x80 mm with two 35.355mm Isosceles triangles on opposing side in order to rest the cube when not in use.
You can find here also 3d printable .stl files. The 3rd iteration was printed using the original prusa mk3s
The first two iterations were made with 3mm plywood.

