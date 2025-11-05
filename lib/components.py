from lib import g

def html_head(meta_title, meta_description, form_head=''):
    # with open(g.GOOGLE_ADSENSE_SCRIPT) as f: google_adsense_script = f.read()
    # with open(g.GOOGLE_ANALYTICS_SCRIPT) as f: google_analytics_script = f.read()
    html = f'''
        <head>
            <meta name="viewport" content="width=device-width, inital-scale=1">
            <link rel="stylesheet" href="/style.css">
            {form_head}
        </head>
    '''
            # {google_adsense_script}
            # {google_analytics_script}
    return html

