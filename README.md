# adb-photo-remote
Simple python web server to use a computer to take photos with ADB over USB

## Installation

Create a virtual environment and install requirements.

```sh
python3 -m venv venv
. ./venv/bin/activate
python -m pip install -r requirements.txt
```

Also ensure the adb commandline tool is intalled for your phone.

## Use

1. Plug in phone with USB.
2. Turn on camera.
3. Position camera for the photo.
4. Run the script `./run.sh`
5. Open the web page, localhost:5050
6. Click anywhere to take a photo with your camera and the result should populate locally.

## Notes

It's pretty rough and there are surely a lot of bugs. Use at your own risk.
