class Concur(threading.Thread):
    def __init__(self):
        super(Concur, self).__init__()
        self.daemon = True  # Allow main to exit even if still running.
        self.paused = True  # Start out paused.
        self.state = threading.Condition()

    def run(self):
        self.resume()
        while True:
            with self.state:
                if self.paused:
                    self.state.wait()  # Block execution until notified.
            connecting_user = input('User ID: ')
            message = input('-> ')
            data = {'TOKEN':'SINGLECHAT', 'USERDATA':{'RECV_ID': connecting_user, 'TEXT':message}}
            data_json = json.dumps(data)
            client_socket.send(data_json.encode())

    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()  # Unblock self if waiting.

    def pause(self):
        with self.state:
            self.paused = True  # Block self.