from django.contrib.gis.db import models


class Attraction(models.Model):
    point = models.PointField()
    name = models.CharField(max_length=50)
    introduction = models.TextField()
    rank = models.IntegerField(default=101)


class Tag(models.Model):
    tag_name = models.CharField(max_length=50)


class Tag_Map(models.Model):
    attraction_id = models.ForeignKey(Attraction)
    tag_id = models.ForeignKey(Tag)


class Picture(models.Model):
    pic_path = models.CharField(max_length=100)
    attraction_id = models.ForeignKey(Attraction)


class Route(models.Model):
    route_name = models.CharField(max_length=40)


class Route_Map(models.Model):
    attraction_num = models.IntegerField(default=0)
    attraction_id = models.ForeignKey(Attraction)
    route_id = models.ForeignKey(Route)
