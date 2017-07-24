from django.db import models


class Clube(models.Model):
    """ Club """
    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=200)
    abreviacao = models.CharField(max_length=3)
    escudo_30x30 = models.URLField()
    escudo_45x45 = models.URLField()
    escudo_60x60 = models.URLField()

    def __str__(self):
        return self.nome


class Partida(models.Model):
    """ Match """
    clube_casa = models.ForeignKey(
        Clube, on_delete=models.CASCADE, related_name='partidas_casa')
    clube_visitante = models.ForeignKey(
        Clube, on_delete=models.CASCADE, related_name='partidas_visitante')
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
    rodada = models.IntegerField()

    def __str__(self):
        return '{} x {}, {}'.format(self.clube_casa,
                                    self.clube_visitante,
                                    self.partida_data)
