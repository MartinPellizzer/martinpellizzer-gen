import shutil
import markdown

from lib import g
from lib import media
from lib import sections

# from lib import art_plants

# art_plants.gen()

if 1:
    data = [
        {
            'flower_slug_singular': 'tulip',
            'flower_slug_plural': 'tulips',
            'flower_name_singular': 'tulip',
            'flower_name_plural': 'tulips',
        },
        {
            'flower_slug_singular': 'sunflower',
            'flower_slug_plural': 'sunflowers',
            'flower_name_singular': 'sunflower',
            'flower_name_plural': 'sunflowers',
        },
        {
            'flower_slug_singular': 'rose',
            'flower_slug_plural': 'roses',
            'flower_name_singular': 'rose',
            'flower_name_plural': 'roses',
        },
        {
            'flower_slug_singular': 'cherry-blossom',
            'flower_slug_plural': 'cherry-blossoms',
            'flower_name_singular': 'cherry blossom',
            'flower_name_plural': 'cherry blossoms',
        },
        {
            'flower_slug_singular': 'lily',
            'flower_slug_plural': 'lilies',
            'flower_name_singular': 'lily',
            'flower_name_plural': 'lilies',
        },
        {
            'flower_slug_singular': 'lavender',
            'flower_slug_plural': 'lavenders',
            'flower_name_singular': 'lavender',
            'flower_name_plural': 'lavenders',
        },
        {
            'flower_slug_singular': 'daisy',
            'flower_slug_plural': 'daisies',
            'flower_name_singular': 'daisy',
            'flower_name_plural': 'daisies',
        },
        {
            'flower_slug_singular': 'peony',
            'flower_slug_plural': 'peonies',
            'flower_name_singular': 'peony',
            'flower_name_plural': 'peonies',
        },
        {
            'flower_slug_singular': 'hydrangea',
            'flower_slug_plural': 'hydrangeas',
            'flower_name_singular': 'hydrangea',
            'flower_name_plural': 'hydrangeas',
        },
        {
            'flower_slug_singular': 'jasmine',
            'flower_slug_plural': 'jasmines',
            'flower_name_singular': 'jasmine',
            'flower_name_plural': 'jasmines',
        },
        {
            'flower_slug_singular': 'lotus',
            'flower_slug_plural': 'lotuses',
            'flower_name_singular': 'lotus',
            'flower_name_plural': 'lotuses',
        },
        {
            'flower_slug_singular': 'hibiscus',
            'flower_slug_plural': 'hibiscuses',
            'flower_name_singular': 'hibiscus',
            'flower_name_plural': 'hibiscuses',
        },
        {
            'flower_slug_singular': 'carnation',
            'flower_slug_plural': 'carnations',
            'flower_name_singular': 'carnation',
            'flower_name_plural': 'carnations',
        },
        {
            'flower_slug_singular': 'sakura',
            'flower_slug_plural': 'sakuras',
            'flower_name_singular': 'sakura',
            'flower_name_plural': 'sakuras',
        },
        {
            'flower_slug_singular': 'poppy',
            'flower_slug_plural': 'poppies',
            'flower_name_singular': 'poppy',
            'flower_name_plural': 'poppies',
        },
        {
            'flower_slug_singular': 'dahlia',
            'flower_slug_plural': 'dahlias',
            'flower_name_singular': 'dahlia',
            'flower_name_plural': 'dahlias',
        },
        {
            'flower_slug_singular': 'cosmos',
            'flower_slug_plural': 'cosmoses',
            'flower_name_singular': 'cosmos',
            'flower_name_plural': 'cosmoses',
        },
    ]
    # from lib import art_plants_types_flowers_sunflowers_aesthetic
    # art_plants_types_flowers_sunflowers_aesthetic.gen()
    # from lib import art_plants_types_flowers_tulips_aesthetic
    # art_plants_types_flowers_tulips_aesthetic.gen()
    from lib import art_plants_types_flowers_var_aesthetic
    for item in data:
        art_plants_types_flowers_var_aesthetic.gen(item)

shutil.copy2(f'style.css', f'{g.website_folderpath}/style.css')

quit()


def image_ai():
    prompt = f'''
        plants,
        living room,
        indoor, interior design,
        minimalist, cozy atmosphere,
        bokeh,
        photography,
        high resolution,
    '''.replace('  ', ' ')
    image = media.image_gen(prompt, 832, 1216)
    image.save(f'{g.database_folderpath}/markdown/plants/indoor/indoor-plants-best.jpg')
    ###
    prompt = f'''
        plants,
        living room,
        indoor, interior design,
        minimalist, cozy atmosphere,
        bokeh,
        photography,
        high resolution,
    '''.replace('  ', ' ')
    image = media.image_gen(prompt, 832, 1216)
    image.save(f'{g.database_folderpath}/markdown/plants/indoor/indoor-plant-right.jpg')
    quit()
    with open(f'{g.database_folderpath}/markdown/plants/indoor/best-list.md') as f: 
        plants = [line.strip() for line in f.read().split('\n') if line.strip() != '']
    for plant_i, plant in enumerate(plants):
        print(f'{plant_i}/{len(plants)} - {plant}')
        plant_slug = plant.strip().lower().replace(' ', '-')
        prompt = f'''
            {plant}, plants,
            living room,
            indoor, interior design,
            minimalist, cozy atmosphere,
            bokeh,
            photography,
            high resolution,
        '''.replace('  ', ' ')
        # image = media.image_gen(prompt, 1024, 1024)
        image = media.image_gen(prompt, 832, 1216)
        # image = media.resize(image, 768, 768)
        # image.show()
        image.save(f'{g.database_folderpath}/markdown/plants/indoor/{plant_i}-{plant_slug}.jpg')
        # quit()

# image_ai()
# quit()

def html_article(article_slug):
    with open(f'{g.database_folderpath}/markdown/{article_slug}.md', encoding='utf-8') as f: 
        markdown_content = f.read()
    markdown_formatted = ''
    line_prev = ''
    for line in markdown_content.split('\n'):
        if line_prev == '':
            markdown_formatted += '\n'
            markdown_formatted += line
            markdown_formatted += '\n'
        elif line_prev.startswith('-'): 
            markdown_formatted += line
            markdown_formatted += '\n'
        elif line_prev[0].isdigit(): 
            markdown_formatted += line
            markdown_formatted += '\n'
        elif line_prev.startswith('|'): 
            markdown_formatted += line
            markdown_formatted += '\n'
        else:
            markdown_formatted += '\n'
            markdown_formatted += line
            markdown_formatted += '\n'
        line_prev = line
        
    print(markdown_formatted)
    html_article = markdown.markdown(markdown_formatted, extensions=['markdown.extensions.tables'])
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <header>
                <div class="container-xl" style="display: flex; justify-content: space-between;">
                    <a href="/">Martin Pellizzer</a>
                    <ul>
                        <a href="plants">Plants</a>
                    </ul>
                </div>
            </header>
            <main>
                {sections.breadcrumbs(article_slug)}
                <div class="article container-md">
                    {html_article}
                </div>
            </main>
            <footer>
                <div class="container-xl" style="display: flex; justify-content: space-between;">
                    <span href="/">martinpellizzer.com | all rights reserved</span>
                </div>
            </footer>
        </body>
        </html>
    '''
    with open(f'{g.website_folderpath}/{article_slug}.html', 'w') as f: f.write(html)

html_article(f'plants/types/flowers/tulips/wallpapers')

