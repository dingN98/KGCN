import getKG
import json
import numpy as np
import time


def get_train_data():
    movie_id_dict, genre_dict, director_dict, star_dict = getKG.get_entity_dict(False)

    ratings_json_path = "../fullData/ratings.json"

    threshold = 4

    user_pos_ratings = {}
    user_neg_ratings = {}

    # 读取正负样本  这里的 用户id  和 电影id  都是老的
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    print("根据 ratings.json 构建正负样本 ...")
    with open(ratings_json_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip("\n")
            data = json.loads(line)

            movie_id = data["item_id"]
            user_id = data["user_id"]
            rating = data["rating"]

            # 如果电影不在 movie_id_dict 里，直接忽略
            if movie_id not in movie_id_dict:
                continue

            if rating >= threshold:
                if user_id not in user_pos_ratings:
                    user_pos_ratings[user_id] = set()
                user_pos_ratings[user_id].add(movie_id)
            else:
                if user_id not in user_neg_ratings:
                    user_neg_ratings[user_id] = set()
                user_neg_ratings[user_id].add(movie_id)

    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    print("构建数据集 ratings_final.txt ...")
    item_set = set(movie_id_dict.keys())
    writer = open('../data/movie/ratings_final.txt', 'w', encoding='utf-8')
    user_cnt = 0
    user_index_old2new = dict()
    for user_index_old, pos_item_set in user_pos_ratings.items():
        if user_index_old not in user_index_old2new:
            user_index_old2new[user_index_old] = user_cnt
            user_cnt += 1
        user_index = user_index_old2new[user_index_old]

        for item in pos_item_set:
            writer.write('%d\t%d\t1\n' % (user_index, movie_id_dict[item]))
        unwatched_set = item_set - pos_item_set
        if user_index_old in user_neg_ratings:
            unwatched_set -= user_neg_ratings[user_index_old]
        for item in np.random.choice(list(unwatched_set), size=len(pos_item_set), replace=False):
            writer.write('%d\t%d\t0\n' % (user_index, movie_id_dict[item]))
    writer.close()
    print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
    print('number of users: %d' % user_cnt)
    print('number of items: %d' % len(item_set))


if __name__ == '__main__':
    get_train_data()
