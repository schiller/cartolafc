from django.db import models


class Clube(models.Model):
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
    escudo_30x30 = models.CharField(max_length=200, default="")
    escudo_45x45 = models.CharField(max_length=200, default="")
    escudo_60x60 = models.CharField(max_length=200, default="")
