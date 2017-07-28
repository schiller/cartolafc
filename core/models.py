from django.db import models


class Clube(models.Model):
    """Club"""
    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=200)
    abreviacao = models.CharField(max_length=3)
    escudo_30x30 = models.URLField()
    escudo_45x45 = models.URLField()
    escudo_60x60 = models.URLField()

    def __str__(self):
        return self.nome


class Partida(models.Model):
    """Match between two Clube instances"""
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


class Atleta(models.Model):
    """Athlete - player or coach"""
    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=200)
    apelido = models.CharField(max_length=200)
    foto = models.URLField()

    def __str__(self):
        return self.apelido


class Posicao(models.Model):
    """Tactical position of an Atleta"""
    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=20)
    abreviacao = models.CharField(max_length=3)

    def __str__(self):
        return self.nome


class Status(models.Model):
    """Probable status of an Atleta for the next round"""
    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Pontuacao(models.Model):
    """Points earned for each scout"""
    abreviacao = models.CharField(max_length=3)
    nome = models.CharField(max_length=200)
    pontuacao = models.IntegerField(default=0)

    def __str__(self):
        return '{}: {}'.format(self.abreviacao, self.pontuacao)


class Scout(models.Model):
    """Set of scouts of an Athete in one match"""
    ano = models.IntegerField()
    rodada = models.IntegerField()
    atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE)
    clube = models.ForeignKey(Clube, on_delete=models.CASCADE)
    posicao = models.ForeignKey(Posicao, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    pontos_num = models.FloatField(default=0)
    preco_num = models.FloatField(default=0)
    variacao_num = models.FloatField(default=0)
    media_num = models.FloatField(default=0)
    jogos_num = models.IntegerField(default=0)
    scouts_FS = models.IntegerField(default=0)
    scouts_PE = models.IntegerField(default=0)
    scouts_A = models.IntegerField(default=0)
    scouts_FT = models.IntegerField(default=0)
    scouts_FD = models.IntegerField(default=0)
    scouts_FF = models.IntegerField(default=0)
    scouts_G = models.IntegerField(default=0)
    scouts_I = models.IntegerField(default=0)
    scouts_PP = models.IntegerField(default=0)
    scouts_RB = models.IntegerField(default=0)
    scouts_FC = models.IntegerField(default=0)
    scouts_GC = models.IntegerField(default=0)
    scouts_CA = models.IntegerField(default=0)
    scouts_CV = models.IntegerField(default=0)
    scouts_SG = models.IntegerField(default=0)
    scouts_DD = models.IntegerField(default=0)
    scouts_DP = models.IntegerField(default=0)
    scouts_GS = models.IntegerField(default=0)

    def __str__(self):
        return '{}-{}: {}'.format(ano, rodada, atleta.apelido)
