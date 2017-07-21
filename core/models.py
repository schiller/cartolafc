from django.db import models


class Clube(models.Model):
    """ Club """
    def __init__(self, id, nome, abreviacao,
                 escudo_30x30="",
                 escudo_45x45="",
                 escudo_60x60=""):
        self.id = id
        self.nome = nome
        self.abreviacao = abreviacao
        self.escudo_30x30 = escudo_30x30
        self.escudo_45x45 = escudo_45x45
        self.escudo_60x60 = escudo_60x60

    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=200)
    abreviacao = models.CharField(max_length=3)
    escudo_30x30 = models.URLField()
    escudo_45x45 = models.URLField()
    escudo_60x60 = models.URLField()


class Partida(models.Model):
    """ Match """
    def __init__(self,
                 clube_casa, clube_visitante,
                 clube_casa_posicao, clube_visitante_posicao,
                 aproveitamento_mandante, aproveitamento_visitante,
                 placar_oficial_mandante, placar_oficial_visitante,
                 partida_data, local, valida, url_confronto):
        self.clube_casa = clube_casa
        self.clube_visitante = clube_visitante
        self.clube_casa_posicao = clube_casa_posicao
        self.clube_visitante_posicao = clube_visitante_posicao
        self.aproveitamento_mandante = aproveitamento_mandante
        self.aproveitamento_visitante = aproveitamento_visitante
        self.placar_oficial_mandante = placar_oficial_mandante
        self.placar_oficial_visitante = placar_oficial_visitante
        self.partida_data = partida_data
        self.local = local
        self.valida = valida
        self.url_confronto = url_confronto

    clube_casa = models.ForeignKey(Clube,
                                   on_delete=models.CASCADE,
                                   related_name='partidas_casa')
    clube_visitante = models.ForeignKey(Clube,
                                        on_delete=models.CASCADE,
                                        related_name='partidas_visitante')
    clube_casa_posicao = models.IntegerField()
    clube_visitante_posicao = models.IntegerField()
    aproveitamento_mandante = models.CharField(max_length=5)
    aproveitamento_visitante = models.CharField(max_length=5)
    placar_oficial_mandante = models.IntegerField()
    placar_oficial_visitante = models.IntegerField()
    partida_data = models.DateTimeField()
    local = models.CharField(max_length=200)
    valida = models.BooleanField()
    url_confronto = models.URLField()
