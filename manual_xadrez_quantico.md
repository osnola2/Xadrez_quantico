# 🌌 Manual do Xadrez Quântico (Simultâneo)

Bem-vindo ao **Xadrez Quântico**, uma variante de xadrez em tempo real baseada em turnos simultâneos e física de colisão. O tabuleiro pode parecer o mesmo, mas a estratégia muda completamente quando a mente do seu oponente e a sua agem no exato mesmo milissegundo!

---

## ⏱️ 1. A Mecânica de Turnos Simultâneos
Diferente do xadrez clássico (onde as Brancas jogam, depois as Pretas), aqui **ambos os jogadores jogam ao mesmo tempo**.
- Durante um turno (Round), ambos os jogadores escolhem e enviam seu movimento em segredo.
- O jogo aguarda até que os dois jogadores tenham enviado (Submit) suas jogadas.
- Assim que ambos confirmam, o servidor resolve as duas jogadas no **mesmo instante**.

---

## ♟️ 2. Movimentos e Intenções (Movimentos Pseudo-Legais)
Como você não sabe para onde a peça inimiga vai, o jogo permite movimentos baseados em **intenção**:
- **Bloqueio Inimigo:** Se uma peça inimiga está bloqueando o seu caminho (ex: um peão na frente do seu), você **pode** mandar sua peça ir para aquela casa! Se o inimigo tirar a peça dele de lá naquele turno, sua peça ocupará o espaço vazio com sucesso.
- **Fogo Amigo Proibido:** Você não pode ordenar que uma peça sua vá para uma casa onde já existe uma peça **aliada**. Como você só tem uma jogada por turno, a sua peça aliada não terá como sair da frente!
- **Ataques no Escuro:** Seus peões podem tentar capturar na diagonal em casas que atualmente estão vazias, antecipando que o inimigo moverá uma peça para lá.

---

## 💥 3. Resolução e Física do Tabuleiro
Quando os dois movimentos são revelados, o servidor aplica as seguintes regras de colisão:

### 3.1. Aniquilação Mútua (Colisão Direta)
Se os dois jogadores tentarem mover suas peças para a **mesma exata casa** no mesmo turno:
- **Colisão Crítica!** As duas peças batem de frente no meio do caminho.
- Ambas as peças são **destruídas** (Aniquiladas) e removidas do tabuleiro. Ninguém fica com a casa!

### 3.2. Emboscada de Peões (Exceção de Colisão)
Existe uma exceção à regra de Aniquilação Mútua exclusiva para peões:
- Se um peão ataca **na diagonal** para uma casa...
- E no mesmo instante, o peão inimigo avança **para a frente** (movimento vertical) para aquela mesma casa...
- **Vitória do Atacante!** O peão que atacou na diagonal "embosca" o peão que estava apenas correndo para frente. O atacante sobrevive e captura o peão inimigo!
- *(Nota: Se ambos os peões atacarem na diagonal para a mesma casa, a regra de Aniquilação Mútua volta a valer).*

### 3.3. Peões: Bloqueios e Golpes no Vento
Os peões possuem uma física especial de combate:
- **🛡️ Bloqueio (Falha de Avanço):** Se o seu peão tentar avançar para frente, mas o oponente **não** tirar a peça dele da frente, o seu peão colide com ela, o movimento falha, e o seu peão recua para a casa original perdendo o turno.
- **💨 Vento (Falha de Captura):** Se o seu peão atacar na diagonal, mas o oponente for esperto e remover a peça dele a tempo, o seu peão golpeia o vazio, o ataque falha, e o peão recua para a casa original.

### 3.3. Capturas Padrão
Se a sua peça pousar na casa do inimigo e ele não moveu a peça daquela casa, a peça dele é **capturada normalmente**, exatamente como no xadrez padrão.

### 3.5. Penalidade por Tempo (Reversão Temporal)
O tempo é implacável no nível quântico. Se o tempo da rodada se esgotar e você não tiver enviado uma jogada, **o universo pune a sua inatividade com uma Reversão Temporal!**
- O sistema varrerá o seu histórico para encontrar a **última peça** que você moveu e que ainda está viva no tabuleiro.
- Essa peça será **forçada a fazer o movimento inverso** de volta para a casa de onde veio!
- Esse movimento entra na resolução simultânea normalmente (podendo causar colisões ou ser bloqueada).
- **Desvantagem na Colisão:** Se a sua peça estiver sofrendo uma Reversão Temporal e colidir com uma peça inimiga que está avançando para a mesma casa, a sua peça revertida perde o embate e é aniquilada, enquanto a peça inimiga sobrevive e toma a casa!
- *(Se for o turno 1, ou se você não tiver peças com histórico válido, você apenas perderá o turno).*

---

## 🏆 4. Fim de Jogo
Esqueça as regras complexas de Xeque e Xeque-Mate. No Xadrez Quântico, a sobrevivência do Rei é brutal e direta:
- **Morte do Rei:** A partida acaba no instante em que o Rei de um jogador é **capturado** ou **aniquilado** em uma colisão.
- **Empate Quântico (Morte Mútua):** Se ocorrer uma loucura onde **ambos** os Reis morrem no mesmo exato turno (seja por aniquilação mútua ou capturas cruzadas simultâneas), a partida termina em um empate épico!
- **Desistência:** A qualquer momento, um jogador pode apertar a bandeira de desistir (Resign) para encerrar a partida e ceder a vitória ao oponente.
- Ao final da partida, você pode iniciar um novo jogo instantaneamente, reiniciando o tabuleiro para ambos os jogadores sem precisar recarregar a sala.
