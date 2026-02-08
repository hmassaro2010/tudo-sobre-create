import tomllib
import pathlib as pl
import zipfile
import requests
import argparse
from time import sleep
from json import dumps
from shutil import rmtree, copy2, copytree
from os import remove
from os.path import isdir
from typing import Literal, Union

CONFIG = {}
DEFAULT_CONFIG = \
'# Caminho para o .minecraft\n\
minecraft-path = "C:/users/eu/caminho/para/a/.minecraft"\n\n\
# Repositório do modpack\n\
modpack-repo = "User/repository"\n\n\
# Token de autorização (opicional)\n\
auth-token = ""\n\n\
# Limpa os arquivos de versão baixados.\n\
clear-download = true'

MODPACK_VERSION = 'v0'
GIT_VERSIONS = []
TO_INSTALL_VERSIONS = []
TO_DELETE: list[dict[Literal['path', 'type'], Union[pl.Path, Literal['file', 'folder']]]] = []
FORCE_DELETE = False

# Argumentos
def argParser():
    global FORCE_DELETE
    parser = argparse.ArgumentParser(description='Atualiza automaticamente o modpack para seus amigos.')
    parser.add_argument('-f', '--force', action='store_true', help='Força deletar os arquivos sem pedir permissão.')
    
    args = parser.parse_args()
    FORCE_DELETE = args.force

# Carrega configuração
def loadConfig():
    global CONFIG
    try:
        with open('config.toml', 'rb') as file:
            CONFIG = tomllib.load(file)
            
    except FileNotFoundError:
        with open('config.toml', 'w') as file:
            file.write(DEFAULT_CONFIG)
        print('Nova configuração criada, configure no arquivo "config.toml"')
        sleep(3)
        exit()
    
    except tomllib.TOMLDecodeError:
        print('Erro: Arquivo de configuração mal formatado (Se não consiguir resolver delete-o)')
        sleep(3)
        exit()

# Carrega versão atual do modpack
def loadVersion():
    global MODPACK_VERSION
    version_path = pl.Path(CONFIG['minecraft-path']).joinpath('modpack-version.txt')
    try:
        with open(version_path, 'r') as file:
            MODPACK_VERSION = file.read()
            
    except FileNotFoundError:
        saveVersion()

# Salva a versão atual
def saveVersion():
    version_path = pl.Path(CONFIG['minecraft-path']).joinpath('modpack-version.txt')
    
    with open(version_path, 'w') as file:
        file.write(MODPACK_VERSION)

# Coleta versões do git
def getGitVersions():
    print('\nColetando versões disponíveis.')
    global GIT_VERSIONS
    url = f'https://api.github.com/repos/{CONFIG['modpack-repo']}/releases'
    header = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {CONFIG.get('auth-token', '')}'
    }
    response = requests.get(url, headers=header)
    
    if response.status_code == 200:
        releases = response.json()
        for r in releases:
            GIT_VERSIONS.append({
                'version': r['name'],
                'url': r['assets_url']
            })
        
        # Ordena numéricamente
        GIT_VERSIONS = sorted(GIT_VERSIONS, key = lambda v: tuple(map(int, v['version'].removeprefix('v').removeprefix('V').split('.'))))
            
    else:
        print(f'Erro {response.status_code}: {dumps(response.json(), indent=2)}')
        sleep(3)
        exit()

# Cria uma lista de quais versões necessitam ser baixadas
def toInstallVersions():
    global TO_INSTALL_VERSIONS
    for version in GIT_VERSIONS:

        num_version = tuple(map(int, version['version'].removeprefix('v').removeprefix('V').split('.')))
        actual_num_version = tuple(map(int, MODPACK_VERSION.removeprefix('v').removeprefix('V').split('.')))
        

        if num_version > actual_num_version:
            TO_INSTALL_VERSIONS.append(version)

# Baixa o conteudo de uma versão
def installContent(version):
    print('\nPreparando para baixar conteúdo')
    
    if pl.Path('download/content.zip').exists() or pl.Path(f'download/{version['version']}').exists():
        print('Arquivo de conteúdo já existe, pulando.')
        return
    
    url = version['url']
    header = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'Bearer {CONFIG.get('auth-token', '')}'
    }
    
    response = requests.get(url, headers=header)
    
    if response.status_code == 200:
        assets = response.json()
        
        download_url = assets[0]['url']
        download_size = assets[0]['size']
        header['Accept'] = 'application/octet-stream'
        
        downloadFolder = pl.Path('download')
        downloadFolder.mkdir(exist_ok=True)
        
        dResponse = requests.get(download_url, headers=header, stream=True)
        
        if dResponse.status_code == 200:
            
            with open('download/content.zip', 'wb') as out:
                total_downloaded = 0
                for chunk in dResponse.iter_content(chunk_size=8192):
                    out.write(chunk)
                    total_downloaded += len(chunk)
                    print(f'\r{total_downloaded / download_size * 100:.2f}%', flush=True, end='')
                print('\rDownload Concluído')
        
        else:
            print(f'Erro ao baixar arquivo zip {dResponse.status_code}: {dResponse.text}')
            sleep(3)
            exit()
        
    else:
        print(f'Erro {response.status_code}: {dumps(response.json(), indent=2)}')
        sleep(3)
        exit()

# Descompacta o conteudo
def uncompressContent(version):
    print('\nDescompactando arquivo.')
    if pl.Path(f'download/{version['version']}').exists():
        print('Arquivo já descompactado, pulando')
        return
    
    with zipfile.ZipFile('download/content.zip', 'r') as zip:
        zip.extractall('download/')

# Coleta lista de arquivos para deletar
def getToDelete(version):
    global TO_DELETE
    del_txt = pl.Path('download').joinpath(version['version'], 'del.txt')
    
    if del_txt.exists():
        
        # Transforma o conteudo do txt em uma lista de arquivos
        main_path = pl.Path(CONFIG['minecraft-path'])
        
        with open(del_txt, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith('#') or line == '':
                    continue
                
                line = line.split('#')[0]
                line = line.strip()
                
                # Modificador de caminho
                if line.startswith('[') and line.endswith(']'):
                    line = line.strip('[]')
                    main_path = pl.Path(CONFIG['minecraft-path'])
                    
                    # Trata pontos consecutivos (..) corretamente
                    parts = []
                    for part in line.split('.'):
                        if part == '':  # Ponto duplo (..) significa subir um nível
                            if parts:  # Só sobe se tiver onde subir
                                parts = parts[:-1]
                        else:
                            parts.append(part)
                    
                    # Reconstrói o caminho
                    for path in parts:
                        main_path = main_path.joinpath(path)
                    continue
                    
                # Caminho de arquivo/pasta
                to_delete_path = main_path.joinpath(line)
                TO_DELETE.append({
                    'path': to_delete_path,
                    'type': isdir(to_delete_path) and 'folder' or 'file'
                })
        
        return True
    else:
        print('Nenhum arquivo a deletar.')
        return False

# Pede permissão para deletar arquivos
def getDelPermission():
    print('\n')
    if FORCE_DELETE: return True
    
    for path in TO_DELETE:
        print(path['path'], flush=True)
    permission = input('Permitir deletar os arquivos acima? [S/n]: ')
    permission = permission.strip()
    if permission == '' or permission.lower() == 's':
        return True
    else:
        print('Permissão negada.')
        return False

# Deleta tudo
def delete():
    print('\nPreparando para deletar arquivos.')
    for delObj in TO_DELETE:
        if delObj['path'].exists():
            print(f'Deletando {delObj['path']}', flush=True)
            if delObj['type'] == 'file':
                remove(delObj['path'])
            else:
                rmtree(delObj['path'])
        else:
            print(f'Não encontrado {delObj['path']}', flush=True)

# Copia os outros arquivas
def copyContent(version):
    print('\nPreparando para copiar arquivos.')
    main_path = pl.Path(f'download/{version['version']}')
    for from_copy in main_path.glob('*'):
        if from_copy.as_posix() == f'download/{version['version']}/del.txt':
            continue
        
        print(f'Copiando {from_copy}', flush=True)
        if isdir(from_copy):
            copytree(from_copy, pl.Path(CONFIG['minecraft-path']).joinpath(from_copy.as_posix().removeprefix(f'download/{version['version']}/')), dirs_exist_ok=True)
            #print(pl.Path(CONFIG['minecraft-path']).joinpath(from_copy.as_posix().removeprefix(f'download/{version['version']}/')))
        
        else:
            copy2(from_copy, pl.Path(CONFIG['minecraft-path']).joinpath(from_copy.as_posix().removeprefix(f'download/{version['version']}/')))
            #print(pl.Path(CONFIG['minecraft-path']).joinpath(from_copy.as_posix().removeprefix(f'download/{version['version']}/')).as_posix())

# Limpa os arquivos de download
def cleanDownloads(version):
    print('\nLimpando downloads.')
    try:
        remove('download/content.zip')
    except Exception:
        pass
    if CONFIG['clear-download']: rmtree(f'download/{version['version']}')

def main():
    argParser()
    loadConfig()
    loadVersion()
    getGitVersions()
    toInstallVersions()
    if len(TO_INSTALL_VERSIONS) <= 0:
        print('seu modpack já está atualizado.')
        return
    
    for installVersion in TO_INSTALL_VERSIONS:
        print(f'\nBaixando versão {installVersion['version']}')
        
        TO_DELETE = []
        installContent(installVersion)
        uncompressContent(installVersion)
        
        is_deleting = getToDelete(installVersion)
        if is_deleting and getDelPermission():
            delete()
        else:
            print('Pulando.')

        copyContent(installVersion)
        MODPACK_VERSION = installVersion['version']
        saveVersion()
        cleanDownloads(installVersion)
        
        print(f'Versão {installVersion['version']} instalada com sucesso')
        
        
if __name__ == '__main__':
    main()
    sleep(5)