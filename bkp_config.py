import os
import pandas as pd


class Config:

    REDE_DIR = r'\\NOMESERVIDOR'

    PASTAS = {
        'COMERCIAL': os.path.join(REDE_DIR, 'COMERCIAL'),
        'DIVERSOS': os.path.join(REDE_DIR, 'DIVERSOS'),
        'FINANCEIRO': os.path.join(REDE_DIR, 'FINANCEIRO'),
        'LOGISTICA': os.path.join(REDE_DIR, 'LOGISTICA'),
        'PRODUCAO': os.path.join(REDE_DIR, 'PRODUCAO'),
    }

    @classmethod
    def carregar_clientes(cls, caminho_planilha):
        abas = {
            'ABA1': 'ABA1_',
            'ABA2': 'ABA2_',
        }

        for aba, prefixo in abas.items():
            try:
                df = pd.read_excel(caminho_planilha, sheet_name=aba)
                for _, row in df.iterrows():
                    cliente = str(row['Cliente']).strip()
                    caminho_comum = str(row['Caminho Comum']).strip()
                    chave = f"{prefixo}{cliente.replace(' ', '_').upper()}"
                    cls.PASTAS[chave] = os.path.join(caminho_comum, cliente)
            except Exception as e:
                print(f'Erro ao carregar a aba {aba}: {e}')


Config.carregar_clientes('clientes.xlsx')
