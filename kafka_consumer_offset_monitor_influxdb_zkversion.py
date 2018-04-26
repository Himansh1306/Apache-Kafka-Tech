#!/usr/bin/python2.7
'''
1, support kafka version from 0.8 to 1.0
2, get consumer offset from zookeeper
3, if your offset stored in kafka , please refer https://github.com/foreversunyao/Apache-Kafka-Tech/blob/master/kafka_consumer_offset_monitor_influxdb.py
'''

from kafka import SimpleClient
from kafka.protocol.offset import OffsetRequest, OffsetResetStrategy
from kafka.common import OffsetRequestPayload
import logging as log
import sys

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from datetime import datetime
import random
import time
from kazoo.client import KazooClient

log.basicConfig(level=log.CRITICAL,format='%(asctime)s %(levelname)s %(message)s')

import argparse
parser = argparse.ArgumentParser(description='kafka consummer offset remote check')
parser.add_argument('-kafkabroker', help='-kafkabroker 127.0.0.1:9092')
parser.add_argument('-zk', help='-zk 127.0.0.1:2181')
parser.add_argument('-topic', help='-topic topic1')
args = parser.parse_args()

## influxdb db connection info
USER=''
PASSWORD=''
DBNAME='kafka_monitor'
host=''
port=8086

## kafka cluster name, measurement in influxdb
kafka_name=""
zk_path='/consumers/'
consumer_group=''
kafka_brokers=sys.argv[2]
zk_clusters=sys.argv[4]
topic=sys.argv[6]

client = SimpleClient(kafka_brokers)

partitions = client.topic_partitions[topic]
offset_requests = [OffsetRequestPayload(topic, p, -1, 1) for p in partitions.keys()]

offsets_responses = client.send_offset_request(offset_requests)

zk = KazooClient(hosts=zk_clusters,read_only=True)
zk.start()

zk_path=zk_path+consumer_group
if zk.exists(zk_path):
	data, stat = zk.get(zk_path+"/offsets/"+topic+"/1")
	sum_lag=0
	sum_offset=0
	for r in offsets_responses:
		consumer_offset, stat = zk.get(zk_path+"/offsets/"+topic+"/"+str(r.partition))
		producer_offset=r.offsets[0]
		lag_partition=producer_offset - int(consumer_offset)
		#print("Partition: %s, lag: %s" % (r.partition, lag_partition))
		sum_offset=sum_offset+producer_offset
		sum_lag=sum_lag+lag_partition
	print("Topic: %s, sum_lag: %s" % (topic,sum_lag))

series = []
client_influx = InfluxDBClient(host, port, USER, PASSWORD, DBNAME)
now = datetime.utcfromtimestamp(time.time())
try:
	pointValues = {
                "time": now.strftime ("%Y-%m-%dT%H:%M:%SZ"),
                "measurement": kafka_name,
                'fields':  {
                    	'value_offset': producer_offset,
                    	'value_lag': sum_lag,
			'consumer': consumer_group,
			'topic': topic,
                	},
            	}
	series.append(pointValues)
	print(series)
	client_influx.write_points(series)
except Exception, e:
        log.critical(e)
print ("done")
