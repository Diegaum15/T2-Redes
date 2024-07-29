import tkinter as tk
from ring_network import create_message

class GameGUI:
    def __init__(self, game, network):
        self.game = game
        self.network = network
        self.root = tk.Tk()
        self.root.title("Jogo Fodinha")
        self.setup_ui()

    def setup_ui(self):
        self.info_label = tk.Label(self.root, text="Bem-vindo ao Jogo Fodinha!")
        self.info_label.pack()
        self.start_button = tk.Button(self.root, text="Iniciar Jogo", command=self.start_game)
        self.start_button.pack()
        self.baton_button = tk.Button(self.root, text="Passar Bastão", command=self.pass_baton)
        self.baton_button.pack()

    def start_game(self):
        self.info_label.config(text="O jogo começou!")
        self.game.shuffle_and_deal()
        self.update_ui()
        dealer = self.game.get_current_dealer()
        start_message = create_message("START_GAME", dealer, "", "0", "ACK", "O jogo começou!")
        self.network.send_message(start_message)

    def update_ui(self):
        dealer = self.game.get_current_dealer()
        self.info_label.config(text=f"O carteador atual é: {dealer}")
        # Atualiza a interface com as mãos dos jogadores

    def pass_baton(self):
        current_dealer = self.game.get_current_dealer()
        baton_message = create_message("BATON", current_dealer, "", "0", "ACK", "Passando bastão")
        self.network.send_message(baton_message)
        self.game.next_round()
        self.update_ui()

    def run(self):
        self.root.mainloop()
