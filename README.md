Kpy-recorder
============

This script is initially designed to monitor user actions on industrial machines in order 
to report anomalies or improve the production system. 
It allows to record the screen as soon as a user uses the mouse or the keyboard and to stop
the recording after a certain time.

Usage
-----

It run in commands line with following parameters:

    -o /any/path/videos # (required: true) a writable directory where save the videos
    -k 50 # (required: false, default: 100) a int which define how many video to keep, remove the oldest
    -i 30 # (required: false, default: 30) a int which defined how long inactivity time to stop a record
    
    
    ex:
    kpy_recorder -o /tmp/user/screen
    kpy_recorder -o /tmp/user/screen -i 90
    kpy_recorder -o /tmp/user/screen -i 60 -k 500
    kpy_recorder -o /tmp/user/screen -k 20


Binaries
--------

You can download some builds here: https://github.com/KernelPan1k/kpy-recorder/tree/master/dist


User from source
----------------

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python src/kpy_recorder.py -o /path/folder/videos
