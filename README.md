# 📚 Sistema de Biblioteca Universitária

**Flask + PostgreSQL + Interface Web (HTML/CSS/JS)**

Este projeto implementa um sistema completo de controle de biblioteca com:

* Backend em **Python + Flask**
* Banco de dados **PostgreSQL**
* Interface Web em **HTML/CSS/JavaScript**
* Autenticação com níveis de acesso (Admin x Leitor)
* CRUD completo de Usuários, Livros e Empréstimos
* Logs de operações via Trigger no banco
* View agregada para facilitar consultas
* Filtros e consultas avançadas

---

## 📌 1. Objetivo do Sistema

Permitir o gerenciamento completo de uma biblioteca universitária:

* Cadastro de usuários (alunos / funcionários)
* Cadastro de livros
* Controle de empréstimos e devoluções
* Registro automático de logs
* Camadas de acesso (admin → CRUD completo, leitor → somente leitura)
* Interface simplificada e funcional

---

## 📌 2. Arquitetura do Projeto

```
/biblioteca/
 ├── backend_full.py           # API Flask
 ├── web_ui.html               # Interface Web
 ├── biblioteca.sql            # Criação do banco + views + triggers
 └── README.md                 # Documentação
```

---

## 📌 3. Tecnologias Utilizadas

### Backend

* Python 3.10+
* Flask
* Psycopg2 (PostgreSQL connector)

### Banco

* PostgreSQL 14+
* Views, Constraints, FK, Triggers, JSONB

### Frontend

* HTML5 + CSS3
* JavaScript puro (fetch API)
* Layout responsivo básico

---

## 📌 4. Configuração do Banco de Dados

O script `biblioteca.sql` contém:

### 🧱 Criação de tabelas

* `usuarios`
* `livros`
* `emprestimos`
* `log_emprestimos`

### 🔐 Criação de usuários do banco

* `biblioteca_admin` → acesso total
* `biblioteca_leitor` → apenas SELECT na view

### 🪝 Trigger de Log

Qualquer alteração em `emprestimos` gera automaticamente:

* Tipo de operação
* Dados antes/depois (JSONB)
* Data/Hora
* Usuário do banco

### 🔭 View Agregada

`vw_emprestimos_overview` une:

* Usuário
* Livro
* Empréstimo
* Status (devolvido ou em andamento)

---

## 📌 5. Backend (Flask)

O backend fornece uma API REST para:

### 🔐 Autenticação

```
POST /auth/login
```

Retorna:

* token de sessão
* role (admin/leitor)

### 👤 Usuários

```
GET /usuarios
POST /usuarios
PUT /usuarios/<id>
DELETE /usuarios/<id>
```

### 📚 Livros

```
GET /livros
POST /livros
PUT /livros/<id>
DELETE /livros/<id>
```

### 📕 Empréstimos

```
GET /emprestimos
POST /emprestimos
PUT /emprestimos/<id>
PATCH /emprestimos/<id>/devolver
DELETE /emprestimos/<id>
```

### 📝 Logs

```
GET /logs
```

Para rodar o backend:

```bash
pip install flask psycopg2-binary
python backend.py
```

---

## 📌 6. Interface Web (web.ui.html)

A interface inclui abas para:

### 1️⃣ **Login**

Autenticação com backend, acesso limitado por perfil.

### 2️⃣ **Usuários**

* Cadastro
* Edição
* Exclusão
* Listagem automática

### 3️⃣ **Livros**

* Cadastro completo
* Atualização
* Remoção
* Estoque atualizado conforme empréstimos

### 4️⃣ **Empréstimos**

* Registrar empréstimo
* Registrar devolução
* Exclusão de empréstimo
* Filtros (usuário / livro / status / datas)
* Tabela dinâmica conectada à view do banco

### 5️⃣ **Logs**

Exibe todas as operações registradas pela trigger.

### 6️⃣ **Logout**

Remove token e volta à tela de login.

---

## 📌 7. Fluxo de Funcionamento

### 🔹 Passo 1 — Criar o banco

Execute:

```bash
psql -U postgres -f biblioteca.sql
```

### 🔹 Passo 2 — Iniciar o backend

```bash
python backend.py
```

Servidor aberto em:

```
http://127.0.0.1:5001/
```

### 🔹 Passo 3 — Abrir a interface web

Abra:

```
web.ui.html
```

### 🔹 Passo 4 — Login

* **Admin:** CRUD completo
* **Leitor:** somente visualização

---

## 📌 8. Regras Importantes

* Um usuário não pode pegar o mesmo livro sem devolver antes → constraint no banco.
* Trigger registra todas as ações.
* Ao registrar devolução: `devolvido = TRUE`, data atual aplicada.
* Frontend bloqueia funções de admin para leitores.
* Token é removido no logout.

---

## 📌 9. Possíveis Melhorias Futuras

* Tema escuro / claro
* Dashboard com gráficos
* Suporte a anexos
* JWT real
* PWA
* Versão mobile

---

## 📌 10. Autor

Projeto desenvolvido para fins educacionais, abordando:

* Modelagem de dados
* API REST
* Backend Python
* Interface Web
* Integração com PostgreSQL
