# Teste Técnico - API de Cancelamento de Contrato

## Requisitos

- Python 3.12 ou maior
- uv
- docker & docker compose

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

## Pontos de melhoria

- Não retornar a entidade de contrato, mas sim o ID. Não revelar
  comportamento interno do sistema
