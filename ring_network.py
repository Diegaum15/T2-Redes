import socket
import threading
import hashlib

class RingNetwork:
    def __init__(self, local_address, next_address):
        self.local_address = local_address
        self.next_address = next_address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.local_address)
        self.running = True
        self.thread = threading.Thread(target=self.receive_messages)
        self.thread.start()

    def send_message(self, message):
        self.sock.sendto(message.encode(), self.next_address)

    def receive_messages(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                message = data.decode()
                if validate_message(message):
                    self.process_message(message)
            except Exception as e:
                print(f"Error receiving message: {e}")

    def process_message(self, message):
        # Implementação para processar diferentes tipos de mensagens
        pass

    def stop(self):
        self.running = False
        self.sock.close()
        self.thread.join()

def calculate_checksum(message):
    return hashlib.md5(message.encode()).hexdigest()

def create_message(msg_type, origin, dest, message_id, ack, content):
    message = f"START;{msg_type};{origin};{dest};{message_id};{ack};{content}"
    checksum = calculate_checksum(message)
    return f"{message};{checksum}"

def validate_message(message):
    *parts, received_checksum = message.rsplit(';', 1)
    message_without_checksum = ';'.join(parts)
    calculated_checksum = calculate_checksum(message_without_checksum)
    return calculated_checksum == received_checksum
