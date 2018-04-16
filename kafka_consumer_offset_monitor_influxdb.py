#!/usr/bin/python2.7
'''
1, not support python3 because of a difference in dict behavior between python 2 and 3, refer https://github.com/Parsely/pykafka/issues/670
2, need to pip install influxdb
'''
from pykafka import KafkaClient
from pykafka.utils.compat import iteritems
import pykafka.cli.kafka_tools as kafka_tools
import logging as log
import sys

from influxdb import InfluxDBClient
from influxdb.client import InfluxDBClientError
from datetime import datetime
import time

log.basicConfig(level=log.CRITICAL,format='%(asctime)s %(levelname)s %(message)s')

import argparse
parser = argparse.ArgumentParser(description='kafka consummer offset remote check')
parser.add_argument('-kafkabroker', help='-kafkabroker 127.0.0.1:9092')
args = parser.parse_args()

USER = 'root'
PASSWORD = 'xxx'
DBNAME = 'kafka_monitor'
host='ip'
port=8086

kafka_brokers = sys.argv[2]

client = KafkaClient(hosts=kafka_brokers)

# get all topics
topics = client.topics

# get all brokers
brokers = client.brokers

consumer_groups = []

# get all consumer groups
for broker_id, broker in brokers.iteritems():
    consumer_groups = consumer_groups + broker.list_groups().groups.keys()

# point value in influxdb
series = []

# connect to influxdb
client_influx = InfluxDBClient(host, port, USER, PASSWORD, DBNAME)

# get offset of all consumer groups
for topic in client.topics:
    c_topic =topics[topic]
    for group in consumer_groups:
	sum_lag = 0
        sum_offset = 0
	now = datetime.utcfromtimestamp(time.time())
        try:
                lags = kafka_tools.fetch_consumer_lag(client, c_topic, group)
		# sum offset of each partition
		for k,v in iteritems(lags):
			sum_lag = sum_lag + (v[0]-v[1])
			sum_offset = sum_offset + v[0]
		pointValues = {
                	"time": now.strftime ("%Y-%m-%dT%H:%M:%SZ"),
                	"measurement": 'kafka-app-log-offset',
                	'fields':  {
                    		'value_offset': sum_offset,
                    		'value_lag': sum_lag,
				'consumer': group,
				'topic': topic,
                	},
            	}
		series.append(pointValues)
		client_influx.write_points(series)
		series = []
	   
                ## generate differetn time
		time.sleep(1)

		## log details
		log.critical(now)
		log.critical(topic, group, sum_offset, sum_lag)
        except Exception, e:
            	log.critical(e)
