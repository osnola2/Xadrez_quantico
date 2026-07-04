# 📜 Regras e Mecânicas do Xadrez Simultâneo

Este documento detalha as propostas de regras e resolução de conflitos para a nossa variante de **Xadrez Simultâneo**. Como ambas as jogadas de uma rodada são reveladas e executadas exatamente ao mesmo tempo, regras especiais são necessárias para tratar interações entre peças em movimento.

---

## 1. O Ciclo da Rodada (Turno Síncrono)

1. **Fase de Planejamento (Cronômetro Ativo):**
   * O cronômetro da rodada (sugestão: 15 ou 30 segundos) inicia a contagem regressiva.
   * Ambos os jogadores podem selecionar qualquer jogada que seja legal no estado *atual* do tabuleiro.
   * Ao confirmar a jogada, a decisão é enviada secretamente ao servidor. O oponente recebe um aviso de que você está "Pronto", mas não vê sua jogada.
2. **Fase de Resolução:**
   * Ocorre quando **ambos submetem** suas jogadas ou quando **o cronômetro zera**.
   * O servidor calcula a interação entre as duas jogadas e atualiza o tabuleiro instantaneamente para o novo estado.

---

## 2. Propostas de Resolução de Conflitos (Para Discussão)

Abaixo estão os 4 principais cenários de conflito em um turno simultâneo e as propostas para debate com os idealizadores do projeto:

### 💥 Cenário A: Colisão na Mesma Casa (Destino Comum)
* **O que acontece:** O jogador Branco move um Cavalo para `d5` e o jogador Preto move um Peão para a mesma casa `d5` na mesma rodada.
* **Proposta 1 (Aniquilação Mútua - Recomendada):** O choque de duas peças na mesma casa gera uma explosão! Ambas as peças são capturadas e removidas do jogo, deixando a casa `d5` vazia.
* **Proposta 2 (Hierarquia de Força):** A peça de maior valor (Dama > Torre > Bispo/Cavalo > Peão) sobrevive e ocupa a casa, destruindo a menor. Se tiverem o mesmo valor, ambas são destruídas.
* **Proposta 3 (Física Quântica / Sorte):** Cada peça tem 50% de probabilidade de ocupar a casa, capturando a outra.

### 💨 Cenário B: Esquiva / Alvo em Movimento
* **O que acontece:** O Branco tenta capturar um Bispo preto em `e5` (movendo sua Torre para `e5`). No entanto, na mesma rodada, o Preto decidiu mover esse Bispo de `e5` para `g7`.
* **Regra Proposta:** A Torre branca conclui seu movimento para a casa `e5` (que agora está vazia), sem realizar captura. O Bispo preto escapa ileso para `g7`. O ataque branco falhou porque o alvo se moveu!

### 🔄 Cenário C: Cruzamento de Posições
* **O que acontece:** Duas peças inimigas trocam de posição na mesma linha/coluna/diagonal diretamente. Exemplo: Torre branca vai de `e1` para `e8`, e Torre preta vai de `e8` para `e1`.
* **Regra Proposta:** As peças "passam uma pela outra" em sentidos opostos sem se chocarem, terminando suas jogadas com sucesso em suas novas casas.

### ⏱️ Cenário D: Falta de Jogada no Tempo Limite (Timeout)
* **O que acontece:** O cronômetro chega a zero e um dos jogadores não escolheu/confirmou sua jogada.
* **Regra Proposta:** O jogador que não submeteu passa a vez naquela rodada. Apenas a jogada do oponente que submeteu no tempo correto é executada no tabuleiro.

---

## 3. Condição de Vitória: A Queda do Rei 👑

No xadrez tradicional, não se pode fazer uma jogada que deixe o próprio Rei em xeque, e o jogo termina em Xeque-Mate ou Afogamento.

Em **Xadrez Simultâneo**:
* **Aviso de Perigo:** Se o Rei de um jogador estiver sob ataque (linha de visão enemiga), o tabuleiro exibirá um alerta visual na casa do Rei.
* **Captura Direta (Proposta):** Como as jogadas acontecem ao mesmo tempo, se você mover seu Rei para uma casa atacada por uma peça inimiga — ou se esquecer de tirar o Rei da linha de ataque —, o oponente poderá **capturar o seu Rei diretamente na jogada seguinte**, vencendo a partida imediatamente!

---

## 🗣️ Deixe seu Feedback
Sinta-se à vontade para comentar ou abrir uma Issue sugerindo alterações ou novas variantes quânticas para adicionarmos a essas regras!
