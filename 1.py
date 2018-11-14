import getpass 
import socket
import ast
import threading
import json


def fun():
	for i in range(0,10000000):
		if i%100000==0:
			print(i)

def readd():
	a = input("->")
	print(a)

threads = []
t1 = threading.Thread(target=fun, args=())
threads.append(t1)
t1.daemon = True

t2 = threading.Thread(target=readd, args=())
threads.append(t2)
t2.daemon = True

t2.start()
t1.start()


t1.join()
t2.join()
