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

1. In the terminal, go to the default home directory:

```bash
cd ~
```

2. Download the latest stable release of Redis from Redis.io as a tar file:

```bash
wget http://download.redis.io/redis-stable.tar.gz
```

The version used in creating this tutorial is `6.2.6`

3. Unpack the archived files:

```bash
tar xzf redis-stable.tar.gz
```

4. Enter the unpacked Redis folder and build the source. The `make test` command, while important, is optional as it may require specific tools and an extended amount of time to complete.

```bash
cd redis-stable
sudo make
make test
sudo make install PREFIX=/usr
```

### Setting Redis as an automatic service

Now that Redis has been compiled on the Raspberry Pi, we will perform some housecleaning to allow a modified user `redis` to automatically run our `redis-server` instance. We will also move and update our compiled Redis configuration file `redis.conf` for local network access. Lastly we will add a service to automatically start Redis when the Raspberry Pi unit is turned on.

1. Create a directory where the `redis.conf` will be stored:

```bash 
sudo mkdir /etc/redis
```

2. Copy the compiled Redis configuration file to the new folder:

```bash
sudo cp redis.conf /etc/redis/
```

3. Remove the `.tar` file and original Redis folder:

```bash
cd ..
sudo rm -Rf redis*
```

4. Create a new user `redis` without a home directory or the ability to login as a regular user. This user will run Redis upon startup:

```bash
sudo adduser --system --group --disabled-login redis --no-create-home --shel /usr/sbin/nologin --quiet
```

5. Verify within the shadow file that the user `redis` has been created:

```bash
cat /etc/passwd | grep redis
```

6. Edit the `redis.conf` configuration file recently copied to `/etc/redis/` for local access:

```bash
sudo nano /etc/redis/redis.conf
```

Use the CTRL+W search function to find and update the following directives. They should have the following attributes after the file is saved:

```bash
protected-mode no
daemonize yes
stop-writes-on-bgsave-error no
rdbcompression yes
maxmemory 250M
maxmemory-policy allkeys-lru
```

To save the file, press CTRL+O. Verify the name of the file by pressing ENTER. Exit out of nano by pressing CTRL+X.

7. We will now create a directory containing a script to run Redis upon startup:

```bash
sudo mkdir -p /var/run/redis
```

8. Set permissions on the user `redis` to be the sole owner of this directory:

```bash
sudo chown -R redis /var/run/redis
```

9. Create a new script by starting up nano in the following location:

```bash
sudo nano /etc/init.d/redis-server
```

Copy the following into the nano window:

```bash
#! /bin/sh
### BEGIN INIT INFO
# Provides: redis-server
# Required-Start: $syslog $remote_fs
# Required-Stop: $syslog $remote_fs
# Should-Start: $local_fs
# Should-Stop: $local_fs
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: redis-server - Persistent key-value db
# Description: redis-server - Persistent key-value db
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/bin/redis-server
DAEMON_ARGS=/etc/redis/redis.conf
NAME=redis-server
DESC=redis-server

RUNDIR=/var/run/redis
PIDFILE=$RUNDIR/redis-server.pid

test -x $DAEMON || exit 0

if [ -r /etc/default/$NAME ]
then
. /etc/default/$NAME
fi

. /lib/lsb/init-functions

set -e

case "$1" in
  start)
echo -n "Starting $DESC: "
mkdir -p $RUNDIR
touch $PIDFILE
chown redis:redis $RUNDIR $PIDFILE
chmod 755 $RUNDIR

if [ -n "$ULIMIT" ]
then
ulimit -n $ULIMIT
fi

if start-stop-daemon --start --quiet --umask 007 --pidfile $PIDFILE --chuid redis:redis --exec $DAEMON -- $DAEMON_ARGS
then
echo "$NAME."
else
echo "failed"
fi
;;
  stop)
echo -n "Stopping $DESC: "
if start-stop-daemon --stop --retry forever/TERM/1 --quiet --oknodo --pidfile $PIDFILE --exec $DAEMON
then
echo "$NAME."
else
echo "failed"
fi
rm -f $PIDFILE
sleep 1
;;

  restart|force-reload)
${0} stop
${0} start
;;

  status)
status_of_proc -p ${PIDFILE} ${DAEMON} ${NAME}
;;

  *)
echo "Usage: /etc/init.d/$NAME {start|stop|restart|force-reload|status}" >&2
exit 1
;;
esac

exit 0
```

10. Set this script to be executable:

```bash
sudo chmod +x /etc/init.d/redis-server
```

11. Add the script as a command

```bash
sudo update-rc.d redis-server defaults
```

12. Verify that the command can be called by entering the following:

```bash
sudo service redis-server restart
```

13. Verify that the redis server is running by checking the active version:

```bash
redis-server -v
```

14. Ensure that Redis is listening at `127.0.0.1` and on port `6379`:
```bash
netstat -antp
```

15. Lastly, check that Redis is running as the `redis` user:
```bash
ps aux | grep redis
```

16. Restart the Raspberry Pi unit. Enter a terminal again and check connectivity to Redis by starting the cli:

```bash
# On the Raspberry Pi Unit:
redis-cli PING
```

```bash
# If connected to Raspberry Pi via ssh:
redis-cli -h <RASPBERRY_PI_IP_ADDRESS> -P 6379 PING
```

You should receive a `PONG` response






## Wireless AP integration:


TODO: Instructions in integrating RaspAP
