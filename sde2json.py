# v1.0.1
import os
import time
import json
import copy
import zipfile
import urllib.error
import urllib.request
import urllib.parse
from collections import OrderedDict

# pip install -r requirements.txt
import yaml
from bs4 import BeautifulSoup

LANGUAGES = [
    'de',
    'en',
    'fr',
    'ja',
    'ru',
    'zh',
]

TYPES_JSON_PATH = os.path.join('.', 'types.json')

UNIVERSES_JSON_PATH = os.path.join('.', 'universes.json')
UNIVERSE_IDS = OrderedDict(
    eve=1,
    wormhole=2,
    abyssal=3,
    penalty=4,
)
DEFAULT_UNIVERSES = OrderedDict()
DEFAULT_UNIVERSES['1'] = OrderedDict(
    name='eve',
    de='eve',
    en='eve',
    fr='eve',
    ja='\u30cb\u30e5\u30fc\u30a8\u30c7\u30f3',
    ru='eve',
    zh='eve',
)
DEFAULT_UNIVERSES['2'] = OrderedDict(
    name='wormhole',
    de='wormhole',
    en='wormhole',
    fr='wormhole',
    ja='\u30ef\u30fc\u30e0\u30db\u30fc\u30eb',
    ru='wormhole',
    zh='wormhole',
)
DEFAULT_UNIVERSES['3'] = OrderedDict(
    name='abyssal',
    de='abyssal',
    en='abyssal',
    fr='abyssal',
    ja='\u30a2\u30d3\u30b5\u30eb',
    ru='abyssal',
    zh='abyssal',
)
DEFAULT_UNIVERSES['4'] = OrderedDict(
    name='penalty',
    de='penalty',
    en='penalty',
    fr='penalty',
    ja='\u30da\u30ca\u30eb\u30c6\u30a3',
    ru='penalty',
    zh='penalty',
)

def get_json_by_file(path):
    if os.path.isfile(path):
        with open(path, 'r') as file:
            return json.load(file)
    return {}

def get_json_by_url(url):
    while(True):
        try:
            print('Download: ' + url)
            with urllib.request.urlopen(url) as html:
                data = json.loads(html.read().decode())
            time.sleep(1)
            return data
        except urllib.error.HTTPError:
            print('urllib.error.HTTPError: ' + url)
            time.sleep(30)

def get_supported_names(names):
    lang_dict = OrderedDict()
    lang_dict['name'] = names['en']
    for lang in LANGUAGES:
        if lang in names:
            lang_dict[lang] = names[lang]
        else:
            lang_dict[lang] = names['en']
    return lang_dict

def get_supported_names_by_esi(target_type, target_id, default_name):
    names = {'en': default_name}

    for lang in LANGUAGES:
        if lang == 'en':
            continue

        esi_url = 'https://esi.evetech.net/latest/universe/%s/%d?language=%s' % (
            target_type,
            target_id,
            lang,
        )

        names[lang] = get_json_by_url(esi_url)['name']
    return get_supported_names(names)

def generate_types_json(version):
    print('Create: ' + TYPES_JSON_PATH)

    # # Only categories to which the killmail is issued.
    # include_category_ids = [
    #     6,  # Ship
    #     18, # Drone
    #     22, # Deployable
    #     23, # Starbase
    #     46, # Orbitals
    #     65, # Structure
    #     87, # Fighter
    # ]

    include_category_ids = [
        4,  # Material
        6,  # Ship
        7,  # Module
        8,  # Charge
        9,  # Blueprint
        16, # Skill
        18, # Drone
        20, # Implant
        22, # Deployable
        23, # Starbase
        25, # Asteroid
        30, # Apparel
        32, # Subsystem
        42, # Planetary Resources
        43, # Planetary Commodities
        46, # Orbitals
        65, # Structure
        66, # Structure Module
        87, # Fighter
        91, # Super Kerr-Induced Nanocoatings
    ]

    include_group_ids = []
    base_path = os.path.join('.', 'sde', 'fsd')

    types = OrderedDict()
    types['version'] = version
    types['categories'] = OrderedDict()

    with open(os.path.join(base_path, 'categoryIDs.yaml')) as file:
        for i, items in yaml.load(file, Loader=yaml.FullLoader).items():
            if i not in include_category_ids:
                continue

            types['categories'][i] = get_supported_names(items['name'])

    types['groups'] = OrderedDict()
    with open(os.path.join(base_path, 'groupIDs.yaml')) as file:
        for i, items in yaml.load(file, Loader=yaml.FullLoader).items():
            if items['categoryID'] not in include_category_ids or not items['name']:
                continue

            include_group_ids.append(i)
            types['groups'][i] = get_supported_names(items['name'])
            types['groups'][i]['category_id'] = items['categoryID']

    types['types'] = {}
    with open(os.path.join(base_path, 'typeIDs.yaml')) as file:
        for i, items in yaml.load(file, Loader=yaml.FullLoader).items():
            if items['groupID'] not in include_group_ids or not items['name']:
                continue

            types['types'][i] = get_supported_names(items['name'])
            types['types'][i]['group_id'] = items['groupID']

    with open(TYPES_JSON_PATH, 'w', encoding='utf-8') as file:
        json.dump(types, file, indent=4)

def generate_universes_json(version):
    print('Create: ' + UNIVERSES_JSON_PATH)

    level_items = [
        # level_name, level_id_name, level_filename, parent_level_id_name, level_included_keys
        ('regions', 'regionID', 'region.staticdata', 'universe_id', []),
        ('constellations', 'constellationID', 'constellation.staticdata', 'region_id', []),
        ('systems', 'solarSystemID', 'solarsystem.staticdata', 'constellation_id', ['security']),
    ]

    universes = OrderedDict(
        version=version,
        universes=OrderedDict(),
        regions=OrderedDict(),
        constellations=OrderedDict(),
        systems=OrderedDict(),
    )

    universes['universes'] = copy.deepcopy(DEFAULT_UNIVERSES)

    cached_universes = get_json_by_file(UNIVERSES_JSON_PATH)
    if not cached_universes:
        cached_universes = {
            'regions': {},
            'constellations': {},
            'systems': {},
        }

    def get_universe_values(path, *names):
        values = {}
        with open(path) as file:
            target_yaml = yaml.load(file, Loader=yaml.FullLoader)
            for name in names:
                values[name] = target_yaml[name]
        return values

    def recursive(nest, parent_universe_id, path):
        for name in os.listdir(path):
            next_path = os.path.join(path, name)

            if not os.path.isdir(next_path):
                continue

            level_name, level_id_name, level_filename, parent_level_id_name, level_included_keys = level_items[nest]
            values = get_universe_values(os.path.join(next_path, level_filename), level_id_name, *level_included_keys)

            universe_id = values[level_id_name]
            universe_id_str = str(universe_id)

            if universe_id_str in cached_universes[level_name]:
                print('Cached: ' + next_path)
                universes[level_name][universe_id_str] = cached_universes[level_name][universe_id_str]
            else:
                print('Add: ' + next_path)
                universes[level_name][universe_id_str] = get_supported_names_by_esi(
                    level_name,
                    universe_id,
                    name,
                )
                universes[level_name][universe_id_str][parent_level_id_name] = parent_universe_id

                for key in level_included_keys:
                    universes[level_name][universe_id_str][key] = values[key]

            if nest <= -1:
                recursive(nest + 1, universe_id, next_path)

    base_path = os.path.join('.', 'sde', 'fsd', 'universe')
    for universe_name in os.listdir(base_path):
        recursive_path = os.path.join(base_path, universe_name)
        if os.path.isdir(recursive_path):
            recursive(0, UNIVERSE_IDS[universe_name], recursive_path)

    with open(UNIVERSES_JSON_PATH, 'w', encoding='utf-8') as file:
        json.dump(universes, file, indent=4)

def update_version(old_version):
    resources_url = 'https://developers.eveonline.com/resource/resources'

    while(True):
        try:
            with urllib.request.urlopen(resources_url) as html:
                soup = BeautifulSoup(html, 'html.parser')
            break
        except urllib.error.HTTPError:
            print('urllib.error.HTTPError: ' + resources_url)

    for link in soup.find('div', attrs={'class': 'content'}).findAll('a'):
        sde_url = link['href']

        if 'https://cdn1.eveonline.com/data/sde/tranquility/' in sde_url:
            parsed = urllib.parse.urlparse(sde_url)
            sde_filename = parsed.path[1:].split('/')[-1]

            version, ext = os.path.splitext(sde_filename)
            if ext == '.zip' and 'sde-' in version and '-TRANQUILITY' in version:
                if version == old_version:
                    print('Cached: ' + sde_url)
                    break

                while(True):
                    try:
                        print('Download: ' + sde_url)
                        with urllib.request.urlopen(sde_url) as data:
                            with open('sde.zip', mode='wb') as file:
                                file.write(data.read())
                        break
                    except urllib.error.HTTPError:
                        print('urllib.error.HTTPError: ' + sde_url)

                with zipfile.ZipFile('sde.zip') as zfile:
                    zfile.extractall()
    return version

def run():
    old_version = None
    if os.path.isfile(TYPES_JSON_PATH):
        old_version = get_json_by_file(TYPES_JSON_PATH)['version']

    version = update_version(old_version)

    if version != old_version:
        print('Update SDE')
        generate_types_json(version)
        generate_universes_json(version)
    else:
        print('SDE is the latest.')

if __name__ == '__main__':
    run()
