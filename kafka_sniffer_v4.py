#!/usr/bin/python2.7
#Packet sniffer in python for Linux
#Sniffs only incoming TCP packet

#Usage: python kafka_sniffer.py -t topicname -s 0.0.0.0 -p 9092
import socket, sys
from struct import *
import getopt


def encode(s):
    return ' '.join([bin(ord(c)).replace('0b', '') for c in s])

def get_data_by_topic_source(topic,source,iphead,data):
	s_addr = socket.inet_ntoa(iphead[8])
	thread_start=14
	if topic != "all" and source != "0.0.0.0":
		if s_addr == source and topic in data:
			#print "Topic: "+topic+ " From: "+source
			get_producer_data(s_addr,thread_start,data)
	elif topic == "all" and source != "0.0.0.0":
		if s_addr == source:
			#print "From: "+source
			get_producer_data(s_addr,thread_start,data)
	elif topic != "all" and source == "0.0.0.0":
		if topic in data:
			#print "Topic: "+topic+" From: "+s_addr
			get_producer_data(s_addr,thread_start,data)
	else:
		if len(data) >=thread_start:
				get_producer_data(s_addr,thread_start,data)
				get_replica_fetcher_data(s_addr,thread_start,data)


def get_producer_data(s_addr,thread_start,data):
	thread_end=thread_start+int(encode(data[thread_start-1]),2)
	## producer is a client lib name and can be changed , for example "sarama" for golang lib
        if "producer" in data[thread_start:thread_end]:
				next_step=12
                		topic_len=int(encode(data[thread_end+next_step-1]),2)
                                print "From "+s_addr+" "+data[thread_start:thread_end]+" Topic: "+data[thread_end+next_step:thread_end+next_step+topic_len]
                                next_step=12
                                topic_len=int(encode(data[thread_end+next_step-1]),2)
                                print data[thread_end+next_step:thread_end+next_step+topic_len]
def get_replica_fetcher_data(s_addr,thread_start,data):
	thread_end = thread_start+int(encode(data[thread_start-1]),2)
	fetch_topics_v = ""
	if "ReplicaFetcherThread" in data[thread_start:thread_start+int(encode(data[thread_start-1]),2)]:
                                print "From "+s_addr+" "+" Fetch: "+data[thread_start:thread_end]
                                topic_len1 = int(encode(data[thread_end+17]),2)

				data_end = thread_end+18+topic_len1
                                while data_end + 4 < len(data):
                                        if encode(data[data_end:data_end+2]) == "11 100000":
                                                if encode(data[data_end+5]) != "0":
                                        		fetch_topics_v = ''.join(data[data_end+5:data_end+5+int(encode(data[data_end+5]),2)+1])
							print fetch_topics_v
                                        data_end=data_end + 1
	return fetch_topics_v


def upack_packet(port,topic,source):
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
	get_data_by_topic_source(topic,source,iph,data)

def main():
	try:
        	opts, args = getopt.getopt(sys.argv[1:], '-ht:s:p:',['h','t','s','p'])
	except getopt.GetoptError:
        	print 'Error: kafka_sniffer.py -t <topic> -s <source> -p <kafka_port>'
        	sys.exit(2)
        if len(opts) == 0:
		print "Error: python kafka_sniffer.py -h for help"
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

        upack_packet(port,topic,source)
if __name__ == "__main__":
    	main()
