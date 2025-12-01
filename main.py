import shutil
import markdown

from lib import g

shutil.copy2(f'style.css', f'{g.website_folderpath}/style.css')

if 0:
    from ai import plants_ai
    plants_ai.main()
    # quit()

if 1:
    from hub import art_hub
    art_hub.main()
    # quit()

from hub import home_hub
home_hub.main()

