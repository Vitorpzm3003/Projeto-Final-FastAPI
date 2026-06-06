# Sistema de Gestão de Pedidos e Caixa

Este projeto é uma Aplicação Web completa desenvolvida como Trabalho Prático Semestral para a disciplina de Arquitetura de Aplicações Web.

## Visão Geral e Domínio
A aplicação foca no domínio de **Gestão de Vendas (Restaurantes/Lojas)**. O sistema gerencia toda a jornada do pedido: desde o cadastro de produtos (catálogo), criação de pedidos com carrinho de compras assíncrono, até a gestão financeira no Caixa (registro de formas de pagamento como PIX, Dinheiro, etc) e Histórico.

Possui as seguintes entidades principais inter-relacionadas:
- Usuários (com níveis de acesso Administrativo e Normal)
- Produtos
- Pedidos
- Itens do Pedido

## Tecnologias e Stack
- **Backend:** Python + FastAPI (REST API assíncrona)
- **Banco de Dados:** SQLite (com SQLAlchemy ORM) - *Exceção homologada para a disciplina.*
- **Frontend:** HTML5, Bootstrap 5 e Vanilla JavaScript (SPA via `fetch`).
- **Segurança:** Autenticação via JWT (JSON Web Tokens) e hash de senhas com Bcrypt.

---

## Pré-requisitos
Para executar o projeto, você precisará de:
- **Python 3.8+** instalado.
- Ferramenta para gerenciar pacotes, como `pip`.

## Instalação e Execução (Passo a Passo)

1. **Clone o repositório:**
   Baixe ou clone o código para sua máquina local.

2. **Instale as dependências:**
   No terminal, dentro da pasta raiz do projeto, instale os pacotes necessários:
   ```bash
   pip install fastapi uvicorn sqlalchemy passlib[bcrypt] python-jose python-dotenv pytest httpx
   ```

3. **Configuração das Variáveis de Ambiente:**
   Crie um arquivo chamado `.env` na raiz do projeto contendo sua chave secreta para geração dos tokens JWT.
   Exemplo de conteúdo do `.env`:
   ```env
   SECRET_KEY=sua_chave_secreta_super_segura_aqui_123
   ```

4. **Inicie o Servidor Backend:**
   No terminal, execute o Uvicorn para ligar a API:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

5. **Acesse o Sistema Front-end:**
   Basta acessar no seu navegador: `http://127.0.0.1:8000/`

---

## Documentação da API (Swagger)
O FastAPI gera automaticamente a documentação padrão OpenAPI. Com a aplicação rodando localmente, acesse:
- **Interface Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentação ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Lá você encontrará todas as rotas de GET, POST, PATCH e DELETE, bem como os Schemas de requisição exigidos.

---

## Testes Unitários
O projeto contempla testes automatizados que simulam requisições HTTP e validam as regras de negócio sem afetar o banco de dados oficial (utilizando um banco em memória).

Para rodar os testes unitários, basta abrir o terminal na raiz do projeto e digitar:
```bash
pytest
```
