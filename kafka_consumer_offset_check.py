#!/usr/bin/python2.7
'''
1, not support python3 because of a difference in dict behavior between python 2 and 3, refer https://github.com/Parsely/pykafka/issues/670
2, todo: will make it as the prometheus exporter
'''
from pykafka import KafkaClient
from pykafka.utils.compat import iteritems
import pykafka.cli.kafka_tools as kafka_tools
import logging as log
import sys
log.basicConfig(level=log.CRITICAL,format='%(asctime)s %(levelname)s %(message)s')

import argparse
parser = argparse.ArgumentParser(description='kafka consummer offset remote check')
parser.add_argument('-kafkabroker',required=True, help='-kafkabroker 127.0.0.1:9092')
args = parser.parse_args()


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
# get all consumer groups lag according each topic
for topic in client.topics:
    c_topic =topics[topic]
    for group in consumer_groups:
		try:
    		    lags = kafka_tools.fetch_consumer_lag(client, c_topic, group)
                    lag_info = [(k, '{:}'.format(v[0] - v[1]), v[0], v[1]) for k, v in iteritems(lags)]
		    print(topic , group , lag_info)
                except Exception, e:
		    log.critical(e)
