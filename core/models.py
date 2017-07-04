from django.db import models


class Clube(models.Model):
    def __init__(self, id, nome, abreviacao):
        self.id = id
        self.nome = nome
        self.abreviacao = abreviacao

    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=200)
    abreviacao = models.CharField(max_length=3)
