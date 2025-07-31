# Guia de Contribuição - Painel de Laboratório HSF

Agradecemos o interesse em contribuir para o desenvolvimento do Painel de Laboratório. Sua ajuda é valiosa para melhorar esta ferramenta para toda a equipe.

Para garantir um processo de colaboração organizado e eficiente, pedimos que siga as diretrizes abaixo.

## Como Contribuir

### Reportando Bugs ou Sugerindo Melhorias

Se você encontrar um bug, tiver uma ideia para uma nova funcionalidade ou uma sugestão de melhoria, o processo é simples:

1.  **Abra uma Issue:** A forma preferencial de comunicação é através da abertura de uma *Issue* no repositório do projeto.
2.  **Use um Título Claro:**
    *   Para bugs: `Bug: Descrição curta do problema`
    *   Para sugestões: `Sugestão: Descrição curta da melhoria`
3.  **Descreva com Detalhes:**
    *   **Para Bugs:** Forneça os passos para reproduzir o erro, o que você esperava que acontecesse e o que de fato aconteceu. Se possível, inclua screenshots ou logs do terminal.
    *   **Para Sugestões:** Explique o problema que sua ideia resolve e como você imagina que a funcionalidade deveria se comportar.

## Contribuindo com Código

Se você deseja escrever código para corrigir um bug ou implementar uma funcionalidade, siga este fluxo de trabalho.

### 1. Crie uma Branch

Nunca trabalhe diretamente na `main` ou `master`. Crie uma nova *branch* a partir da `main` com um nome descritivo.

-   Para uma nova funcionalidade: `feature/nome-da-funcionalidade`
-   Para uma correção de bug: `fix/descricao-do-bug`

```bash
# Exemplo para uma nova funcionalidade
git checkout -b feature/filtro-por-setor
```

### 2. Desenvolva

-   **Escreva seu código:** Faça as alterações necessárias.
-   **Mantenha o estilo do código:** Siga as convenções e o estilo de codificação já existentes no projeto.
-   **Teste suas alterações:** Garanta que sua modificação não quebra nenhuma funcionalidade existente e que funciona como esperado.

### 3. Faça o Commit e o Push

-   **Adicione suas alterações:** Faça o `git add` dos arquivos que você modificou.
-   **Faça o commit:** Escreva uma mensagem de commit clara e concisa.
    ```bash
    git commit -m "Feat: Adiciona filtro por setor na página do Pronto Socorro"
    ```
-   **Envie para o repositório:**
    ```bash
    git push origin feature/filtro-por-setor
    ```

### 4. Crie um Pull Request (PR)

-   No GitHub/GitLab, crie um *Pull Request* da sua *branch* para a `main`.
-   Preencha a descrição do PR, resumindo as alterações e referenciando a *Issue* correspondente (ex: `Resolve #12`).
-   Designe um ou mais membros da equipe para revisar seu código.

Obrigado por sua contribuição!
