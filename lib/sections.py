def header():
    html = f'''
        <header>
            <div class="container-xl" style="display: flex; justify-content: space-between;">
                <a href="/">Martin Pellizzer</a>
                <ul>
                    <a href="plants">Plants</a>
                </ul>
            </div>
        </header>
    '''
    return html

def footer():
    html = f'''
        <footer>
            <div class="container-xl" style="display: flex; justify-content: space-between;">
                <span href="/">martinpellizzer.com | all rights reserved</span>
            </div>
        </footer>
    '''
    return html


def breadcrumbs(url):
    breadcrumb_list = url.split('/')
    breadcrumb_href = f'/'
    breadcrumb_html = f'<a href="{breadcrumb_href}">Home</a>'
    for breadcrumb_i, breadcrumb_text in enumerate(breadcrumb_list):
        breadcrumb_href += '/' + breadcrumb_text
        breadcrumb_href = breadcrumb_href.replace('//', '/')
        breadcrumb_text = breadcrumb_text.strip().replace('-', ' ').title()
        if breadcrumb_i == len(breadcrumb_list)-1:
            breadcrumb_html += f' > {breadcrumb_text}'
        else:
            breadcrumb_html += f' > <a href="{breadcrumb_href}.html">{breadcrumb_text}</a>'
    html = f'''
        <section class="breadcrumbs">
            <div class="container-xl">
                {breadcrumb_html}
            </div>
        </section>
    '''
    return html

