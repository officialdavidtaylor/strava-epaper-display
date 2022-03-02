# Project Overview

The goal of this project is to flex on my co-workers with an auto-updating e-paper display that always shows my latest rides on Strava.

# Project Notes

For the current release, all credentials and access tokens must be hard-coded into the 'credentials.py' file.

Depending on the complexity of the implementation, the current plan is to follow the below control flow:

1. Boot Raspberry Pi
1. Clear e-paper screen
1. Search for known WiFi network (reflect status on e-paper screen)
 1. If no known WiFi is found, launch local website and start WiFi in AP node
  - display available SSIDs and allow the user to enter credentials via a website interface
1. Run application

# BOM

- Raspberry Pi Zero W 1.1
- WaveShare e-Paper 4.2" 300x400px
