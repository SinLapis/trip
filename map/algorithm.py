from operator import itemgetter

from django.contrib.gis.geos import Point
from .models import Attraction, Tag, Tag_Map, Tag_Class_Map
from math import sqrt

INSIDE_CIRCLE = 0.0088960
OUTSIDE_CIRCLE = 0.0133439

tag_count = {}


def tag_count_init():
    results = Tag.objects.all()
    for result in results:
        tag_count[result.tag_name] = 0


def find_tag(attraction):
    return Tag_Map.objects.filter(attraction_id=attraction.id)[0].tag_id


def find_tag_class(tag):
    return Tag_Class_Map.objects.filter(tag_id=tag.id)[0].class_id


def get_distance_matrix(recommends):
    distance_matrix = []
    for i in range(0, len(recommends)):
        distance_list = []
        for j in range(0, len(recommends)):
            distance = sqrt(
                (recommends[i]['attraction'].point.x -
                 recommends[j]['attraction'].point.x) ** 2 +
                (recommends[i]['attraction'].point.y -
                 recommends[j]['attraction'].point.y) ** 2
            )
            distance_list.append(distance)
        distance_matrix.append(distance_list)
    print(distance_matrix)
    return distance_matrix


def score_delete_recommends(recommends, days):
    decrease_recommends = recommends
    for recommend in decrease_recommends:
        delete_score = 0.0
        if not recommend['fit-select-theme']:
            delete_score += 3.0
        if not recommend['is-inside']:
            delete_score += 5.0
        if not recommend['fit-most-theme']:
            delete_score += 2.0
        if not recommend['above-mid-rank']:
            delete_score += 1.0
        delete_score += (recommend['rank'] / 1000.0)
        recommend['delete-score'] = delete_score
    sorted(decrease_recommends, key=itemgetter('delete-score'))
    count = days * 3
    while len(decrease_recommends) >= count:
        decrease_recommends.pop(0)

    return decrease_recommends


def add_attraction(recommends):
    pass


def offset_match(points, tag_classes):
    tag_count_init()
    recommends = []
    for point in points:
        inside_results = Attraction.objects.filter(point__dwithin=(
            Point(float(point['lat']), float(point['lng']), srid=4326), INSIDE_CIRCLE
        ))
        outside_results = Attraction.objects.filter(point__dwithin=(
            Point(float(point['lat']), float(point['lng']), srid=4326), OUTSIDE_CIRCLE
        ))
        # 内圈
        inside_ids = []
        for result in inside_results:
            fit_select_theme = False
            attraction_tag = find_tag(result)
            for content_class in tag_classes:
                if content_class.id == find_tag_class(attraction_tag).id:
                    fit_select_theme = True
                    break
            recommend = {
                'attraction': result,
                'is-inside': True,
                'fit-select-theme': fit_select_theme,
                'tag': attraction_tag,
                'fit-most-theme': False,
                'rank': result.rank,
            }
            tag_count[attraction_tag.tag_name] += 1
            inside_ids.append(recommend['attraction'].id)
            recommends.append(recommend)
        # 外圈
        for result in outside_results:
            if result.id not in inside_ids:
                fit_select_theme = False
                attraction_tag = find_tag(result)
                for content_class in tag_classes:
                    if content_class.id == find_tag_class(attraction_tag).id:
                        fit_select_theme = True
                        break
                recommend = {
                    'attraction': result,
                    'is-inside': False,
                    'fit-select-theme': fit_select_theme,
                    'tag': attraction_tag,
                    'fit-most-theme': False,
                    'rank': result.rank,
                }
                tag_count[attraction_tag.tag_name] += 1
                recommends.append(recommend)

    most_theme = max(tag_count, key=tag_count.get)
    sorted(recommends, key=itemgetter('rank'))
    mid_rank = recommends[int((len(recommends) / 2))]['rank']
    for i in range(len(recommends)):
        if recommends[i]['tag'].tag_name == most_theme:
            recommends[i]['fit-most-theme'] = True
        if recommends[i]['rank'] >= mid_rank:
            recommends[i]['above-mid-rank'] = True
        else:
            recommends[i]['above-mid-rank'] = False

    return recommends

def greedy_algorithm_one(recommends, distance_matrix, start_index):
    plan = [start_index]
    while len(plan) < len(recommends):
        min_distance = 10
        min_index = len(recommends)
        for i in range(0, distance_matrix[plan[-1]]):
            if i not in plan and distance_matrix[plan[-1]][i] < min_distance:
                min_distance = distance_matrix[plan[-1]][i]
                min_index = i
        plan.append(min_index)
    return plan


def greedy_algorithm_all(recommends, distance_matrix):
    plans = []


