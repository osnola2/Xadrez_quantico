# Manual Oficial do Xadrez Quântico & Simultâneo

Bem-vindo a uma nova dimensão do xadrez. Aqui, as regras clássicas são apenas a base; o tempo, o espaço e a incerteza governam o tabuleiro. Este documento reflete o estado exato e atual do motor do jogo.

---

## 1. O Princípio da Simultaneidade
Não existem turnos alternados. As Brancas e as Pretas **escolhem suas jogadas ao mesmo tempo**, de forma secreta, dentro de um limite de tempo (que pode variar de 30s a 5min).
- O estado do tabuleiro só é resolvido e atualizado **após** ambos submeterem suas jogadas (ou o relógio zerar).
- Como consequência, você deve prever não só a resposta do seu oponente, mas o que ele está fazendo no exato instante em que você age.

---

## 2. Movimentação e Capturas Padrões
Se uma peça se mover para uma casa vazia ou ocupada por uma peça que permaneceu parada, ela se comporta como no xadrez clássico (move-se ou captura o alvo).
No entanto, por conta da simultaneidade, os **Peões** ganham interações físicas reais:
- **Golpe no Vento:** Se um peão tentar capturar na diagonal, mas a peça inimiga que estava lá também se moveu para outro lugar no mesmo turno, o peão "bate no vento". Ele falha em se mover e retorna para sua casa original.
- **Bloqueio Físico:** Se um peão tentar avançar um passo à frente, mas a casa de destino for subitamente ocupada por uma peça inimiga no mesmo turno, o peão é "bloqueado" e permanece em sua casa original.

---

## 3. Colisões Quânticas (Aniquilação Mútua)
O que acontece quando duas forças irrefreáveis se encontram no mesmo ponto do espaço-tempo?
Se ambas as peças (uma Branca e uma Preta) se moverem para a **MESMA casa de destino** no mesmo turno, ocorre uma Colisão Quântica.
- **Resultado:** O espaço não comporta as duas. Ambas colidem, explodem e são **completamente aniquiladas**, sendo removidas do tabuleiro!

---

## 4. A Regra de Emboscada de Peões
Existe uma exceção elegante à regra de Aniquilação Mútua, baseada na geometria do ataque do peão:
Se um Peão ataca uma casa na diagonal e, no exato mesmo turno, uma peça inimiga se move de forma reta para essa mesma casa de destino, **não há colisão**.
- **Resultado:** O peão estava "mirando" naquele quadrado. Ele intercepta o alvo em movimento e **realiza a captura com sucesso** (a peça recém-chegada é destruída e o peão toma a casa).

---

## 5. Penalidade por Estouro de Tempo
Se o tempo acabar e você não tiver confirmado sua jogada, você simplesmente **perde a vez** naquele turno, ficando imóvel enquanto o oponente realiza a jogada dele.

---

## 6. O Roque Simultâneo
O Roque no xadrez quântico movimenta tanto o Rei quanto a Torre no mesmo microssegundo. 
Se você rocar e o oponente atacar:
- A casa final do Rei será resolvida normalmente.
- Se o oponente mover uma peça exatamente para a casa em que sua Torre vai parar após pular o Rei, ocorre uma Colisão Quântica específica na Torre! A Torre e a peça agressora são aniquiladas, mas seu Rei permanece a salvo.

---

## 7. Condição de Vitória (A Queda dos Reis)
O objetivo do jogo continua sendo a destruição do Rei adversário, que agora pode ocorrer via captura normal ou aniquilação em colisões.
- Aquele que destruir o Rei inimigo primeiro ganha a partida.
- Se, por um acaso do destino, **ambos os Reis forem capturados ou aniquilados no mesmo turno** (seja porque os Reis colidiram, ou porque dois ataques letais foram coordenados no mesmo turno), a partida terminará em um glorioso **Empate**!
