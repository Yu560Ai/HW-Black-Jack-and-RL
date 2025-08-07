import random
random.seed(42)


player_cards = []
dealer_cards = []
player_sum = 0
dealer_sum = 0
deck = [1,2,3,4,5,6,7,8,9,10,10,10,10] * 4  # HW2定义：1副牌
random.shuffle(deck)


# 游戏核心函数（符合HW2规则）
def calculate_sum(cards: list):
    """计算手牌总和，处理A的11/1转换（HW2定义）"""
    total = sum(cards)
    num_aces = cards.count(1)
    while total <= 21 and num_aces > 0:
        if total + 10 <= 21:
            total += 10
            num_aces -= 1
        else:
            break
    return total

def has_usable_ace(cards: list):
    """判断是否有可用A（HW2定义：A按11点算不爆牌）"""
    total = sum(cards)
    return 1 in cards and (total + 10) <= 21

def reset():
    """初始化游戏，返回有效状态（HW2定义：玩家点数12-21）"""
    global deck, player_sum, dealer_sum, player_cards, dealer_cards
    if len(deck) <= 15:
        deck = [1,2,3,4,5,6,7,8,9,10,10,10,10] * 4
        random.shuffle(deck)
    player_cards.clear()
    dealer_cards.clear()
    # 发初始牌
    player_cards.append(deck.pop())
    player_cards.append(deck.pop())
    dealer_cards.append(deck.pop())
    dealer_cards.append(deck.pop())
    # 计算初始点数
    player_sum = calculate_sum(player_cards)
    dealer_sum = calculate_sum(dealer_cards)
    # 处理黑杰克（HW2规则）
    if player_sum == 21:
        return (None, 0) if dealer_sum == 21 else (None, 1)
    # 自动要牌直到玩家点数≥12（HW2定义的有效状态）
    while player_sum < 12:
        player_cards.append(deck.pop())
        player_sum = calculate_sum(player_cards)
    # 构建状态（玩家点数, 庄家明牌, 可用A）
    state = (player_sum, dealer_cards[0], has_usable_ace(player_cards))
    return state, 0

def step(action: str):
    """执行动作，返回新状态和奖励（遵循HW2庄家策略）"""
    global player_sum, dealer_sum
    if action == 'hit':
        # 玩家要牌（HW2规则）
        player_cards.append(deck.pop())
        player_sum = calculate_sum(player_cards)
        if player_sum > 21:  # 玩家爆牌
            return None, -1
        # 确保状态有效（≥12点）
        while player_sum < 12:
            player_cards.append(deck.pop())
            player_sum = calculate_sum(player_cards)
        new_state = (player_sum, dealer_cards[0], has_usable_ace(player_cards))
        return new_state, 0
    else:  # stick（停牌）
        # 庄家策略（HW2定义：≤16点要牌，≥17点停牌）
        while dealer_sum < 17:
            dealer_cards.append(deck.pop())
            dealer_sum = calculate_sum(dealer_cards)
        # 判断胜负（HW2规则）
        if dealer_sum > 21:  # 庄家爆牌
            return None, 1
        elif dealer_sum > player_sum:
            return None, -1
        elif dealer_sum < player_sum:
            return None, 1
        else:
            return None, 0


# HW3策略改进与Q值存储
def initial_policy(state):
    """HW3指定初始策略：≥20点停牌，否则要牌"""
    player_sum, _, _ = state
    return 'stick' if player_sum >= 20 else 'hit'

def policy_improvement(num_epi=100000, gamma=0.999, alpha=0.01):
    # 初始化Q值字典（存储所有状态-动作对的Q值）
    Q = {}
    # 有效状态集合
    all_states = [
        (p, d, a) 
        for p in range(12, 22)  # 玩家点数12-21
        for d in range(1, 11)   # 庄家明牌1-10
        for a in [True, False]  # 有无可用A
    ]

    # 初始化策略字典
    policy_dict = {s: initial_policy(s) for s in all_states}

    for i in range(num_epi):
        if i % 20000 == 0:
            print(f'TD(0)进度 (γ={gamma}): {i}/{num_epi}')

        state, _ = reset()
        if state is None:
            continue

        while state is not None:
            action = policy_dict[state]
            next_state, reward = step(action)

            # 初始化当前Q值
            if (state, action) not in Q:
                Q[(state, action)] = 0.0

            # 计算TD目标
            if next_state is not None:
                next_action = policy_dict[next_state]
                if (next_state, next_action) not in Q:
                    Q[(next_state, next_action)] = 0.0
                td_target = reward + gamma * Q[(next_state, next_action)]
            else:
                td_target = reward

            # 更新Q值（HW3 TD(0)公式）
            Q[(state, action)] += alpha * (td_target - Q[(state, action)])

            # 策略改进（贪心选择最优动作）
            actions = ['hit', 'stick']
            q_vals = [Q.get((state, a), 0.0) for a in actions]
            best_action = actions[q_vals.index(max(q_vals))]
            policy_dict[state] = best_action

            state = next_state

    # 按顺序写入所有Q值到文件（状态排序后存储）
    with open('HW3_Q3_all_q_values.txt', 'w') as f:
        f.write("所有Q值（按状态-动作对排序）：\n")
        # 按状态和动作排序（玩家点数→庄家明牌→可用A→动作）
        sorted_q = sorted(Q.items(), key=lambda x: (x[0][0][0], x[0][0][1], x[0][0][2], x[0][1]))
        for (state, action), q_val in sorted_q:
            f.write(f"Q{state, action}: {q_val:.4f}\n")

    # 写入状态-动作策略到文件
    with open('HW3_Q3_policy_result.txt', 'w') as f:
        f.write("每个状态的最优动作（HW2定义的200个状态）：\n")
        for state in sorted(all_states):
            f.write(f"状态{state}: 最优动作={policy_dict[state]}\n")

    return policy_dict, Q


if __name__ == '__main__':
    # 运行HW3策略改进，生成Q值文件
    improved_policy, all_Q = policy_improvement(num_epi=100000, gamma=0.999, alpha=0.01)
    print("Q值已全部写入 all_q_values.txt，策略写入 policy_result.txt")