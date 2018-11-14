import time
import threading
import os
import signal
import sys
import fileinput

lock = threading.Lock()

class FiveSec(threading.Thread):
	def restart(self):
		self.my_timer = time.time() + 5
	def run(self, *args):
		self.restart()
		while 1:
			time.sleep(0.1)
			if time.time() >= self.my_timer:
				break
		for line in fileinput.input():
			print(line)
		# lock.acquire()
		# file = sys.stdin
		# file = open(file)
		# data = file.read()
		# file = close(file)
		print(data)
		# print('\n')
		print("abcd")
		lock.release()



def main():
	t = FiveSec()
	t.daemon = True
	t.start()
	x = input('::> ')
	print(x)

if __name__ == '__main__':
	main()


