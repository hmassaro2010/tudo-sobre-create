import tomllib
import pathlib as pl
import zipfile
import requests
import argparse
import hashlib as hl
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
clear-download = true\n\n\
# É um servidor?\n\
is-server = false'

MODPACK_VERSION = 'v0'
GIT_VERSIONS = []
TO_INSTALL_VERSIONS = []
TO_DELETE: list[dict[Literal['path', 'type'], Union[pl.Path, Literal['folder', 'file']]]] = []
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
        with open('updater_config.toml', 'rb') as file:
            CONFIG = tomllib.load(file)
            
    except FileNotFoundError:
        with open('updater_config.toml', 'w') as file:
            file.write(DEFAULT_CONFIG)
        print('Nova configuração criada, configure no arquivo "updater_config.toml"')
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
    global MODPACK_VERSION
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
            print(r['name'], flush=True)
            GIT_VERSIONS.append({
                'version': r['name'],
                'url': r['assets_url']
            })
    
    else:
        print(f'Erro {response.status_code}: {dumps(response.json(), indent=2)}')
        sleep(3)
        exit()

def compareVersions(v1, v2):
    for i in range(max(len(v1), len(v2))):
        t1 = v1[i] if i < len(v1) else (0, '0')
        t2 = v2[i] if i < len(v2) else (0, '0')

        # Se os números forem diferentes, decidimos pela STRING se quisermos
        # que '2' > '11'. Em strings, '2' vem depois de '1'.
        if t1[1] != t2[1]:
            return t1[1] < t2[1]
            
    return False

# Cria uma lista de quais versões necessitam ser baixadas
def toInstallVersions():
    global TO_INSTALL_VERSIONS
    
    v_to_tuple = lambda vers : tuple(
        (int(v), v) for v in vers.lower().replace('v', '').split('.')
    )
    this_version = v_to_tuple(MODPACK_VERSION)

    print(this_version)
    print("não")
    
    for version in GIT_VERSIONS:
        print(version)
        if compareVersions(this_version, v_to_tuple(version['version'])):
            TO_INSTALL_VERSIONS.append(version)

# Baixa o conteudo de uma versão
def installContent(version):
    print('\nPreparando para baixar conteúdo')
    
    url = version['url']
    header = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'Bearer {CONFIG.get('auth-token', '')}'
    }
    
    response = requests.get(url, headers=header)
    
    if response.status_code == 200:
        assets = response.json()
        
        if pl.Path(f'download/{version['version']}').exists():
            print('O conteúdo já esta baixado, pulando etapa.')
            return
        
        if pl.Path('download/content.zip').exists():
            # Faz verificação se o arquivo é identico
            sha256 = hl.sha256()
            
            # gera hash local
            with open('./download/content.zip', 'rb') as f:
                for chunk in iter(lambda: f.read(8 * 1024), b""):
                    sha256.update(chunk)
            
            # compara com hash remoto
            if str(assets[0]['digest']).removeprefix('sha256:') == sha256.hexdigest():
                print('O conteúdo já esta baixado, pulando etapa.')
                return
            
            else:
                remove('./download/content.zip')
        
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
            print('O conteúdo já esta descompactado, pulando etapa.')
            return
    
    with zipfile.ZipFile('download/content.zip', 'r') as zip:
        zip.extractall('download/')

# Ler arquivo de deleção
def readDeleteFile(del_file):
    global TO_DELETE
    main_path = pl.Path(CONFIG['minecraft-path'])
    
    with open(del_file, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip()
            
            # comentários e linhas vazias
            if line.startswith('#') or line == '':
                continue
            
            # comentários pós arquivo/modificador
            line= line.split('#', 1)[0]
            line = line.strip()
            
            # modificador de caminhos
            if line.startswith('[') and line.endswith(']'):
                line = line.strip('[]')
                main_path = pl.Path(CONFIG['minecraft-path'])
                
                # separação por '/' menos recomendadp
                if line.find('/') != -1:
                    for part in line.split('/'):
                        if part != '': main_path = main_path.joinpath(part) 
                
                # separação por '.'
                else:
                    for part in line.split('.'):
                        if part != '': main_path = main_path.joinpath(part) 

                continue

            # salva caminho do arquivo a deletar
            to_delete_path = main_path.joinpath(line)
            
            TO_DELETE.append({
                'path': to_delete_path,
                'type': 'folder' if isdir(to_delete_path) else 'file'
            })

# Coleta lista de arquivos para deletar
def getToDelete(version):
    del_txt = pl.Path('download').joinpath(version['version'], 'del.txt')
    sdel_txt = pl.Path('download').joinpath(version['version'], 'sdel.txt')
    
    state = False
    
    if del_txt.exists():
        readDeleteFile(del_txt)
        state = True

    if CONFIG['is-server'] and sdel_txt.exists():
        readDeleteFile(sdel_txt)
        state = True
    
    return state    

# Pede permissão para deletar arquivos
# Pode evita deletar arquivos importantes
def getDelPermission():
    print('\n')
    if FORCE_DELETE: return True
    
    for path in TO_DELETE:
        print(path['path'], flush=True)
    print('Para cancelar a atualização aperte "CTRL + C".')
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
        # Não copias os arquivos de deleção
        if from_copy.as_posix() == f'download/{version['version']}/del.txt' or from_copy.as_posix() == f'download/{version['version']}/sdel.txt':
            continue
        
        print(f'Copiando {from_copy}', flush=True)
        if isdir(from_copy):
            copytree(from_copy, pl.Path(CONFIG['minecraft-path']).joinpath(from_copy.as_posix().removeprefix(f'download/{version['version']}/')), dirs_exist_ok=True)
        
        else:
            copy2(from_copy, pl.Path(CONFIG['minecraft-path']).joinpath(from_copy.as_posix().removeprefix(f'download/{version['version']}/')))

# Limpa os arquivos de download
def cleanDownloads(version):
    print('\nLimpando downloads.')
    try:
        remove('download/content.zip')
    except Exception:
        pass
    if CONFIG['clear-download']: rmtree(f'download/{version['version']}')

def main():
    global TO_INSTALL_VERSIONS, TO_DELETE, MODPACK_VERSION
    
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
        print(MODPACK_VERSION)
        saveVersion()
        cleanDownloads(installVersion)
        
        print(f'Versão {installVersion['version']} instalada com sucesso')
        
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Atualização cancelada, até mais o/')
    except Exception as e:
        print(e)
    
    sleep(5)