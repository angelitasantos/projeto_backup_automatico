import os
import tkinter as tk
from tkinter import messagebox, ttk
import threading
from bkp_config import Config
from bkp_utils import Utils
from bkp_backup import BackupManager


class BackupApp:

    def __init__(self, root, width=600, height=620):
        self.root = root
        self.width = width
        self.height = height
        self.root.title('Assistente de Backup')
        self.root.geometry(f'{self.width}x{self.height}')
        self.centralizar_tela()

        self.tipo = None
        self.hd = None
        self.pasta_especifica = None

        self.criar_interface()

    def centralizar_tela(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - self.height / 2)
        position_right = int(screen_width / 2 - self.width / 2)
        self.root.geometry(
            f'{self.width}x{self.height}+{position_right}+{position_top}')

    def criar_interface(self):
        tk.Label(self.root, text='Escolha o tipo de backup:',
                 font=('Arial', 10)).pack(pady=10)

        self.tipo_var = tk.StringVar()
        self.tipo_var.set('')

        tipo_frame = tk.Frame(self.root)
        tipo_frame.pack(pady=5)

        tk.Radiobutton(tipo_frame, text='Simples', variable=self.tipo_var,
                       value='SIMPLES', font=('Arial', 10)).grid(
                           row=0, column=0, padx=10)
        tk.Radiobutton(tipo_frame, text='Completo', variable=self.tipo_var,
                       value='COMPLETO', font=('Arial', 10)).grid(
                           row=0, column=1, padx=10)

        botoes_frame = tk.Frame(self.root)
        botoes_frame.pack(pady=5)

        tk.Button(botoes_frame, text='Escolher tipo',
                  command=self.escolher_tipo,
                  font=('Arial', 10)).grid(row=0, column=0, padx=10)
        tk.Button(botoes_frame, text='Cancelar', command=self.cancelar,
                  font=('Arial', 10), bg='red', fg='white').grid(
                      row=0, column=1, padx=10)

        self.progresso_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.root, variable=self.progresso_var, maximum=100, length=500)
        self.progress_bar.pack(pady=20)

    def escolher_tipo(self):
        tipo = self.tipo_var.get()
        if tipo:
            self.tipo = tipo
            self.mostrar_hd_input()
        else:
            messagebox.showerror('Erro',
                                 'Por favor, selecione um tipo de backup!')

    def mostrar_hd_input(self):
        self.tipo_frame = tk.Frame(self.root)
        self.tipo_frame.pack(pady=10)

        tk.Label(self.tipo_frame, text='Digite a letra do HD externo (ex: D):',
                 font=('Arial', 10)).pack()
        self.hd_entry = tk.Entry(self.tipo_frame, font=('Arial', 10))
        self.hd_entry.pack(pady=5)
        tk.Button(self.tipo_frame, text='Confirmar HD',
                  command=self.escolher_hd, font=('Arial', 10)).pack(pady=10)

    def escolher_hd(self):
        hd = self.hd_entry.get().strip().upper()
        if hd:
            self.hd = hd + ':\\BACKUP'
            self.mostrar_pasta_input()
        else:
            messagebox.showerror('Erro',
                                 'Por favor, insira uma letra de HD válida!')

    def mostrar_pasta_input(self):
        self.tipo_frame.destroy()
        tk.Label(self.root, text='Deseja copiar uma pasta específica?',
                 font=('Arial', 10)).pack(pady=5)

        self.pasta_especifica_var = tk.StringVar()

        radio_frame = tk.Frame(self.root)
        radio_frame.pack(pady=5)

        tk.Radiobutton(radio_frame, text='Sim',
                       variable=self.pasta_especifica_var, value='sim',
                       font=('Arial', 10)).grid(row=0, column=0, padx=5)
        tk.Radiobutton(radio_frame, text='Não',
                       variable=self.pasta_especifica_var, value='nao',
                       font=('Arial', 10)).grid(row=0, column=1, padx=5)

        tk.Button(self.root, text='Confirmar', command=self.escolher_pasta,
                  font=('Arial', 10)).pack(pady=5)

    def escolher_pasta(self):
        escolha = self.pasta_especifica_var.get()
        if escolha == 'sim':
            self.mostrar_pastas_disponiveis()
        elif escolha == 'nao':
            self.iniciar_backup()
        else:
            messagebox.showerror('Erro',
                                 'Por favor, selecione "Sim" ou "Não"!')

    def mostrar_pastas_disponiveis(self):
        self.pasta_especifica_frame = tk.Frame(self.root)
        self.pasta_especifica_frame.pack(pady=10)

        tk.Label(self.pasta_especifica_frame,
                 text='Escolha uma pasta para backup:',
                 font=('Arial', 10)).pack()

        self.pasta_listbox = tk.Listbox(self.pasta_especifica_frame,
                                        font=('Arial', 10), height=6)
        for nome in Config.PASTAS.keys():
            self.pasta_listbox.insert(tk.END, nome)
        self.pasta_listbox.pack(pady=10)

        tk.Button(self.pasta_especifica_frame, text='Confirmar',
                  command=self.confirmar_pasta,
                  font=('Arial', 10)).pack(pady=10)

    def confirmar_pasta(self):
        selected_index = self.pasta_listbox.curselection()
        if selected_index:
            pasta_escolhida_nome = self.pasta_listbox.get(selected_index[0])
            pasta_path = Config.PASTAS[pasta_escolhida_nome]
            self.loading_window = tk.Toplevel(self.root)
            self.loading_window.title('Aguarde')
            tk.Label(self.loading_window,
                     text='Calculando tamanho da pasta...',
                     font=('Arial', 10)).pack(padx=20, pady=20)
            self.loading_window.grab_set()
            self.root.update_idletasks()

            threading.Thread(target=self.verificar_tamanho_e_confirmar,
                             args=(pasta_escolhida_nome, pasta_path)).start()

        else:
            messagebox.showerror('Erro',
                                 'Por favor, selecione uma pasta válida!')

    def verificar_tamanho_e_confirmar(self, nome, caminho):
        tamanho_pasta = self.calcular_tamanho_pasta(caminho)
        tamanho_formatado = self.formatar_tamanho(tamanho_pasta)

        def confirmar():
            if tamanho_pasta > 0:
                mensagem = (
                    f'A pasta "{nome}" tem o tamanho de {tamanho_formatado}. '
                    'Deseja continuar com o backup?'
                )
                resposta = messagebox.askyesno(
                    'Confirmação do Backup', mensagem)
                if resposta:
                    self.pasta_especifica = caminho
                    self.iniciar_backup()
            else:
                messagebox.showwarning(
                    'Atenção',
                    (
                        'O tamanho da pasta é 0.0 B. '
                        'Verifique se a pasta está vazia ou inacessível.'
                    )
                )
        self.root.after(0, self.loading_window.destroy)
        self.root.after(0, confirmar)

    def calcular_tamanho_pasta(self, pasta):
        tamanho_total = 0
        arquivos_excluidos = ['thumbs.db', 'desktop.ini']
        ignorados = []

        if os.path.exists(pasta):
            for dirpath, dirnames, filenames in os.walk(pasta):
                for filename in filenames:
                    if filename.lower() in arquivos_excluidos:
                        continue
                    filepath = os.path.join(dirpath, filename)
                    try:
                        tamanho_total += os.path.getsize(filepath)
                    except (FileNotFoundError, OSError):
                        ignorados.append(filepath)
        else:
            print(f'Erro: A pasta {pasta} não foi encontrada.')

        if ignorados:
            with open('arquivos_ignorados.txt',
                      'w', encoding='utf-8') as log_file:
                log_file.write(
                    'Arquivos ignorados durante o cálculo do tamanho:\n\n')
                for caminho in ignorados:
                    log_file.write(f'{caminho}\n')

        return tamanho_total

    def formatar_tamanho(self, tamanho):
        for unidade in ['B', 'KB', 'MB', 'GB', 'TB']:
            if tamanho < 1024.0:
                return f'{tamanho:.2f} {unidade}'
            tamanho /= 1024.0

    def iniciar_backup(self):
        self.cancelar_calculo = False
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title('Aguarde')
        tk.Label(self.loading_window,
                 text='Calculando número total de arquivos...',
                 font=('Arial', 10)).pack(padx=20, pady=10)
        tk.Button(self.loading_window, text='Cancelar',
                  command=self.cancelar_verificacao,
                  font=('Arial', 10)).pack(pady=10)
        self.loading_window.grab_set()
        self.root.update_idletasks()

        threading.Thread(target=self.preparar_backup).start()

    def cancelar_verificacao(self):
        self.cancelar_calculo = True
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()
        messagebox.showinfo(
            'Cancelado',
            (
                'Cálculo de backup cancelado. '
                'Você pode tentar novamente.'
            )
        )

    def preparar_backup(self):
        exclusoes_dict = Utils.carregar_exclusoes('exclusoes.txt')
        exclusoes = [
            item for lista in exclusoes_dict.values() for item in lista]
        exclusoes.extend(['Thumbs.db', 'desktop.ini'])

        backup = BackupManager(self.tipo, self.hd, exclusoes,
                               progresso_callback=self.atualizar_progresso)

        if self.pasta_especifica:
            total = self.contar_arquivos(self.pasta_especifica)
            if self.cancelar_calculo:
                self.root.after(0, self.loading_window.destroy)
                return
            self.root.after(0, self.loading_window.destroy)
            backup.executar(pasta_especifica=self.pasta_especifica,
                            total_arquivos=total)
        else:
            total = 0
            for pasta in Config.PASTAS.values():
                if self.cancelar_calculo:
                    self.root.after(0, self.loading_window.destroy)
                    return
                total += self.contar_arquivos(pasta)
            self.root.after(0, self.loading_window.destroy)
            backup.executar(total_arquivos=total)

        self.root.after(0, lambda: self.finalizar_backup())

    def executar_backup_thread(self):
        exclusoes_dict = Utils.carregar_exclusoes('exclusoes.txt')
        exclusoes = [
            item for lista in exclusoes_dict.values() for item in lista]
        exclusoes.extend(['Thumbs.db', 'desktop.ini'])

        backup = BackupManager(self.tipo, self.hd, exclusoes,
                               progresso_callback=self.atualizar_progresso)

        if self.pasta_especifica:
            total = self.contar_arquivos(self.pasta_especifica)
            backup.executar(pasta_especifica=self.pasta_especifica,
                            total_arquivos=total)
        else:
            total = sum(
                self.contar_arquivos(p) for p in Config.PASTAS.values())
            backup.executar(total_arquivos=total)

        self.root.after(0, lambda: self.finalizar_backup())

    def finalizar_backup(self):
        self.progresso_var.set(100)
        self.root.update_idletasks()
        messagebox.showinfo('Sucesso', 'Backup concluído com sucesso!')

    def atualizar_progresso(self, valor):
        self.progresso_var.set(valor)
        self.root.update_idletasks()

    def contar_arquivos(self, pasta):
        total = 0
        for _, _, arquivos in os.walk(pasta):
            total += len(arquivos)
        return total

    def cancelar(self):
        resposta = messagebox.askyesno('Cancelar',
                                       'Você tem certeza que deseja cancelar?')
        if resposta:
            self.root.quit()


if __name__ == '__main__':
    root = tk.Tk()
    app = BackupApp(root, width=600, height=520)
    root.mainloop()
