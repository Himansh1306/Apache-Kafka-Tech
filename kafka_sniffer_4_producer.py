#!/usr/bin/python2.7
#Packet sniffer in python for Linux
#Sniffs only incoming TCP packet

#Usage: python kafka_sniffer.py -t topicname -s 0.0.0.0 -p 9092
import socket, sys
from struct import *
import getopt
import array


clients={'golang':"sarama",'default':"producer",'cpp':"librdkafka",'python':"pykafka"}

def encode(s):
    return ' '.join([bin(ord(c)).replace('0b', '') for c in s])

def bytes_to_int(bytes):
    result = 0

    for b in bytes:
        result = result * 256 + int(b)

    return result

def get_data_by_topic_source(topic,source,iphead,data):
	s_addr = socket.inet_ntoa(iphead[8])
	thread_start=14
        #print "From: "+s_addr
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
        unpack_data = data
        #print array.array('B',data)
        #message len,apikey,apiversion,correlationId,ClientId(len+data)
	head1 = unpack('>IHHIH',data[0:14])
	#print "Message Len: "+str(head1[0])
	#print "apikey: "+str(head1[1])
	#print "apiversion: "+str(head1[2])
	#print "correlationId: "+str(head1[3])
	#print "ClientId: "+str(head1[4])
## producer
	if head1[1] == 0:
		try:
			print "From: "+s_addr
        		print "Message Len: "+str(head1[0])
       			print "apikey: "+str(head1[1])
        		print "apiversion: "+str(head1[2])
        		print "correlationId: "+str(head1[3])
			if head1[2] == 3:
				pos=2
			else:
				pos=0
			len_producer = head1[-1]
	#		print "len_producer: "+str(len_producer)
			producer_name = data[14:14+len_producer]
			print "ClientId: "+producer_name
			#print array.array('B',data[14:14+len_producer])
			#ack,timeout,topic_num,topic_len,topic_name
			head2 = unpack('>HIIH',data[pos+14+len_producer:pos+14+len_producer+12])
			#print array.array('B',data[14+len_producer:14+len_producer+12])
			print "ack: "+ str(head2[0])
			print "timeout: "+ str(head2[1])
			print "topic_num: "+ str(head2[2])
			print "topic_len: "+ str(head2[3])
			topic_name = data[pos+14+len_producer+12:pos+14+len_producer+12+head2[3]]
			print "topic_name: "+topic_name
        		head3 = unpack('>IIIQIIBIHIQQQHI',data[pos+14+len_producer+12+head2[3]:pos+14+len_producer+12+head2[3]+69])
        		print "partition count: "+str(head3[0])
        		print "partition: "+str(head3[1])
			print "data"
        		#head4 = data[14+2+len_producer+12+head2[3]+69:14+2+len_producer+12+head2[3]+12+head3[2]]
			#print "head4"
			#print array.array('B',head4)
        		data_array = array.array('B',data)
        		data_len = bytes_to_int(data_array[0:4])
			ApiKey = bytes_to_int(data_array[4:6])
			ApiVersion = bytes_to_int(data_array[6:8])
  			CorrelationId = bytes_to_int(data_array[8:12])
			Clientlen = bytes_to_int(data_array[12:14])
        		ClientId = "".join(map(chr, data_array[14:14+Clientlen]))
        		# for ProduceRequest
			#ProduceRequest_start = 14 + Clientlen + 21 + 1
			ProduceRequest_start = 14 + Clientlen + 2
			RequiredAcks = bytes_to_int(data_array[ProduceRequest_start:ProduceRequest_start+2])
			Timeout = bytes_to_int(data_array[ProduceRequest_start+2:ProduceRequest_start+2+4])
			Topiclen = bytes_to_int(data_array[ProduceRequest_start+10:ProduceRequest_start+12])
			Topicname = "".join(map(chr, data_array[ProduceRequest_start+12:ProduceRequest_start+12+Topiclen]))
			Partitionlen = bytes_to_int(data_array[ProduceRequest_start+12+Topiclen:ProduceRequest_start+12+Topiclen+4])
			Partition = bytes_to_int(data_array[ProduceRequest_start+12+Topiclen+4:ProduceRequest_start+12+Topiclen+4+4])
			MessageSetSize = bytes_to_int(data_array[ProduceRequest_start+12+Topiclen+4+4:ProduceRequest_start+12+Topiclen+4+4+4])
			Offset = bytes_to_int(data_array[ProduceRequest_start+12+Topiclen+4+4+4:ProduceRequest_start+12+Topiclen+4+4+4+8])
			MessageSize = bytes_to_int(data_array[ProduceRequest_start+12+Topiclen+4+4+4+8:ProduceRequest_start+12+Topiclen+4+4+4+8+4])
#        		print "data length: ",data_len,data_array[0:4]
#        		print "ApiKey: ",ApiKey,data_array[4:6]
#        		print "ApiVersion: ",ApiVersion,data_array[6:8]
#        		print "CorrelationId: ",CorrelationId,data_array[8:12]
#			print "Clientlen: ",Clientlen,data_array[12:14]
#        		print "Client: ",ClientId,data_array[14:14+Clientlen]
#        		print "RequiredAcks: ",RequiredAcks,data_array[ProduceRequest_start:ProduceRequest_start+2]
#        		print "Timeout: ",Timeout,data_array[ProduceRequest_start+2:ProduceRequest_start+6]
#        		print "Topiclen: ",Topiclen,data_array[ProduceRequest_start+10:ProduceRequest_start+12]
#			print "Topicname: ",Topicname,data_array[ProduceRequest_start+12:ProduceRequest_start+12+Topiclen]
#			print "Partitionlen: ",Partitionlen,data_array[ProduceRequest_start+12+Topiclen:ProduceRequest_start+12+Topiclen+4]
#			print "Partition: ",Partition,data_array[ProduceRequest_start+12+Topiclen+4:ProduceRequest_start+12+Topiclen+4+4]
#			print "MessageSetSize: ",MessageSetSize,data_array[ProduceRequest_start+12+Topiclen+4+4:ProduceRequest_start+12+Topiclen+4+4+4]
#			print "Offset: ",Offset,data_array[ProduceRequest_start+12+Topiclen+4+4+4:ProduceRequest_start+12+Topiclen+4+4+4+8]
##			print "MessageSize: ",MessageSize,data_array[ProduceRequest_start+12+Topiclen+4+4+4+8:ProduceRequest_start+12+Topiclen+4+4+4+8+4]
#ClientId => str	ing
## clients['gola	ng'] is a client lib name and can be changed , for example "sarama" for golang lib
        		if clients['default'] in data[thread_start:thread_end]:
						next_step=12
        		        		topic_len=int(encode(data[thread_end+next_step-1]),2)
        		                        print "From "+s_addr+" "+data[thread_start:thread_end]+" Topic: "+data[thread_end+next_step:thread_end+next_step+topic_len]
        		                        next_step=12
        		                        topic_len=int(encode(data[thread_end+next_step-1]),2)
        		                        print data[thread_end+next_step:thread_end+next_step+topic_len]
		except:
			pass
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

def format_multi_line(prefix, string, size=80):
    size -= len(prefix)
    if isinstance(string, bytes):
        string = ''.join(r'\x{:02x}'.format(byte) for byte in string)
        if size % 2:
            size -= 1
    return '\n'.join([prefix + line for line in textwrap.wrap(string, size)])

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
