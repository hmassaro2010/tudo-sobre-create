from json import loads
from typing import Literal, Union
import pathlib as pl

mods : list[dict[Literal['file', 'value'], Union[str, bool]]] = []

with open('activate.json') as file:
    mods = loads(file.read())

MOD_FOLDER = pl.Path('servidor_minecraft/mods')

for mod in mods:
    pure_file = pl.Path(mod['file'].removesuffix('.jar'))
    path = MOD_FOLDER.joinpath(pure_file)
    jar_path = pl.Path(path.as_posix() + '.jar')
    
    if mod['value']:
        if path.exists():
            path.rename(jar_path)
            print(f'alterando {path}', flush=True)
    else:
        if jar_path.exists():
            jar_path.rename(path)
            print(f'alterando {path}', flush=True)