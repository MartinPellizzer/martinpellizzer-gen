import shutil
import markdown

from lib import g
from lib import media
from lib import sections

shutil.copy2(f'style.css', f'{g.website_folderpath}/style.css')

########################################
# CSV............................[CSV]
########################################
if 1:
    from hub import hub_csv
    hub_csv.gen()

html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <link rel="stylesheet" href="/style.css">
    </head>
    <body>
        {sections.header()}
        <main>
            <div class="article container-md">
            </div>
        </main>
        {sections.footer()}
    </body>
    </html>
'''
with open(f'{g.website_folderpath}/index.html', 'w') as f: f.write(html)

