from lib import g
from lib import io

def plants_wcvp_get():
    plants_0000 = io.csv_to_dict(f'{g.VAULT_TMP}/terrawhisper/wcvp_taxon.csv', delimiter = '|')
    ###
    plants = []
    for plant in plants_0000: plants.append(plant['scientfiicname'].strip().lower())
    plants = list(set(plants))
    plants = sorted(plants)
    return plants
