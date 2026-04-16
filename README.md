# Teste Técnico - API de Cancelamento de Contrato

## Requisitos

- Python 3.12 ou maior
- uv
- docker & docker compose

## Passos para execução local

- Criar arquivo `.env`. Ver exemplo
- Executar `uv sync`
- Criar banco de dados postgresql
- Executar o script `seed_database.py` ao menos um vez. Ex.: `python -m scripts.seed_database`
- Executar a aplicação com o seguinte comando: `uv run uvicorn app.main:app`

## Passos para execução em docker

- docker compose up -d --build
- Conferir `http://localhost:8000/docs`

## Exemplo de `.env`

```[bash]
DEPLOY_MODE="DEVELOPMENT"
DATABASE_URL="postgresql://cancellation:cancellation@localhost:5555/cancellation"
MINIMUM_POOL_SIZE=1
MAXIMUM_POOL_SIZE=10
```

## Comportamento

O comportamento do sistema foi descrito utilizando a linguagem Guerkin. Onde
`Funcionalidade` descreve o que está sendo testado e o `Cenário` apresenta um
exemplo específico de comportamento. Os passos de um dado cenário utiliza as
seguintes palavras-chave:

- Dado: Define o estado inicial ou pré-condição
- Quando: Descreve a ação ou evento principal
- Então: Descreve o resultado esperado
- E/Mas: Adicionam mais condições sem repetir as palavras anteriores

### Funcionalidade: Criação de contrato

```[plain]
Cenário: Criação de contrato realizado com sucesso
    Dado um contrato válido
    Quando executada a operação de criação
    Então o sistema deve retornar o contrato criado com o status "CREATED"
```

### Funcionalidade: Criação de requerimento de cancelamento de contrato

```[plain]
Cenário: Criação de requerimento de cancelamento de contrato com sucesso
    Dado um contrato existênte com o status "CREATED"
        E uma chave de idempotência válida
        E requerimento feito até 7 dias após a criação do contrato
        E contrato possui valor reembolsável maior que zero
    Quando executada a operação de criação
    Então o sistema deve retornar uma mensagem de sucesso
        E status do requerimento deve ser "SUCCESS"
```

```[plain]
Cenário: Duplicação de requerimento de cancelamento de contrato
    Dado um contrato existênte com o status "CREATED"
        E uma chave de idempotência válida existênte
    Quando executada a operação de criação
    Então o sistema deve retornar o status do requerimento existênte
```

```[plain]
Cenário: Criação de requerimento de cancelamento de contrato com contrato cancelado
    Dado um contrato existênte com o status "CANCELLED"
    Quando executada a operação de criação
    Então o sistema deve retornar uma mensagem de sucesso
```

```[plain]
Cenário: Falha na criação de requerimento de cancelamento de contrato, requerimento
realizado após 7 dias da data de criação do contrato
    Dado um contrato existênte com o status "CREATED"
        E uma chave de idempotência válida
        E requerimento feito após 7 dias da data criação do contrato
    Quando executada a operação de criação
    Então o sistema deve retornar um erro
        E status do requerimento deve ser "FAILED"
```

```[plain]
Cenário: Falha na criação de requerimento de cancelamento de contrato,
requerimento realizado para contrato sem valor reembolsável
    Dado um contrato existênte com o status "CREATED"
        E uma chave de idempotência válida
        E requerimento feito até 7 dias após a criação do contrato
        E contrato possui valor reembolsável menor ou igual à zero
    Quando executada a operação de criação
    Então o sistema deve retornar um erro
        E status do requerimento deve ser "FAILED"
```

### Funcionalidade: Reprocessar contrato

```[plain]
Cenário: Reprocessamento de contrato com sucesso
    Dado um contrato existênte com o status "PROCESSING"
        E faz mais de 5 minutos desde a última atualização
    Quando executada a operação de reprocessamento
    Então o sistema deve retornar sucesso
        E status do contrato deve ser "CREATED"
```

```[plain]
Cenário: Falha no reprocessamento de contrato, contrato atualizado a menos
de 5 minutos
    Dado um contrato existênte com o status "PROCESSING"
        E a última atualização do contrato foi a menos de 5 minutos
    Quando executada a operação de reprocessamento
    Então o sistema deve retornar uma mensagem de falha
```

```[plain]
Cenário: Falha no reprocessamento de contrato, contrato com status diferente
de "PROCESSING"
    Dado um contrato existênte com o status diferente de "PROCESSING"
    Quando executada a operação de reprocessamento
    Então o sistema deve retornar uma mensagem de falha
```

## Decisões técnicas

- Não utilização de ORM para evitar classes anêmicas e incentivar o desenvolvimento
  guiado pelo comportamento
- Foi aplicado TDD e BDD
- Os testes seguiram os princípios FIRST:
  1.Rápidos - Fast
  2.Independentes - Independent
  3.Determinísticos - Repeatable
  4.Auto-verificáveis - Self-Validating
  5.Oportunos - Timely (TDD)
- As mudanças de status do contrato e da requisição de cancelamento foram
  inspirados em máquinas de estado
- Foi utilizado o padrão Query Object para as queries, o que incentiva a
  organização do código
- Assim como o pydantic previne problemas de tipo com os dados do cliente, o
  `restore` das entidades restaura o estado do objeto pelo banco de dados
  previnindo possíveis problemas de tipo com o uso de `assert`
- Os `services` foram quebrados em casos de uso para evitar `God Classes`
- A duplicação de requerimentos de cancelamento com mesma chave de idempotência
  foi evitado em nível de banco de dados através do uso de `ON CONFLICT (idempotency_key)`
- A duplicação de requerimentos de cancelamento com diferents chaves de idempotência
  foi considerado um requerimento novo válido. Porém para evitar a sobreposição
  inválida de status, existe uma checagem do status esperado que deve corresponder
  ao comportamento da entidade de contrato para a mudança ser bem sucedida

## Pontos de melhoria

- Não retornar a entidade de contrato, mas sim o ID. Não revelar
  comportamento interno do sistema
- Executar o processamento do contrato em backgroung e dar uma resposta imediata
  ao cliente
- Utilização de banco em memória para os testes
- Utilização de contâiner de injeção de dependência
