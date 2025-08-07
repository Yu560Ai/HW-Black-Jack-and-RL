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
    return state

def step(player_cards: list, dealer_cards: list, action: str):
    global player_sum, dealer_sum
    if action == 'hit':
        player_cards.append(deck.pop())
        player_sum = calculate_sum(player_cards)

        if player_sum > 21:
            return None, -1
        
        while player_sum < 12:
            player_cards.append(deck.pop())
            player_sum = calculate_sum(player_cards)
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
        
def simulation():
    init = reset()
    # print(f'player cards: {player_cards}')
    # print(f'dealer cards: {dealer_cards}')
    if init[0] == None:
        state, reward = init
        return [('finish', reward)], player_cards, dealer_cards
    else:
        state = init

    trajectory = [state]

    while True:
        player_sum, dealer_show, usable_ace = state
        action = 'stick' if player_sum >= 20 else 'hit'
        # if player_sum < 21:
        trajectory.append(action)
        new_state, reward = step(player_cards, dealer_cards, action)
        if new_state is None:
            trajectory.append(('finish', reward))
            break

        
        trajectory.append(new_state)
        state = new_state
    
    return trajectory, player_cards, dealer_cards

if __name__ == '__main__':
    '''q1'''
    tra_list = []
    for i in range (10):
        trajectory, player_cards, dealer_cards = simulation()
        tra_list.append(trajectory)
        print(f'轨迹{i+1}：')
        print(f'玩家手牌：{player_cards} (点数:{calculate_sum(player_cards)})')
        print(f'庄家手牌：{dealer_cards} (点数:{calculate_sum(dealer_cards)})')    
        print(f'轨迹详情：{trajectory}')
        print(f'最终奖励：{trajectory[-1][1]}\n')
        print('--------------------------------------------------------------------')

    # '''q2'''
    # # 首次访问（first-visit）和每次访问（every-visit）的价值记录
    # first_visit_counts = {}  
    # first_visit_values = {}  
    # every_visit_counts = {}  
    # every_visit_values = {}  

    # for tra in tra_list:
    #     states_in_tra = tra[:-2:2]
    #     final_reward = tra[-1][-1]

    #     # first-visit
    #     visited = set()
    #     for s in states_in_tra:
    #         if s not in visited:
    #             visited.add(s)
    #             first_visit_counts[s] = first_visit_counts.get(s, 0) + 1
    #             first_visit_values[s] = first_visit_values.get(s, 0) + final_reward

    #     # every-visit
    #     for s in states_in_tra:
    #         every_visit_counts[s] = every_visit_counts.get(s, 0) + 1
    #         every_visit_values[s] = every_visit_values.get(s, 0) + final_reward
        
    # # 计算平均值
    # first_visit_results = {s: first_visit_values[s]/first_visit_counts[s] for s in first_visit_counts}
    # every_visit_results = {s: every_visit_values[s]/every_visit_counts[s] for s in every_visit_counts}
    
    # print("\n首次访问法（first-visit）价值函数：")
    # for s, v in first_visit_results.items():
    #     print(f"状态 {s}: {v:.2f}")
    
    # print("\n每次访问法（every-visit）价值函数：")
    # for s, v in every_visit_results.items():
    #     print(f"状态 {s}: {v:.2f}")
    

    # '''q3'''
    # counts = {}
    # values ={}

    # for i in range(500000):
    #     if i % 100000 == 0:
    #         print(f"已完成 {i}/{500000} 次模拟...")
        
    #     trajectory, player_cards, dealer_cards = simulation()
    #     states_in_traajectory = trajectory[:-2:2]
    #     final_reward = trajectory[-1][-1]

    #     visited = set()
    #     for s in states_in_traajectory:
    #         if s not in visited:
    #             visited.add(s)
    #             # 手动初始化计数器和价值总和
    #             counts[s] = counts.get(s, 0) + 1
    #             values[s] = values.get(s, 0) + final_reward

    #     state_values = {s: values[s]/counts[s] for s in counts}
    
    # # 输出部分结果（全量200个状态可保存到文件）
    # print(f"\n{500000}次模拟后的状态价值（部分）：")
    # for i, (s, v) in enumerate(state_values.items()):
    #     if i < 10:  # 只显示前10个状态
    #         print(f"状态 {s}: {v:.4f}")
    #     else:
    #         break

    # with open("HW2_blackjack_values.txt", "w") as f:
    #     for s in sorted(state_values.keys()):  # 按状态排序
    #         f.write(f"状态{s}: {state_values[s]:.4f}\n")

 