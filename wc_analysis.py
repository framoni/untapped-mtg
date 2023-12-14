import json
from PIL import Image
from sklearn.cluster import KMeans


def flatten_wc(wc):
    wc_list = []
    for deck in wc:
        temp = []
        for item in wc[deck]:
            temp += [item['name']] * item['quantity']
        wc_list.append(temp)
    return wc_list


def merge_pics(pic_list, label):
    pics = [Image.open(p) for p in pic_list]
    min_img_width = min(p.width for p in pics)
    total_height = 0
    for it, p in enumerate(pics):
        if p.width > min_img_width:
            pics[it] = p.resize((min_img_width, int(p.height / p.width * min_img_width)), Image.ANTIALIAS)
        total_height += pics[it].height
    pic_merge = Image.new(pics[0].mode, (min_img_width, total_height))
    y = 0
    for p in pics:
        pic_merge.paste(p, (0, y))
        y += p.height
    pic_merge.save('groups/{}.png'.format(label))


def cluster_decks(list_of_lists, deck_titles):
    import itertools
    import numpy as np
    unique = list(set(list(itertools.chain.from_iterable(list_of_lists))))
    vectors = []
    for sublist in list_of_lists:
        v = np.zeros(len(unique))
        for item in sublist:
            idx = unique.index(item)
            v[idx] += 1
        vectors.append(v)
    km = KMeans(n_clusters=5)
    labels = km.fit_predict(vectors)
    for i in range(5):
        idx = np.where(labels == i)[0]
        pic_list = ['pics/{}.png'.format(deck_titles[j]) for j in idx]
        merge_pics(pic_list, i)


def main():
    with open('mtga_standard_wc.json', 'r') as f:
        wc = json.loads(f.read())
    wc_list = flatten_wc(wc)
    cluster_decks(wc_list, list(wc.keys()))


if __name__ == "__main__":
    main()
