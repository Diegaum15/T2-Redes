import socket
import threading
import hashlib
# PORT = 1111

class RingNetwork:
    def __init__(self, local_address, next_address):
        localport = int(input("Qual a sua porta:"))
        nextport = int(input("Qual a porta do proximo: "))
        self.local_address = tuple([local_address, localport])
        self.next_address = tuple([next_address, nextport])
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.local_address)

    def change_timeout(self, timeout):
        self.sock.settimeout(timeout)

    #type 0 - manda timestamp; type 1 - manda player;  type 2 - manda player_amt; type 3 - manda cartas; type 4 - manda aposta
    #type 5 - manda carta jogada; type 6 - jogador que ganhou a rodada ;type 7 - manda pontos perdidos; type 8 - manda quem ganhou
    def create_message(self, msg_type, origin, dest, message_id, ack, content):
        message = f"START;{msg_type};{origin};{dest};{message_id};{ack};{content}"
        checksum = calculate_checksum(message)
        return f"{message};{checksum}"

    def send_message(self, message):
        self.sock.sendto(message.encode(), self.next_address)

    def receive_messages(self):
        # while self.running:
        try:
            data, addr = self.sock.recvfrom(1024)
            if (data != None):
                message = data.decode()
                if validate_message(message):
                    return message
                else:
                    print("Mensagem inválida")
                    exit(1)
            else:
                print("Erro no socket")
                exit(1)
        except socket.timeout:
            return None        

def calculate_checksum(message):
    return hashlib.md5(message.encode()).hexdigest()

def validate_message(message):
    content, received_checksum = message.rsplit(';', 1)
    message_list = content.split(';')
    calculated_checksum = calculate_checksum(content)
    return calculated_checksum == received_checksum
