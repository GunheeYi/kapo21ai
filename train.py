# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import torch
import torch.nn as nn
import torch.nn.functional as F
from math import sqrt

# %%
from board import *
from ai import *

    
def compete(match_num, target_num):
    playerA = Player(A, )
    print('Competing')
    AI_champ = Player(1, filepath='model_top.pt', use_gpu=True)
    AI_chall = Player(2, filepath='model.pt', use_gpu=True)
    win_count = 0
    for i in range(match_num):
        turn = 0
        max_turn = 128
        board = initial_state
        while turn < max_turn:
            board_str_1 = [''.join([{0:'_',1:'O',2:'X'}[item] for item in row]) for row in board]
            move_1 = AI_champ.move(board, max_visit=500)
            board = update_board(board, move_1)
            if is_end(board) or turn >= max_turn:
                if i == 0:
                    for j in range(7):
                        print(board_str_1[j])
                    print()
                if get_winner(board, 1, 2) == 2:
                    win_count += 1
                    print('W')
                else:
                    print('_')
                break
                
            turn += 1
            board_str_2 = [''.join([{0:'_',1:'O',2:'X'}[item] for item in row]) for row in board]
            if i == 0:
                for j in range(7):
                    print(board_str_1[j] + '\t' + board_str_2[j])
                print()
            move_2 = AI_chall.move(board, max_visit=500)
            board = update_board(board, move_2)
            if is_end(board) or turn >= max_turn:
                if get_winner(board, 1, 2) == 2:
                    win_count += 1
                    print('W')
                else:
                    print('_')
                break
            turn += 1
        if match_num - (i+1) + win_count < target_num:
            break
        if win_count >= target_num:
            break
    if win_count >= target_num:
        torch.save(AI_chall.net.state_dict(), 'model_top.pt')
        return True
    return False


# %%
def main():
    count = 0

    while True:
        count += 1
        print('count', count)
        new_champ = compete(7, 5)
        if new_champ:
            print('selfplay {}: New champ'.format(count))
        else:
            print('selfplay {}: End'.format(count))


# %%
def print_dataset(record, idx):
    print('idx', idx)
    print(torch.sum(record['input'][idx][0] - record['input'][idx][1]))
    print(record['input'][idx][0] - record['input'][idx][1])
    pol = record['policy'][idx].item()
    print(pol // 7 // 7, (pol // 7) % 7, pol % 7)
    print(record['value'][idx])


# %%
empty_record = {'input': [],
                'policy': [],
                'value': []}

main()