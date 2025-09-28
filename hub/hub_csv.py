from lib import g
from lib import io
from lib import article

def gen():
    articles_data = io.csv_to_dict('articles.csv', delimiter='\\')
    for article_data in articles_data:
        print(f'''ARTICLE: {article_data['article_slug']}''')
        article_obj = {
            'article_slug': article_data['article_slug'],
            'article_type': article_data['article_type'],
            'keyword_main': article_data['keyword_main'],
            'keyword_main_slug': article_data['keyword_main_slug'],
            'keyword_main_pretty': article_data['keyword_main_pretty'],
            'keyword_main_title': article_data['keyword_main_title'],
            'pin_board_name': article_data['pin_board_name'],
            'main_list_num': '10',
            'images_prompts': [article_data['images_prompts']],
            'links': [],
        }
        regen = article_data['regen']
        regen_json = article_data['regen_json']
        dispel = article_data['dispel']
        if regen == '': regen = False
        elif regen == '0': regen = False
        else: regen = True
        if dispel == '': dispel = False
        elif dispel == '0': dispel = False
        else: dispel = True
        if regen_json == '': regen_json = False
        elif regen_json == '0': regen_json = False
        else: regen_json = True
        article.images_gen(article_obj, regen=regen, dispel=dispel)
        article.json_gen(article_obj, regen=regen_json, dispel=dispel)
        article.html_gen(article_data['article_slug'], article_obj)

