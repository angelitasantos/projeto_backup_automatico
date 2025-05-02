import os
import shutil
from datetime import datetime
from bkp_config import Config


class BackupManager:

    def __init__(self, tipo, destino, exclusoes, progresso_callback=None):
        self.tipo = tipo
        self.destino = destino
        self.exclusoes = exclusoes
        self.nao_copiados = []
        self.progresso_callback = progresso_callback
        self.contador = 0
        self.total_arquivos = 1

    def executar(self, pasta_especifica=None, total_arquivos=1):
        self.total_arquivos = total_arquivos
        data_atual = datetime.now().strftime('%Y-%m-%d')
        destino_final = os.path.join(self.destino, f'{self.tipo}_{data_atual}')

        os.makedirs(destino_final, exist_ok=True)

        if pasta_especifica:
            nome_pasta = next((
                k for k, v in Config.PASTAS.items() if v == pasta_especifica),
                'PASTA_PERSONALIZADA')
            destino_pasta = os.path.join(destino_final, nome_pasta)

            if os.path.exists(destino_pasta):
                shutil.rmtree(destino_pasta)

            self.copiar_pasta(pasta_especifica, destino_pasta)

        else:
            if os.path.exists(destino_final):
                shutil.rmtree(destino_final)
            os.makedirs(destino_final, exist_ok=True)

            for nome_pasta, caminho_origem in Config.PASTAS.items():
                self.copiar_pasta(caminho_origem, os.path.join(
                    destino_final, nome_pasta))

        if self.nao_copiados:
            with open('arquivos_nao_copiados.txt',
                      'w', encoding='utf-8') as log:
                log.write('Arquivos que não puderam ser copiados:\n\n')
                for caminho in self.nao_copiados:
                    log.write(f'{caminho}\n')

    def copiar_pasta(self, origem, destino):
        arquivos_excluidos = ['thumbs.db', 'desktop.ini']

        for dirpath, dirnames, filenames in os.walk(origem):
            if any(excl.lower() in dirpath.lower() for excl in self.exclusoes):
                continue

            destino_dir = dirpath.replace(origem, destino, 1)
            os.makedirs(destino_dir, exist_ok=True)

            for arquivo in filenames:
                if arquivo.lower() in arquivos_excluidos:
                    continue

                origem_arquivo = os.path.join(dirpath, arquivo)
                destino_arquivo = os.path.join(destino_dir, arquivo)

                try:
                    shutil.copy2(origem_arquivo, destino_arquivo)
                except (OSError, FileNotFoundError):
                    self.nao_copiados.append(origem_arquivo)

                self.contador += 1
                progresso = int((self.contador / self.total_arquivos) * 100)
                if self.progresso_callback and progresso % 10 == 0:
                    self.progresso_callback(progresso)
