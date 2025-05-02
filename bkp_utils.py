import os


class Utils:

    @staticmethod
    def carregar_exclusoes(path_txt):
        exclusoes = {}
        if not os.path.exists(path_txt):
            return exclusoes

        with open(path_txt, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith('#') or ':' not in linha:
                    continue
                pasta, item = map(str.strip, linha.split(':', 1))
                pasta = pasta.upper()
                exclusoes.setdefault(pasta, []).append(item)
        return exclusoes
