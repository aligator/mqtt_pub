# mqtt_pub

Based on https://weechat.org/scripts/source/mqtt_notify.py.html/
but doesn't use the paho client because I had strange connection-problems even on localhost.
So I use mosquitto_pub instead, which works great and is fast enough for my usecase.
