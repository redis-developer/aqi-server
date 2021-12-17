# The Redis Pi Cube!
## How to install Redis on a Raspberry Pi

This installation guide is based on the instructions found [here](https://habilisbest.com/install-redis-on-your-raspberrypi) with some slight updates to suit the needs of a newer Raspbian OS version and availablity of the Redis instance to outside hosts.

This tutorial has been tested and verified to work on the Raspberry Pi units listed below in the prerequisites section.  If you have any questions, comments, or improvements, please don't hesistate to let us know!

## Goal
The goal of the Redis Pi Cube is to create an automatic instance of Redis on a Raspberry Pi unit open to the local network for testing, developing, and learning.  There are two phases of the installation: Redis installation and wireless AP integration.

Redis installation:
This will install the most recent stable release of Redis and set it as a service to automatically run when the Raspberry Pi unit is powered on.  Protected-mode is currently set to no, so outside hosts can access the Redis instance. Auth and ACL can be implemented if desired.  The user can connect the raspberry pi to a monitor, keyboard, and mouse and connect to a wireless access point or connect to an ethernet connection via USB.

Wireless AP integration:
This phase will create a default SSID to connect to the Redis Pi Cube.  After initial connection a hosted page can be accessed and a connection to a local wireless network can be established. This is to skip the requirement of connecting to the Redis Pi Cube with peripherals to establish the local wireless connection.

## Prerequisites

### Raspberry Pi Units
The Redis Pi Cube has been proven to work on the following units:
- Raspberry Pi Zero W 2
- Raspberry Pi Zero W
- Raspberry Pi 4 Model B
- Raspberry Pi 3 Model B

### Raspberrry Pi OS
The Raspberry Pi currently runs the Rasbian GNU/Linux 11 (bullseye) image found [here](https://www.raspberrypi.com/news/raspberry-pi-os-debian-bullseye/).  SSH has been enabled and the default password has been updated. Enabling SSH on the Pi unit can be found [here](https://linuxize.com/post/how-to-enable-ssh-on-raspberry-pi/). You will need to connect to the internet to install the necessary software.



## Installing Redis
Installing Redis on the Raspberry Pi may be done either from a terminal within Raspbian or connected via SSH from another computer.

### Acquire

In the terminal, go to the default home directory:

```bash
$ cd Downloads
```

Download the latest stable release of Redis from Redis.io as a tar file:

```bash
$ wget http://download.redis.io/redis-stable.tar.gz
```

The version used in creating this tutorial is `6.2.6`

Unpack the archived files:
```bash
$ tar xzf redis-6.2.6.tar.gz
```

### Build

Enter the unpacked Redis folder and build the source. The `make test` command, while important, is optional as it may require specific tools and an extended amount of time to complete.

```bash
$ cd redis-6.2.6
$ make
$ cd src
$ sudo make install PREFIX=/usr
```

### Cleanup
```bash
$ cd ~/Downloads
```
Copy the compiled Redis configuration file to the new folder:
```bash
$ sudo mv redis-stable /etc/redis
```

Remove the tar file:
```bash
$ rm -rf redis-stable.tar.gz
```

### Setting Redis as an automatic service

Now that Redis has been compiled on the Raspberry Pi, we will perform some housecleaning. We will update our compiled Redis configuration file `redis.conf` for local network access. We will also add a service to automatically start Redis when the Raspberry Pi unit is turned on.

### Prep 

$ sudo nano /etc/redis/redis.conf

Update the `redis.conf` file to reflect the following:

```bash
# bind 127.0.0.1 ~::1 
protected-mode no
maxmemory 250M
maxmemory-policy allkeys-lru
TODO: Anything else helpful
```

Create a systemd service file to enable the OS to start Redis when powering on. Start with a configuration file that will hold any arguments to be passed to the `redis-server` command.

```bash
$ sudo touch /etc/redis/redis-service.conf
```

redis-service.conf:
```bash
ARG1=/etc/redis/redis.conf
```

Create a service file within the systemd etc folder to start Redis at boot up:
```bash
$ sudo touch /etc/systemd/system/redis-server.service
$ sudo nano /etc/systemd/system/redis-server.service
```

`redis-server.service`: 
```bash
[Unit]
Description=Redis 6.2.6
After=network.target

[Service]
WorkingDirectory=/etc/redis/
EnvironmentFile=/etc/redis/redis-service.conf
ExecStart=/usr/local/bin/redis-server $ARG1
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
```

Enable the service file, start the `redis-server.service` unit, then test Redis functionality.
```bash
$ sudo systemctl enable redis-server.service
$ sudo systemctl start redis-server.service
$ redis-cli PING
"PONG"
```
