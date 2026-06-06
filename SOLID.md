# Princípios SOLID Aplicados

No desenvolvimento deste projeto backend (FastAPI), focamos em aplicar as melhores práticas de Engenharia de Software. Abaixo estão descritos três dos cinco princípios SOLID que foram implementados com clareza no código.

## 1. Single Responsibility Principle (SRP) - Princípio da Responsabilidade Única
**O que é:** Uma classe, arquivo ou módulo deve ter apenas um motivo para mudar, assumindo apenas uma responsabilidade dentro do domínio.
**Onde aparece no código:** Todo o nosso projeto é fatiado por responsabilidades.
- `models.py`: Responsável *exclusivamente* por ditar a estrutura das tabelas no banco de dados.
- `schemas.py`: Responsável *exclusivamente* por ditar como os dados trafegam na rede (validações Pydantic).
- `dependencies.py`: Lida apenas com injeções de código (como obter a sessão do banco e validar Tokens JWT).
- **Justificativa:** Se mudarmos a forma como validamos um e-mail na API, alteramos o `schemas.py`. Se adicionarmos uma coluna no banco, alteramos `models.py`. As lógicas não se misturam, mantendo o código limpo e coeso.

## 2. Dependency Inversion Principle (DIP) - Princípio da Inversão de Dependência
**O que é:** Entidades de alto nível não devem depender de entidades de baixo nível; ambas devem depender de abstrações. Detalhes devem depender de abstrações.
**Onde aparece no código:** Nas injeções de dependência das nossas Rotas (`Depends`).
- Em `order_routes.py` ou `auth_routes.py`, as rotas recebem a sessão do banco de dados através de `session: Session = Depends(pegar_sessao)` em vez de instanciar o objeto do banco diretamente dentro da função.
- **Justificativa:** Isso desacopla a regra de negócio da infraestrutura de banco. Como a rota depende apenas de uma injeção (`Depends`), podemos facilmente (durante os testes unitários via `pytest`, por exemplo) substituir o `pegar_sessao` por um banco SQLite falso em memória, sem precisarmos alterar sequer uma linha do arquivo de rotas.

## 3. Interface Segregation Principle (ISP) - Princípio da Segregação de Interface
**O que é:** Clientes não devem ser forçados a depender de métodos/interfaces que não utilizam.
**Onde aparece no código:** Na forma como modelamos os `schemas.py` de resposta e atualização.
- **Exemplo prático:** Ao invés de termos um único "Modelo de Usuário Gigante" usado para criar, ler e atualizar, nós o segregamos.
  - O `UsuarioSchema` obriga o envio de todos os dados (nome, email, senha, etc).
  - O `UsuarioUpdate` torna os campos `Optional` (opcionais).
- **Justificativa:** Quando a interface do Frontend precisa fazer a ação de *PATCH* (apenas editar o nome de um usuário sem resetar a senha), ela não é forçada a enviar os dados da senha e do perfil. A interface do contrato (`UsuarioUpdate`) foi desenhada estritamente para não forçar o cliente a passar atributos que ele não quer manipular naquele fluxo.
