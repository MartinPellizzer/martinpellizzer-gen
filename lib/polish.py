def sanitize(text):
    text = text.replace('-', '-')
    return text

def format_1N1(text_raw):
    text_raw = text_raw.replace('*', '')
    text_formatted = ''
    ### split sentences
    import nltk.data
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    sentence_list = tokenizer.tokenize(text_raw)
    ### format 1N1
    paragraph_list = []
    if len(sentence_list) > 3:
        paragraph_list.append(sentence_list[0])
        paragraph_list.append(' '.join(sentence_list[1:-1]))
        paragraph_list.append(sentence_list[-1])
    else:
        paragraph_list = sentence_list
    ### generate html
    for paragraph in paragraph_list:
        text_formatted += f'<p>{paragraph}</p>'
    return text_formatted
