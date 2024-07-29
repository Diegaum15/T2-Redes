import sys
from ring_network import RingNetwork
from game_logic import Game
from game_gui import GameGUI

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python main.py <ip_local>:<porta_local> <ip_next>:<porta_next>")
        sys.exit(1)

    local_address = tuple(sys.argv[1].split(':'))
    next_address = tuple(sys.argv[2].split(':'))

    local_address = (local_address[0], int(local_address[1]))
    next_address = (next_address[0], int(next_address[1]))

    players = ["Jogador 1", "Jogador 2", "Jogador 3", "Jogador 4"]
    game = Game(players)

    network = RingNetwork(local_address, next_address)
    gui = GameGUI(game, network)
    network.gui = gui  # Pass the GUI to the network for callbacks
    gui.run()

    network.stop()
    sys.exit(0)
