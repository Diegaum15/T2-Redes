import sys
import ipaddress
import socket
import time
import operator
import os
from ring_network import RingNetwork
from game_logic import Game

#Pede IP, até receber um IP válido
#Recebe string especificando qual tipo de IP o usuário deve passar
def pede_ip(tipo):
    ip = input(f"Digite o IP {tipo}:")
    while(checar_ip(ip) == False):
        print("\nIP digitado inválido!")
        ip = input(f"Digite o IP {tipo}:")
    return ip

#Checa se ip é válido
def checar_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

#Retorna o endereço IP local utilizado para acessar a rede
#Se nao conseguir pede para o IP para o usuário
def pegar_ip_local():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #cria socket udp
    try:
        s.connect(("8.8.8.8", 80)) #connect não é realizado com UDP, só serve para retornar o IP
    except:
        s.close()
        print("Não foi possível determinar o IP Local")
        return pede_ip("local")

    ip = s.getsockname()[0]
    s.close()
    return ip
    

if __name__ == "__main__":
    #Pega ip do proximo node, seja por argumento da linha de comando, ou pelo usuário
    if len(sys.argv) != 2:
        print("Entrada incorreta!")
        print("Uso: python main.py <ip do próximo node>")
        next_address = pede_ip("do próximo node")
    else:
        next_address = sys.argv[1]
        if (checar_ip(next_address) == False):
            next_address = pede_ip("do próximo node")
    
    #Pega ip local
    local_address = pegar_ip_local()
    # local_address = "127.0.0.1"

    network = RingNetwork(local_address, next_address)
    
    #Mensagem com tempo atual
    timestamp = time.time()
    timestamp_msg = network.create_message(0,0,0,timestamp)
        
    player = 0
    players = []
    player_amt = 0
    
    #Manda tempo para frente, primeiro a abrir vai ter o bastão
    network.change_timeout(1)
    while (True):
        print("Tentando conectar")
        network.send_message(timestamp_msg)
        received = network.receive_messages()
        
        if (received != None):
            #Foi o primeiro a abrir
            if (int(received.split(';')[0]) == 0 and float(received.split(';')[3]) == timestamp):
                network.change_timeout(None)
                network.send_message(network.create_message(1,0,0,player+1))
                received = network.receive_messages()
                player_amt = int(received.split(';')[3])
                network.send_message(network.create_message(2,0,0,player_amt))
                received = network.receive_messages()
                break
            #Não foi o primeiro a abrir
            elif (int(received.split(';')[0]) == 0 and float(received.split(';')[3]) < timestamp):
                network.change_timeout(None) #Desativa timeout
                
                #Espera receber tipo 1 (player)
                while(int(received.split(';')[0]) != 1):
                    network.send_message(received)
                    received = network.receive_messages()
                player = int(received.split(';')[3]) #Recebeu player
                network.send_message(network.create_message(1,0,0,player+1)) #Passa para frente
                
                received = network.receive_messages()
                #Espera receber tipo 2 (player_amt)
                while (int(received.split(';')[0]) != 2):
                    network.send_message(received)
                    received = network.receive_messages()
                        
                player_amt = int(received.split(';')[3])#Recebeu player_amt
                network.send_message(network.create_message(2,0,0,player_amt)) #Passa para frente
                received = network.receive_messages()
                break
            
    for i in range(player_amt):
        players.append(("Player " + str(i+1)))
    
    game = Game(players)
    game.players.player = player
    
    os.system('clear')
    print("Jogo iniciado!")
    print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")

    #loop do jogo
    while (True):
        if (game.players.dealer == game.players.player):# se você é o dealer
            #Distribui as cartas
            game.shuffle_and_deal()
            while (len(game.hands[game.players.previous_string()]) > 0): #envia até enviar todas do último player
                for dest_player in range(player_amt):
                    if (dest_player != game.players.player):
                        message = network.create_message(3,game.players.dealer,dest_player,game.hands[game.players.items[dest_player]].pop(0))
                        network.send_message(message)
                        network.receive_messages()
            print("Sua mão = ", game.hands[game.players.current_string()], "\n")
            
            #Coleta as apostas
            #quantas o dealer acha que faz
            try:
                bid = int(input("Quantas rodadas você acredita que faz?\n"))
            except ValueError:
                bid = -1
            while (bid < 0 or bid > game.num_cards):
                print("Valor invalido, deve ser um número entre 0 e", str(game.num_cards))
                try:
                    bid = int(input("Quantas rodadas você acredita que faz?\n"))
                except ValueError:
                    print("Valor deve ser um número")
            print("Aguardando aposta dos oponentes...")
            
            bid_string = str(game.players.player) + "-" + str(bid) + "-"
            network.send_message(network.create_message(4,0,0,bid_string))
            received = network.receive_messages()
            
            network.send_message(network.create_message(4,0,-1,received.split(';')[3]))
            received = network.receive_messages()
            
            os.system('clear')
            print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")
            
            received_bids = received.split(';')[3].split('-')
            received_bids.pop()
            
            print("Apostas:")
            
            for i in range(0, len(received_bids), 2):
                print("Player " + str(int(received_bids[i])+1) + " apostou " + received_bids[i+1])
                game.bids[game.players.items[int(received_bids[i])]] = int(received_bids[i+1])
            
            print("")
            won_bids = {player: 0 for player in game.players.items}
            
            #Escolhe e manda carta
            while (len(game.hands[game.players.current_string()]) > 0):
                
                print("Sua mão = ", game.hands[game.players.current_string()], "\n")
                if (game.players.player != game.players.first_player):#dealer e nao eh primeiro
                    print("Aguardando escolha dos oponentes...")
                    while (int(received.split(';')[0]) != 5):#espera chegar a carta do primeiro
                        network.send_message(received)
                        received = network.receive_messages()
                    best_card = received.split(';')[3]
                    print("\nA maior carta no momento é: " + best_card)
                
                card = input("Escolha qual carta deseja jogar.\n")
                while (card not in game.hands[game.players.current_string()]):
                    print("A Carta " + card + " não foi encontrada. Digite a carta novamente")
                    card = input("Escolha qual carta deseja jogar.\n")
                game.hands[game.players.current_string()].remove(card)
                
                if (game.players.player != game.players.first_player): #dealer e nao eh primeiro
                    stronger = game.stronger_card(card, best_card)
                    if (stronger == None or stronger == card):
                        network.send_message(network.create_message(5,game.players.player,0,card))
                    else:
                        network.send_message(received)
                    received = network.receive_messages()
                    while (int(received.split(';')[2]) != -1): #enquanto nao eh pro dealer
                        network.send_message(received)
                        received = network.receive_messages()
                else:# dealer e primeiro
                    print("Aguardando escolha dos oponentes...")
                    network.send_message(network.create_message(5,0,0,card))
                    received = network.receive_messages()
                
                os.system('clear')
                print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")
                
                game.players.first_player = int(received.split(';')[1])
                
                if (game.players.first_player != game.players.player):
                    print("O Player", game.players.first_player+1, "ganhou a rodada passada.\n")
                else:
                    print("Parabéns! Você ganhou a rodada passada!\n")
                
                won_bids[game.players.items[game.players.first_player]] += 1
                
                network.send_message(network.create_message(6,0,0,received.split(';')[1]))
                received = network.receive_messages()
                
            #Desconta os pontos
            for player in game.players.items:
                difference = abs(game.bids[player] - won_bids[player])
                result = game.lives[player]
                if (result - difference > 0):
                    result -= difference
                else:
                    result = 0
                game.lives[player] = result
                network.send_message(network.create_message(7,game.players.dealer,game.players.items.index(player),result))
                network.receive_messages()  
            
            #Testa se o jogo acabou
            dead = operator.countOf(game.lives.values(), 0)
            if (dead == player_amt-1):
                os.system('clear')
                print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")
                values = list(game.lives.values())
                winner = values.index(max(values))
                print("O Player", str(winner+1), "ganhou o jogo!")
                network.send_message(network.create_message(8,0,0,winner))
                network.receive_messages()
                break
            elif (dead == player_amt):
                os.system('clear')
                print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")
                print("\nEmpate!")
                network.send_message(network.create_message(8,0,0,player_amt))
                network.receive_messages()
                break
            
            if (game.num_cards == 1):
                keys = list(game.lives.keys())
                values = list(game.lives.values())
                tie = operator.countOf(values, max(values))
                if (tie > 1):
                    os.system('clear')
                    print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")
                    print("Empate!")
                    network.send_message(network.create_message(8,0,0,player_amt))

                else:
                    os.system('clear')
                    print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")
                    print("O Player", str(values.index(max(values))+1), "ganhou o jogo!")
                    network.send_message(network.create_message(8,0,0,values.index(max(values))))
                network.receive_messages()
                break
            
            #Atualiza valores para a próxima rodada
            game.num_cards -= 1
            game.players.dealer = game.players.next_dealer()
            game.round += 1
            
            #imprime informações
            os.system('clear')
            print("Novo round iniciado!")
            print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")
            
            if (game.players.first_player != game.players.player):
                print("O Player", int(received.split(';')[3])+1, "ganhou a rodada passada.\n")
            else:
                print("Parabéns! Você ganhou a rodada passada!\n")
        else:
            #passa bastão até receber a mão
            while (int(received.split(';')[0]) != 3):
                network.send_message(received)
                received = network.receive_messages()
            
            imprimiu = 0
            #até receber as apostas, está recebendo a mão
            while (int(received.split(';')[0]) != 4):
                if (int(received.split(';')[2]) == game.players.player):
                    game.hands[game.players.current_string()].append(received.split(';')[3])
                network.send_message(received)
                if (imprimiu == 0 and len(game.hands[game.players.current_string()]) == game.num_cards):
                    imprimiu = 1
                    print("Sua mão = ", game.hands[game.players.current_string()], "\n")
                    print("Aguardando apostas dos oponentes...")
                received = network.receive_messages()
            
            #Recebe as apostas
            total_bids = 0
            received_bids = received.split(';')[3].split('-')
            for i in range(len(received_bids)):
                if (i % 2 == 1):
                    total_bids += int(received_bids[i])
            print("\nTotal de apostas é " + str(total_bids))
            try:
                bid = int(input("Quantas rodadas você acredita que faz?\n"))
            except ValueError:
                bid = -1
            while (bid < 0 or bid > game.num_cards or (game.players.next_index() == game.players.dealer and bid+total_bids == game.num_cards)):
                if (game.players.next_index() == game.players.dealer and bid+total_bids == game.num_cards):
                    print("A soma das apostas não pode ser igual ao número de cartas, ou seja, deve ser diferente de ", game.num_cards-total_bids)
                else:
                    print("Quantidade inválida, deve ser entre 0 e ", game.num_cards)
                print("Total de apostas é " + str(total_bids))
                try:
                    bid = int(input("Quantas rodadas você acredita que faz?\n"))
                except ValueError:
                    print("Valor deve ser um número")
            
            bid_string = received.split(';')[3] + str(game.players.player) + "-" + str(bid) + "-"
            
            network.send_message(network.create_message(4,0,0,bid_string))
            received = network.receive_messages()
            
            while (int(received.split(';')[0]) != 4 or int(received.split(';')[2]) != -1):
                network.send_message(received)
                received = network.receive_messages()
           
            os.system('clear')
            print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")
            
            print("Apostas:")
            
            received_bids = received.split(';')[3].split('-')
            received_bids.pop()
            
            for i in range(0, len(received_bids), 2):
                print("Player " + str(int(received_bids[i])+1) + " apostou " + received_bids[i+1])
                game.bids[game.players.items[int(received_bids[i])]] = int(received_bids[i+1])
            
            print("")
            
            print("Sua mão = ", game.hands[game.players.current_string()], "\n")
            
            print("Aguarde os outros jogarem suas cartas...")
            
            network.send_message(received)
            received = network.receive_messages()
            
            #Escolhe e manda carta
            while (len(game.hands[game.players.current_string()]) > 0):
                
                if (game.players.player != game.players.first_player):
                    while (int(received.split(';')[0]) != 5):
                        network.send_message(received)
                        received = network.receive_messages()
                    best_card = received.split(';')[3]
                    print("\nA maior carta no momento é: " + best_card)
                
                card = input("Escolha qual carta deseja jogar.\n")
                while (card not in game.hands[game.players.current_string()]):
                    print("A Carta " + card + " não foi encontrada. Digite a carta novamente")
                    card = input("Escolha qual carta deseja jogar.\n")
                game.hands[game.players.current_string()].remove(card)
                
                if (game.players.player != game.players.first_player):
                    stronger = game.stronger_card(card, best_card)
                    if (stronger == None or stronger == card):
                        network.send_message(network.create_message(5,game.players.player,0,card))
                    else:
                        network.send_message(received)
                else:
                    network.send_message(network.create_message(5,game.players.player,0,card))
                    received = network.receive_messages()
                    best_card = received.split(';')[3]
                    stronger = game.stronger_card(card, best_card)
                    if (stronger == None or stronger == card):
                        network.send_message(network.create_message(5,game.players.player,-1,card))
                    else:
                        network.send_message(network.create_message(5,received.split(';')[1],-1,best_card))
                    
                received = network.receive_messages()
                while(int(received.split(';')[0]) != 6):
                    network.send_message(received)
                    received = network.receive_messages()
                
                os.system('clear')
                print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")
                game.players.first_player = int(received.split(';')[3])
                if (game.players.first_player != game.players.player):
                    print("O Player", game.players.first_player+1, "ganhou a rodada passada.\n")
                else:
                    print("Parabéns! Você ganhou a rodada passada!\n")
                
                if (len(game.hands[game.players.current_string()]) > 0):
                    print("Sua mão = ", game.hands[game.players.current_string()], "\n")
                    print("Aguardando escolha dos oponentes...")
                
                network.send_message(received)
                received = network.receive_messages()
            
            #Recebe pontos perdidos
            if (int(received.split(';')[0]) == 7):
                for i in range(player_amt):
                    game.lives[game.players.items[int(received.split(';')[2])]] = int(received.split(';')[3])
                    network.send_message(received)
                    received = network.receive_messages()
            
            #jogo acabou
            if (int(received.split(';')[0]) == 8):
                os.system('clear')
                print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")
                if (int(received.split(';')[3]) == player_amt):
                    print("Empate!")
                elif (int(received.split(';')[3]) == game.players.player):
                    print("Parabéns! Você ganhou o jogo!")
                else:
                    print("O Player", str(int(received.split(';')[3])+1), "ganhou o jogo!")
                network.send_message(received)
                break
            else:
                #Atualiza informações
                game.num_cards -= 1
                game.players.dealer = game.players.next_dealer()
                game.round += 1
                
                #Imprime informações
                os.system('clear')  
                print("Novo round iniciado!")
                print("Você é o", game.players.current_string(), "| Round:", game.round, "| Vidas:", game.lives[game.players.current_string()], "| Dealer:", game.players.dealer+1, "\n")
                
                if (game.players.first_player != game.players.player):
                    print("O Player", game.players.first_player+1, "ganhou a rodada passada.\n")
                else:
                    print("Parabéns! Você ganhou a rodada passada!\n")