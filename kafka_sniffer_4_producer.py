#!/bin/python2.7

"""Funtion.
1, Unpack the packet by sniffer from kafka tcp port
2, Get the producer(client) ip, port and kafka protocol related info
"""

"""Usage.
1, Run on kafka broker server
2, python kafka_sniffer.py -t topicname -s 0.0.0.0 -p 9092
"""

"""
Author:Samuel 
Date:20180218
"""

import socket, sys
from struct import *
import getopt
import array


clients={'golang':"sarama",'default':"producer",'cpp':"librdkafka",'python':"pykafka"}


def get_producer_data(data,topic,output):
	api_client_part = unpack('>IHHIH',data[0:14])
	## Producer ApiKey
	if api_client_part[1] == 0:
		try:
			client_len = api_client_part[-1]
			if api_client_part[2] == 3:
				pos=2
			else:
				pos=0
			client_len = api_client_part[-1]
                        topic_part = unpack('>HIIH',data[pos+14+client_len:pos+14+client_len+12])
			topic_name = data[pos+14+client_len+12:pos+14+client_len+12+topic_part[3]]
			## print topic_name
        		if topic_name == topic:
        			partition_part = unpack('>IIIQIIBIHIQQQHI',data[pos+14+client_len+12+topic_part[3]:pos+14+client_len+12+topic_part[3]+69])
                                output['DataLen'] = api_client_part[0]
                                output['ApiKey'] = api_client_part[1]
                                output['ApiVersion'] = api_client_part[2]
                                output['CorrelationId'] = api_client_part[3]
                                output['Client'] = data[14:14+client_len]
                                output['RequiredAcks'] = topic_part[0]
                                output['Timeout'] = topic_part[1]
                                output['TopicName'] = topic_name
                                output['PartitionCount'] = partition_part[0]
				print output.items()
		except Exception as e:
			print e
			pass

def get_replica_fetcher_data(data,topic):
	#todo
	pass

def unpack_packet(port,topic,source):
    try:
	s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    except socket.error , msg:
        print 'Socket create failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    while True:
    	packet = s.recvfrom(65565)
    	#packet string from tuple
    	packet = packet[0]
    	#ip header
    	ip_header = packet[0:20]
    	iph = unpack('!BBHHHBBH4s4s' , ip_header)
        #tcp header
        version_ihl = iph[0]
        version = version_ihl >> 4
        ihl = version_ihl & 0xF
        iph_length=ihl * 4
        tcp_header = packet[iph_length:iph_length+20]
        tcph = unpack('!HHLLBBHHH' , tcp_header)
    	ttl = iph[5]
    	protocol = iph[6]
    	s_addr = socket.inet_ntoa(iph[8]);
    	d_addr = socket.inet_ntoa(iph[9]);
        #tcp header
    	tcp_header = packet[iph_length:iph_length+20]
    	tcph = unpack('!HHLLBBHHH' , tcp_header)
    	source_port = tcph[0]
    	dest_port = tcph[1]
    	sequence = tcph[2]
    	acknowledgement = tcph[3]
    	doff_reserved = tcph[4]
    	tcph_length = doff_reserved >> 4
        #data
        h_size = iph_length + tcph_length * 4
        data_size = len(packet) - h_size
        data = packet[h_size:]

	#get data by topic&source
	output={'SourceIP':'','SourcePort':'','DestIP':'','DestPort':'','DataLen':-1,'ApiKey':-1,'ApiVersion':-1,'CorrelationId':-1,'Client':'','RequiredAcks':-1,'Timeout':-1,'TopicName':'','PartitionCount':-1}
	output['SourceIP'] = s_addr
	output['SourcePort'] = source_port
	output['DestIP'] = d_addr
	output['DestPort'] = dest_port
	if len(data)>12 and source == output['SourceIP'] and topic in data:
		get_producer_data(data,topic,output)
	elif len(data)>12 and source == "0.0.0.0" and topic in data:
		get_producer_data(data,topic,output)
	else:
		pass
		#print 'source address or topic is not existing'

def main():
	try:
        	opts, args = getopt.getopt(sys.argv[1:], '-ht:s:p:',['h','t','s','p'])
	except getopt.GetoptError:
        	print 'Error: kafka_sniffer.py -t <topic> -s <source> -p <kafka_port>'
        	sys.exit(2)
        if len(opts) == 0:
		print 'Error: python kafka_sniffer.py -h for help'
		sys.exit(2)
	for opt, arg in opts:
        	if opt == "-h" :
            		print ' kafka_sniffer.py -t <topic> -s <source> -p <kafka_port>'
            		print ' if all topics, topic=all'
            		print ' if all sources, source=0.0.0.0'
            		sys.exit()
		if opt in ('-t'):
			topic=arg
		if opt in ('-s'):
			source=arg
		if opt in ('-p'):
			port=arg
	print "topic:", topic
	print "source:", source
	print "port:", port

        unpack_packet(port,topic,source)
if __name__ == "__main__":
    	main()
