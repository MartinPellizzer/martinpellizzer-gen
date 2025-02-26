def html_head(title, stylesheet='/style.css'):
    html = f'''
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="{stylesheet}">
            <title>{title}</title>
        </head>
    '''
    return html

def html_header():
    html = f'''
        <header>
            <div class="container-xl flex justify-between">
                <a href="/">Martin Pellizzer</a>
                <nav>
                    <a href="/herbs.html">Herbs</a>
                    <a href="/preparations.html">Preparations</a>
                    <a href="/equipments.html">Equipments</a>
                    <a href="/ailments.html">Ailments</a>
                </nav>
            </div>
        </header>
    '''
    return html

def html_footer():
    html = f'''
        <footer class="container-xl flex justify-between">
            <span>martinpellizzer.com | all rights reserved</span>
            <nav class="flex gap-16">
                <a class="no-underline" href="/">About</a>
                <a class="no-underline" href="/">Contact</a>
            </nav>
        </footer>
    '''
    return html

def toc(html_in):
    html_out = ''
    json_toc = []
    index = 0
    for line in html_in.split('\n'):
        line = line.strip()
        if line.startswith('<h2'):
            json_toc.append({
                'tag': 'h2',
                'index': index,
                'headline': line.split('>')[1].split('<')[0],
            })
            line = (line.replace('<h2', f'<h2 id="{index}"'))
            index +=1
        html_out += line
        html_out += '\n'
    return html_out, json_toc

def toc_json_to_html_article(json_toc):
    html_toc = ''
    html_toc += '<ul>'
    for item_toc in json_toc:
        index = item_toc['index']
        headline = item_toc['headline']
        html_toc += f'<li><a href="#{index}">{headline}</a></li>'
    html_toc += '</ul>'
    return html_toc

def toc_json_to_html_sidebar(json_toc):
    html_toc_list = ''
    html_toc_list += '<ul>'
    for item_toc in json_toc:
        index = item_toc['index']
        headline = item_toc['headline']
        html_toc_list += f'''
            <li><a href="#{index}">{headline}</a></li>
        '''
    html_toc_list += '</ul>'
    html_toc = ''
    html_toc += f'''
        <div class="sidebar-toc">
            <div class="sidebar-toc-header">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
                </svg>
                <p>On this page</p>
            </div>
                {html_toc_list}
            </ul>
        </div>
    '''
    return html_toc

def breadcrumbs(filepath):
    breadcrumbs = ['<a href="/"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6"><path stroke-linecap="round" stroke-linejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25"/></svg></a>']
    breadcrumbs_path = filepath.replace('website/', '')
    chunks = breadcrumbs_path.split('/')
    filepath_curr = ''
    for chunk in chunks[:-1]:
        filepath_curr += f'/{chunk}'
        chunk = chunk.strip().replace('-', ' ').title()
        breadcrumbs.append(f'<a href="{filepath_curr}.html">{chunk}</a>')
    breadcrumbs = '<span> > </span>'.join(breadcrumbs)
    breadcrumbs += f'<span> > {chunks[-1].strip().replace(".html", "").replace("-", " ").title()}</span>'
    breadcrumbs_section = f'''
        <section class="breadcrumbs">
            {breadcrumbs}
        </section>
    '''
    
    return breadcrumbs_section

