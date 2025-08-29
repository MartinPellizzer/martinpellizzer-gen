from lib import g
from lib import io

flowers_data = [
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

def plants_wcvp_get():
    plants = io.csv_to_dict(f'{g.terrawhisper_database_folderpath}/csv/wcvp/wcvp_names.csv', '|')
    plants_new = []
    for plant in plants:
        plant_name_scientific = f'''{plant['taxon_name']}'''.strip().lower()
        plants_new.append(plant)
    plants_new = sorted(plants_new, key=lambda x: x['taxon_name'], reverse=False)
    return plants_new

def plants_wcvp_get_old():
    plants_0000 = io.csv_to_dict(f'{g.VAULT_TMP}/terrawhisper/wcvp_taxon.csv', delimiter = '|')
    ###
    plants = []
    for plant in plants_0000: plants.append(plant['scientfiicname'].strip().lower())
    plants = list(set(plants))
    plants = sorted(plants)
    return plants

