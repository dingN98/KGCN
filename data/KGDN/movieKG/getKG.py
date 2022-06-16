import json
import pandas as pd

metadata_json_path = '../fullData/metadata.json'
movies_csv_path = '../fullData/movies.csv'


def get_metadata_line(line):
    line = line.strip("\n")
    data = json.loads(line)

    movie_id = data["item_id"]
    # movie_name = data["title"]
    directors = data["directedBy"]
    if directors == "":
        directors = []
    else:
        directors = directors.split(",")
        directors = [i.strip() for i in directors]

    stars = data["starring"]
    if stars == "":
        stars = []
    else:
        stars = stars.split(",")
    stars = [i.strip() for i in stars]
    return movie_id, directors, stars


def get_movies_directors_stars():
    movie_list = []
    director_list = []
    star_list = []
    with open(metadata_json_path, 'r', encoding='utf-8') as f:
        for line in f:
            movie_id, directors, stars = get_metadata_line(line)

            if len(directors) > 0 or len(stars) > 0:
                # 先加入list 再做去重
                movie_list.append(movie_id)

            for director in directors:
                if director != "":
                    director_list.append(director)
            for star in stars:
                if star != "":
                    star_list.append(star)

    director_list = list(set(director_list))
    star_list = list(set(star_list))

    return movie_list, director_list, star_list


def get_genres():
    genre_list = []
    csv_result = pd.read_csv(movies_csv_path, encoding='utf-8')
    row_list = csv_result.values.tolist()

    for line in row_list:
        genres = line[2].split('|')
        genres = [i.strip() for i in genres]

        for genre in genres:
            genre_list.append(genre)

    genre_list = list(set(genre_list))
    return genre_list


def get_entity_dict(save):
    entity_id = 0
    movie_id_dict = {}
    genre_dict = {}
    director_dict = {}
    star_dict = {}

    movie_list, director_list, star_list = get_movies_directors_stars()
    genre_list = get_genres()

    print("电影 %s" % (len(movie_list)))
    print("类别 %s" % (len(genre_list)))
    print("导演 %s" % (len(director_list)))
    print("明星 %s" % (len(star_list)))

    for i in movie_list:
        movie_id_dict[i] = entity_id
        entity_id = entity_id + 1

    for i in genre_list:
        genre_dict[i] = entity_id
        entity_id = entity_id + 1

    for i in director_list:
        director_dict[i] = entity_id
        entity_id = entity_id + 1

    for i in star_list:
        star_dict[i] = entity_id
        entity_id = entity_id + 1

    if save:
        # 保存实体的映射关系
        file_goal_path = '../data/movie/movie_id_dict.txt'
        with open(file_goal_path, 'w', encoding='utf-8') as file_goal:
            # file_goal.write("movieId,entityId\n")
            for key in movie_id_dict:
                file_goal.write("%s\t%s\n" % (key, movie_id_dict[key]))

        file_goal_path = '../data/movie/genre_dict.txt'
        with open(file_goal_path, 'w', encoding='utf-8') as file_goal:
            # file_goal.write("genreName,entityId\n")
            for key in genre_dict:
                file_goal.write("%s\t%s\n" % (key, genre_dict[key]))

        file_goal_path = '../data/movie/director_dict.txt'
        with open(file_goal_path, 'w', encoding='utf-8') as file_goal:
            # file_goal.write("directorName,entityId\n")
            for key in director_dict:
                file_goal.write("%s\t%s\n" % (key, director_dict[key]))

        file_goal_path = '../data/movie/star_dict.txt'
        with open(file_goal_path, 'w', encoding='utf-8') as file_goal:
            # file_goal.write("starName,entityId\n")
            for key in star_dict:
                file_goal.write("%s\t%s\n" % (key, star_dict[key]))

        file_goal.close()

    return movie_id_dict, genre_dict, director_dict, star_dict


def get_kg():
    # 构建关系
    relation_dict = {"star": 0, "director": 1, "genre": 2}
    relation_list = []

    movie_id_dict, genre_dict, director_dict, star_dict = get_entity_dict(True)

    with open(metadata_json_path, 'r', encoding='utf-8') as f:
        for line in f:
            movie_id, directors, stars = get_metadata_line(line)
            if movie_id not in movie_id_dict:
                continue
            movie_id_new = movie_id_dict[movie_id]
            for director in directors:
                if director in director_dict:
                    relation_list.append((movie_id_new, relation_dict["director"], director_dict[director]))
            for star in stars:
                if star in star_dict:
                    relation_list.append((movie_id_new, relation_dict["star"], star_dict[star]))

    csv_result = pd.read_csv(movies_csv_path, encoding='utf-8')
    row_list = csv_result.values.tolist()

    for line in row_list:
        movie_id = line[0]
        genres = line[2].split('|')
        genres = [i.strip() for i in genres]

        if movie_id not in movie_id_dict:
            continue
        movie_id_new = movie_id_dict[movie_id]

        for genre in genres:
            # movies.csv 和 metadata.json 的电影不是完全一致的
            relation_list.append((movie_id_new, relation_dict["genre"], genre_dict[genre]))

    print("关系 %s" % (len(relation_list)))

    # 保存实体的关系
    file_goal_path = '../data/movie/kg_final.txt'
    with open(file_goal_path, 'w', encoding='utf-8') as file_goal:
        # file_goal.write("entityId,relation,entityId\n")
        for line in relation_list:
            file_goal.write("%s\t%s\t%s\n" % (line[0], line[1], line[2]))


if __name__ == '__main__':
    get_kg()
