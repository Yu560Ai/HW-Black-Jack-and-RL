import random
random.seed(42)

player_cards = []
dealer_cards = []
player_sum = 0
dealer_sum = 0
deck = [1,2,3,4,5,6,7,8,9,10,10,10,10] * 4
random.shuffle(deck)


def calculate_sum(cards: list):
    # 计算手牌和
    total = sum(cards)
    num_aces = cards.count(1)

    while total <= 21 and num_aces > 0:
        if total + 10 <= 21:
            total += 10
            num_aces -= 1
        else:
            break
    return total

def has_uasable_ace (cards: list):
    # 判断是否有有用的ace
    total = sum(cards)
    return 1 in cards and (total + 10) <= 21

def reset():
    #重置游戏
    global deck, player_sum, dealer_sum, player_cards, dealer_cards
    if len(deck) <= 15: 
        #当牌不够的时候重新洗牌
        deck = [1,2,3,4,5,6,7,8,9,10,10,10,10] * 4
        random.shuffle(deck)

    #新一轮游戏开始，清空手牌
    player_cards.clear()
    dealer_cards.clear()        

    #玩家和庄家各发两张牌
    player_cards.append(deck.pop())
    player_cards.append(deck.pop())
    dealer_cards.append(deck.pop())
    dealer_cards.append(deck.pop())

    player_sum = calculate_sum(player_cards)
    dealer_sum = calculate_sum(dealer_cards)
    if player_sum == 21:
        if dealer_sum == 21:
            return None, 0
        else:
            return None, 1
    # 自动要牌直到玩家点数≥12（HW2定义的有效状态）
    while player_sum < 12:
        player_cards.append(deck.pop())
        player_sum = calculate_sum(player_cards)    
    state = (player_sum, dealer_cards[0], has_uasable_ace(player_cards))
    return state, 0

def step(player_cards: list, dealer_cards: list, action: str):
    global player_sum, dealer_sum
    if action == 'hit':
        player_cards.append(deck.pop())
        player_sum = calculate_sum(player_cards)

        if player_sum > 21:
            return None, -1
        
        new_state = (player_sum, dealer_cards[0], has_uasable_ace(player_cards))

        return new_state, 0
    
    elif action == 'stick':
        while dealer_sum < 17:
            dealer_cards.append(deck.pop())
            dealer_sum = calculate_sum(dealer_cards)

        if dealer_sum > 21:
            return None, 1
        elif dealer_sum > player_sum:
            return None, -1
        elif dealer_sum < player_sum:
            return None, 1
        else:
            return None, 0
        

def td0(num_epi = 100000, gamma = 0.999, alpha = 0.01):
    values = {}

    for i in range(num_epi):
        if i % 20000 == 0:
            print(f'TD(0)进度 (discount = {gamma}): {i}/{num_epi}')

        init_state, _ = reset()
        state = init_state

        if state is None:
            continue

        while state is not None:
            if state not in values:
                values[state] = 0
            
            player_sum = state[0]
            action = 'stick' if player_sum >= 20 else 'hit'

            next_state, reward = step(player_cards, dealer_cards, action)

            if next_state is None:
                td_target = reward
            else:
                if next_state not in values:
                    values[next_state] = 0
                td_target = reward + gamma * values[next_state]

            values[state] += alpha * (td_target - values[state])
            state = next_state
    
    return values

if __name__ == '__main__':
    gammas = [0.999, 0.9, 0.8]
    gamma_values = {}

    for g in gammas:
        print(f'\n开始计算 gamma = {g} 的状态值...')
        gamma_values[g] = td0(gamma=g)

    all_states = set()
    for values in gamma_values.values():
        all_states.update(values.keys())
    sorted_states = sorted(all_states)

    with open ('HW3_Q1_TD_blackjack_values.txt','w') as f:
        f.write("状态\t")
        f.write("\t".join([f"γ={g}" for g in gammas]) + "\n")
        for state in sorted_states:
            f.write(f"{state}\t")
            # 依次写入每个γ下的状态值（保留4位小数）
            row_values = [f"{gamma_values[g].get(state, 0.0):.4f}" for g in gammas]
            f.write("\t".join(row_values) + "\n")
        
        
