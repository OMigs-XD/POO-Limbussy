import random

from flask import Flask, render_template, request, jsonify


# ----------------------------------------------------------------------
# CLASSE 1: Personagem
# Guarda os dados de cada lutador (nome, logo, sprites...).
# ----------------------------------------------------------------------
class Personagem:
    def __init__(self, jogada, associacao, nome, logo, sprites, altura_morte=None):
        self.jogada = jogada              # "pedra", "papel" ou "tesoura"
        self.associacao = associacao
        self.nome = nome
        self.logo = logo
        self.sprites = sprites            # dicionário: estado -> caminho da imagem
        self.altura_morte = altura_morte  # altura (px) do sprite de morte na tela

    def para_dict(self):
        """Converte o personagem para um dicionário (o Flask transforma em JSON)."""
        return {
            "association": self.associacao,
            "character": self.nome,
            "logo": self.logo,
            "sprites": self.sprites,
            "death_height": self.altura_morte,
        }


# ----------------------------------------------------------------------
# CLASSE 2: Placar
# Cuida só dos pontos e de saber quem venceu a partida.
# ----------------------------------------------------------------------
class Placar:
    PONTOS_PARA_VENCER = 5

    def __init__(self):
        self.player = 0
        self.maquina = 0

    def somar_ponto(self, quem):
        if quem == "player":
            self.player += 1
        elif quem == "machine":
            self.maquina += 1

    def vencedor(self):
        """Retorna 'player', 'machine' ou None (se ninguém chegou nos pontos)."""
        if self.player >= self.PONTOS_PARA_VENCER:
            return "player"
        if self.maquina >= self.PONTOS_PARA_VENCER:
            return "machine"
        return None

    def resetar(self):
        self.player = 0
        self.maquina = 0

    def para_dict(self):
        return {"player": self.player, "machine": self.maquina}


# ----------------------------------------------------------------------
# CLASSE 3: Jogo
# Junta tudo: regras, personagens e placar. É o "cérebro" do jogo.
# ----------------------------------------------------------------------
class Jogo:
    OPCOES = ("pedra", "papel", "tesoura")

    # chave vence o valor: papel vence pedra, pedra vence tesoura...
    VENCE_DE = {
        "papel": "pedra",
        "pedra": "tesoura",
        "tesoura": "papel",
    }

    def __init__(self):
        self.placar = Placar()
        self.personagens = self._criar_personagens()

    def _criar_personagens(self):
        return {
            "pedra": Personagem(
                jogada="pedra",
                associacao="ZWEI",
                nome="Ishmael",
                logo="/static/assets/1200px-Zwei_Logo.webp",
                sprites={
                    "standing": "/static/assets/79px-Zwei_Assoc._West_Section_3_Ishmael_Idle_Sprite.webp",
                    "moving": "/static/assets/120px-Zwei_Assoc._West_Section_3_Ishmael_Moving_Sprite.webp",
                    "defending": "/static/assets/120px-Zwei_Assoc._West_Section_3_Ishmael_Guard_Sprite_2.webp",
                    "death": "/static/assets/Ishamel_death_sprite.png",
                },
                altura_morte=150,
            ),
            "papel": Personagem(
                jogada="papel",
                associacao="SEVEN",
                nome="Heathcliff",
                logo="/static/assets/Seven_Logo.webp",
                sprites={
                    "standing": "/static/assets/77px-Seven_Assoc._South_Section_4_Heathcliff_Idle_Sprite.webp",
                    "moving": "/static/assets/120px-Seven_Assoc._South_Section_4_Heathcliff_Moving_Sprite.webp",
                    "defending": "/static/assets/120px-Seven_Assoc._South_Section_4_Heathcliff_Guard_Sprite.webp",
                    "death": "/static/assets/LCB_Sinner_Heathcliff_Dead_Sprite.webp",
                },
                altura_morte=170,
            ),
            "tesoura": Personagem(
                jogada="tesoura",
                associacao="SHI",
                nome="Don Quixote",
                logo="/static/assets/Shi_Logo.webp",
                sprites={
                    "standing": "/static/assets/59px-Shi_Assoc._South_Section_5_Director_Don_Quixote_Idle_Sprite.webp",
                    "moving": "/static/assets/120px-Shi_Assoc._South_Section_5_Director_Don_Quixote_Moving_Sprite.webp",
                    "defending": "/static/assets/107px-Shi_Assoc._South_Section_5_Director_Don_Quixote_Guard_Sprite.webp",
                    "death": "/static/assets/don-quixote-death.png",
                },
                altura_morte=225,
            ),
        }

    def personagens_dict(self):
        return {jogada: p.para_dict() for jogada, p in self.personagens.items()}

    def opcao_valida(self, escolha):
        return escolha in self.OPCOES

    def decidir_rodada(self, player, maquina):
        """Compara as jogadas e devolve 'draw', 'player' ou 'machine'."""
        if player == maquina:
            return "draw"
        if self.VENCE_DE[player] == maquina:
            return "player"
        return "machine"

    def jogar(self, escolha_player):
        """Executa uma rodada completa e devolve o resultado em dicionário."""
        maquina = random.choice(self.OPCOES)
        resultado = self.decidir_rodada(escolha_player, maquina)
        self.placar.somar_ponto(resultado)  # em empate, nada é somado

        vencedor = self.placar.vencedor()

        print("Jogador usou:", escolha_player)
        print("Maquina usou:", maquina)
        print("Resultado:", resultado)

        return {
            "ok": True,
            "player": escolha_player,
            "machine": maquina,
            "result": resultado,
            "winner": vencedor,
            "game_over": vencedor is not None,
            "scores": self.placar.para_dict(),
            "characters": {
                "player": self.personagens[escolha_player].para_dict(),
                "machine": self.personagens[maquina].para_dict(),
            },
        }

    def resetar(self):
        self.placar.resetar()


# ----------------------------------------------------------------------
# FLASK: rotas (usam o objeto `jogo` criado abaixo)
# ----------------------------------------------------------------------
app = Flask(__name__)
jogo = Jogo()


@app.route("/")
def inicio():
    return render_template(
        "index.html",
        characters=jogo.personagens_dict(),
        player_score=jogo.placar.player,
        machine_score=jogo.placar.maquina,
    )


@app.post("/api/play")
def jogar():
    dados = request.get_json(silent=True) or {}
    escolha = str(dados.get("choice", "")).lower()

    if not jogo.opcao_valida(escolha):
        return jsonify({"ok": False, "error": "Escolha pedra, papel ou tesoura!"}), 400

    return jsonify(jogo.jogar(escolha))


@app.post("/api/reset")
def resetar():
    jogo.resetar()
    return jsonify({"ok": True, "scores": jogo.placar.para_dict()})


if __name__ == "__main__":
    app.run(debug=True)
