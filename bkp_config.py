import os


class Config:

    REDE_DIR = r'\\NOMESERVIDOR'

    PASTAS = {
        'COMERCIAL': os.path.join(REDE_DIR, 'COMERCIAL'),
        'DIVERSOS': os.path.join(REDE_DIR, 'DIVERSOS'),
        'FINANCEIRO': os.path.join(REDE_DIR, 'FINANCEIRO'),
        'LOGISTICA': os.path.join(REDE_DIR, 'LOGISTICA'),
        'PRODUCAO': os.path.join(REDE_DIR, 'PRODUCAO'),
    }
