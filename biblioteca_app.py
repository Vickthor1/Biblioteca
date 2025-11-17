import psycopg2
from psycopg2.extras import RealDictCursor
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'biblioteca_db',
    'user': 'biblioteca_admin',
    'password': 'senha_do_admin'
}

class BibliotecaApp(tk.Tk):
    def __init__(self, db_config):
        self.db_config = db_config
        super().__init__()
        super().__init__()
        self.title('Controle de Empréstimos - Biblioteca')
        self.geometry('900x500')

        # Frames
        frm_top = ttk.Frame(self)
        frm_top.pack(fill='x', padx=8, pady=6)
        frm_mid = ttk.Frame(self)
        frm_mid.pack(fill='both', expand=True, padx=8, pady=6)
        frm_bot = ttk.Frame(self)
        frm_bot.pack(fill='x', padx=8, pady=6)

        # --- Campos para registrar novo usuário ---
        ttk.Label(frm_top, text='Nome Usuário').grid(row=1, column=0)
        self.ent_nome_usuario = ttk.Entry(frm_top, width=20)
        self.ent_nome_usuario.grid(row=1, column=1)

        ttk.Label(frm_top, text='Tipo').grid(row=1, column=2)
        self.ent_tipo_usuario = ttk.Entry(frm_top, width=12)
        self.ent_tipo_usuario.grid(row=1, column=3)

        ttk.Label(frm_top, text='Email').grid(row=1, column=4)
        self.ent_email_usuario = ttk.Entry(frm_top, width=20)
        self.ent_email_usuario.grid(row=1, column=5)

        ttk.Button(frm_top, text='Registrar Usuário', command=self.registrar_usuario).grid(row=1, column=6, padx=6)
        # --- Fim dos campos de usuário ---
        ttk.Label(frm_top, text='Usuario ID').grid(row=0, column=0)
        self.ent_usuario = ttk.Entry(frm_top, width=8)
        self.ent_usuario.grid(row=0, column=1)
        ttk.Label(frm_top, text='Livro ID').grid(row=0, column=2)
        self.ent_livro = ttk.Entry(frm_top, width=8)
        self.ent_livro.grid(row=0, column=3)
        ttk.Label(frm_top, text='Data Devolução (YYYY-MM-DD)').grid(row=0, column=4)
        self.ent_data_dev = ttk.Entry(frm_top, width=12)
        self.ent_data_dev.grid(row=0, column=5)

        # Botões
        ttk.Button(frm_top, text='Inserir Empréstimo', command=self.inserir).grid(row=0, column=6, padx=6)
        ttk.Button(frm_top, text='Atualizar Empréstimo', command=self.atualizar).grid(row=0, column=7, padx=6)
        ttk.Button(frm_top, text='Excluir Empréstimo', command=self.excluir).grid(row=0, column=8, padx=6)
        ttk.Button(frm_top, text='Registrar Devolução', command=self.registrar_devolucao).grid(row=0, column=9, padx=6)
        ttk.Button(frm_top, text='Atualizar View', command=self.carregar_view).grid(row=0, column=10, padx=6)
        

        # Treeview para exibir a view agregada
        columns = ('emprestimo_id','usuario_nome','usuario_tipo','livro_titulo','livro_autor','data_emprestimo','data_devolucao','status_devolvido')
        self.tree = ttk.Treeview(frm_mid, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor='center')
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        # Status
        self.status_var = tk.StringVar()
        ttk.Label(frm_bot, textvariable=self.status_var).pack(side='left')

        # conectar e carregar
        self.conn = None
        self.conectar()
        self.carregar_view()

    def conectar(self):
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.status_var.set('Conectado ao banco')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao conectar: {e}')
            self.status_var.set('Desconectado')

    def carregar_view(self):
        if not self.conn: return
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute('SELECT * FROM vw_emprestimos_overview ORDER BY emprestimo_id;')
            rows = cur.fetchall()
            cur.close()

            # limpar tree
            for r in self.tree.get_children():
                self.tree.delete(r)
            for row in rows:
                vals = (
                    row['emprestimo_id'], row['usuario_nome'], row['usuario_tipo'],
                    row['livro_titulo'], row['livro_autor'],
                    row['data_emprestimo'], row['data_devolucao'], row['status_devolvido']
                )
                self.tree.insert('', 'end', values=vals)
            self.status_var.set(f'{len(rows)} registros exibidos')
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao consultar view: {e}')

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel: return
        vals = self.tree.item(sel[0])['values']
        # !!!!!!!!!!!!!!!!preencher campos com usuario_id e livro_id não estão na view; buscar ids via query auxiliar, não esquece Victor!!!!!!!!!!!
        emprestimo_id = vals[0]
        try:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            cur.execute('SELECT usuario_id, livro_id, data_devolucao FROM emprestimos WHERE id = %s;', (emprestimo_id,))
            r = cur.fetchone()
            cur.close()
            if r:
                self.ent_usuario.delete(0,'end'); self.ent_usuario.insert(0, r['usuario_id'])
                self.ent_livro.delete(0,'end'); self.ent_livro.insert(0, r['livro_id'])
                self.ent_data_dev.delete(0,'end');
                if r['data_devolucao']:
                    self.ent_data_dev.insert(0, r['data_devolucao'].isoformat())
        except Exception as e:
            messagebox.showerror('Erro', f'Falha ao obter dados do empréstimo: {e}')

    def inserir(self):
        u = self.ent_usuario.get().strip()
        l = self.ent_livro.get().strip()
        if not u or not l:
            messagebox.showwarning('Aviso', 'Informe usuario_id e livro_id')
            return
        try:
            cur = self.conn.cursor()
            cur.execute('INSERT INTO emprestimos(usuario_id, livro_id) VALUES (%s,%s) RETURNING id;', (int(u), int(l)))
            new_id = cur.fetchone()[0]
            self.conn.commit()
            cur.close()
            messagebox.showinfo('Sucesso', f'Empréstimo criado com id {new_id}')
            self.carregar_view()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror('Erro', f'Falha ao inserir: {e}')

    def atualizar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Aviso', 'Selecione um empréstimo na lista para atualizar')
            return
        emprestimo_id = self.tree.item(sel[0])['values'][0]
        u = self.ent_usuario.get().strip()
        l = self.ent_livro.get().strip()
        data_dev = self.ent_data_dev.get().strip() or None
        try:
            cur = self.conn.cursor()
            cur.execute('UPDATE emprestimos SET usuario_id=%s, livro_id=%s, data_devolucao=%s WHERE id=%s;', (int(u), int(l), data_dev, emprestimo_id))
            self.conn.commit()
            cur.close()
            messagebox.showinfo('Sucesso', 'Empréstimo atualizado')
            self.carregar_view()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror('Erro', f'Falha ao atualizar: {e}')

    def excluir(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Aviso', 'Selecione um empréstimo na lista para excluir')
            return
        emprestimo_id = self.tree.item(sel[0])['values'][0]
        if not messagebox.askyesno('Confirmar', f'Deseja excluir o empréstimo {emprestimo_id}?'):
            return
        try:
            cur = self.conn.cursor()
            cur.execute('DELETE FROM emprestimos WHERE id=%s;', (emprestimo_id,))
            self.conn.commit()
            cur.close()
            messagebox.showinfo('Sucesso', 'Empréstimo excluído')
            self.carregar_view()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror('Erro', f'Falha ao excluir: {e}')

    def registrar_usuario(self):
        nome = self.ent_nome_usuario.get().strip()
        tipo = self.ent_tipo_usuario.get().strip()
        email = self.ent_email_usuario.get().strip()

        if not nome or not tipo:
            messagebox.showwarning('Aviso', 'Nome e tipo são obrigatórios.')
            return

        try:
            cur = self.conn.cursor()
            cur.execute('INSERT INTO usuarios(nome, tipo, email) VALUES (%s, %s, %s) RETURNING id;', (nome, tipo, email))
            new_id = cur.fetchone()[0]
            self.conn.commit()
            cur.close()
            messagebox.showinfo('Sucesso', f'Usuário registrado com id {new_id}')
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror('Erro', f'Falha ao registrar usuário: {e}')

    def registrar_devolucao(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('Aviso', 'Selecione um empréstimo na lista para registrar devolução')
            return
        emprestimo_id = self.tree.item(sel[0])['values'][0]
        hoje = date.today().isoformat()
        try:
            cur = self.conn.cursor()
            cur.execute('UPDATE emprestimos SET devolvido = TRUE, data_devolucao = %s WHERE id = %s;', (hoje, emprestimo_id))
            self.conn.commit()
            cur.close()
            messagebox.showinfo('Sucesso', 'Devolução registrada')
            self.carregar_view()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror('Erro', f'Falha ao registrar devolução: {e}')

def show_login_and_start():
    # Janela de login simples que tenta conectar ao banco com as credenciais fornecidas lá em cima, pra que pegar o código
    login = tk.Tk()
    login.title('Login - Biblioteca')
    login.geometry('320x140')
    ttk.Label(login, text='Usuário:').grid(row=0, column=0, padx=8, pady=8)
    ent_user = ttk.Entry(login)
    ent_user.grid(row=0, column=1, padx=8, pady=8)
    ttk.Label(login, text='Senha:').grid(row=1, column=0, padx=8, pady=8)
    ent_pass = ttk.Entry(login, show='*')
    ent_pass.grid(row=1, column=1, padx=8, pady=8)

    status_var = tk.StringVar()
    ttk.Label(login, textvariable=status_var).grid(row=3, column=0, columnspan=2)

    def tentar_login():
        user = ent_user.get().strip()
        passwd = ent_pass.get().strip()
        if not user or not passwd:
            status_var.set('Informe usuário e senha')
            return
        # monta a config temporária do banco
        cfg = {
            'host': 'localhost', 'port': 5432, 'database': 'biblioteca_db',
            'user': user, 'password': passwd
        }
        try:
            conn = psycopg2.connect(**cfg)
            conn.close()
            login.destroy()
            # abre app principal com as credenciais inseridas
            app = BibliotecaApp(cfg)
            app.mainloop()
        except Exception as e:
            status_var.set('Falha ao conectar: ' + str(e))

    btn = ttk.Button(login, text='Entrar', command=tentar_login)
    btn.grid(row=2, column=0, columnspan=2, pady=8)

    login.mainloop()

if __name__ == '__main__':
    show_login_and_start()
