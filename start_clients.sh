#!/bin/bash

#python -m kickstarter.kickstart -i kickstarter/ec2_init.sh
#sleep 10

DEFAULT_QUEUE_NAME=dsurv-client-queue

python -m client.client_main \
	-i client/lorem.txt \
	-o 1.txt \
	-c ${DEFAULT_QUEUE_NAME}-1 &

python -m client.client_main \
	-i client/lorem.txt \
	-o 2.txt \
	-l sed magna vitae bla \
	-c ${DEFAULT_QUEUE_NAME}-2 &

python -m client.client_main \
	-i client/lorem.txt \
	-o 3.txt \
	-d \
	-c ${DEFAULT_QUEUE_NAME}-3 &

python -m client.client_main \
	-i client/lorem.txt \
	-o 4.txt \
	-d \
	-l sed magna vitae \
	-c ${DEFAULT_QUEUE_NAME}-4 &

python -m client.client_main \
	-i server/test/empty.txt \
	-o 5.txt \
	-c ${DEFAULT_QUEUE_NAME}-5 &

python -m client.client_main \
	-i server/test/empty.txt \
	-o 6.txt \
	-l bla1 bla2 bla3 \
	-c ${DEFAULT_QUEUE_NAME}-6 &

python -m client.client_main \
	-i client/lorem.txt \
	-o 7.txt \
	-l bla1 bla2 bla3 \
	-c ${DEFAULT_QUEUE_NAME}-7 &


