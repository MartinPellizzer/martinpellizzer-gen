from lib import article

def article_house_garden_design_gen():
    article_slug = f'''plants/house/garden/design'''
    print(f'ARTICLE: {article_slug}')
    article_obj = {
        'article_slug': article_slug,
        'keyword_main': 'garden design',
        'keyword_main_slug': 'garden-design',
        'keyword_main_pretty': 'garden designs',
        'main_list_num': '10',
        'article_type': 'listicle',
        'images_prompts': ['garden design, bokeh, depth of field, high resolution'],
        'links': [],
    }
    article.images_gen(article_obj, regen=False, dispel=False)
    article.json_gen(article_obj, regen=True, dispel=False)
    article.html_gen(article_slug)

def article_house_garden_gen():
    article_slug = f'''plants/house/garden'''
    print(f'ARTICLE: {article_slug}')
    article_house_garden_design_gen()

def article_house_gen():
    article_slug = f'''plants/house'''
    print(f'ARTICLE: {article_slug}')
    article_house_garden_gen()

def gen():
    print(f'HUB: house')
    article_house_gen()
