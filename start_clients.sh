#!/bin/bash
declare -a PID_ARRAY

DEFAULT_QUEUE_NAME=dsurv-client-queue

#python -m kickstarter.kickstart -i kickstarter/ec2_init.sh
#sleep 10
OUTDIR=./tmp
mkdir -p ${OUTDIR}

python -m client.client_main \
	-i client/lorem.txt \
	-o ${OUTDIR}/1.txt \
	-c ${DEFAULT_QUEUE_NAME}-11 &
PID_ARRAY[0]=$!

python -m client.client_main \
	-i client/lorem.txt \
	-o ${OUTDIR}/2.txt \
	-l sed magna vitae bla \
	-c ${DEFAULT_QUEUE_NAME}-21 &
PID_ARRAY[1]=$!

python -m client.client_main \
	-i client/lorem.txt \
	-o ${OUTDIR}/3.txt \
	-d \
	-c ${DEFAULT_QUEUE_NAME}-31 &
PID_ARRAY[2]=$!

python -m client.client_main \
	-i client/lorem.txt \
	-o ${OUTDIR}/4.txt \
	-d \
	-l sed magna vitae \
	-c ${DEFAULT_QUEUE_NAME}-41 &
PID_ARRAY[3]=$!

python -m client.client_main \
	-i server/test/empty.txt \
	-o ${OUTDIR}/5.txt \
	-c ${DEFAULT_QUEUE_NAME}-51 &
PID_ARRAY[4]=$!

python -m client.client_main \
	-i server/test/empty.txt \
	-o ${OUTDIR}/6.txt \
	-l bla1 bla2 bla3 \
	-c ${DEFAULT_QUEUE_NAME}-61 &
PID_ARRAY[5]=$!

python -m client.client_main \
	-i client/lorem.txt \
	-o ${OUTDIR}/7.txt \
	-l bla1 bla2 bla3 \
	-c ${DEFAULT_QUEUE_NAME}-71 &
PID_ARRAY[6]=$!

for i in ${PID_ARRAY[*]}
do
	wait $i
done

