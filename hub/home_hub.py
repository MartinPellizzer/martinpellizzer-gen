from lib import g
from lib import media
from lib import sections

def main():
    if 0:
        prompt = f'''
            plants and flowers, outdoor, scenic view, soft focus, bokeh, depth of field, high resolution
        '''
        image = media.image_gen(prompt, 1216, 832, steps=20, cfg=6)
        image.save('test.jpg')
        quit()

    hero = f'''
        <section style="
                background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), 
                    url('/images/plants.jpg');
                background-size: cover;
                background-position: center;
                padding-top: 8rem;
                padding-bottom: 8rem;
                display: flex;
                flex-direction: column;
                align-items: center;
        ">
            <div class="container-lg">
                <h1 style="font-size: 4rem; line-height: 1; text-align: center; color: #ffffff;">
                    Discover Beautiful Plants Around The World
                </h1>
            </div>
        </section>
    '''
    html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            {sections.header()}
            <main>
                {hero}
            </main>
            {sections.footer()}
        </body>
        </html>
    '''
    with open(f'{g.website_folderpath}/index.html', 'w') as f: f.write(html)

