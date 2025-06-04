from django.db import models
from django.db import connections


# Create your models here.
class Project(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    technology = models.CharField(max_length=20)
    image = models.FilePathField(path="/images")

class Trades(models.Model):
    date = models.DateTimeField()
    symbol = models.CharField(max_length=100)
    id = models.BigIntegerField(primary_key=True)
    orderId = models.BigIntegerField()
    side = models.CharField(max_length=20)
    price = models.FloatField()
    qty = models.FloatField()
    realizedPnl = models.FloatField()
    marginAsset = models.CharField(max_length=20)
    quoteQty = models.FloatField()
    commission = models.FloatField()
    commissionAsset = models.CharField(max_length=20)
    time = models.BigIntegerField()
    positionSide = models.CharField(max_length=20)
    buyer = models.CharField(max_length=20)
    maker = models.CharField(max_length=20)
    class Meta:
        abstract = True  # Make this an abstract base model

class mirrorx1(Trades):
    class Meta:
        db_table = 'mirrorx1'

class mirrorx2(Trades):
    class Meta:
        db_table = 'mirrorx2'

class mirrorx3(Trades):
    class Meta:
        db_table = 'mirrorx3'

class mirrorx4(Trades):
    class Meta:
        db_table = 'mirrorx4'

class mirrorx5(Trades):
    class Meta:
        db_table = 'mirrorx5'
class mirrorxfund(Trades):
    class Meta:
        db_table = 'mirrorxfund'


class Strategies(models.Model):   # Please find a better name for this.
    """
    We create a model for saving and retrieving data
    from our database (MySQL).
    """
    symbol = models.CharField(max_length=100)
    datetime = models.DateTimeField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    class Meta:
        db_table = "stocks"

# model for chart

class ChartData(models.Model):
    label = models.CharField(max_length=255)
    value = models.IntegerField()
    class Meta:
        db_table = "chart"