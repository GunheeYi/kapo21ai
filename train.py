# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as data_utils
from math import sqrt

# %%
from board import *
from ai import *

EPOCHS = 3000
LEARNRATE = 0.1

# class loss_dummy(torch.nn.Module):
#     def __init__(self):
#         super(loss_dummy,self).__init__()
    
#     def forward(self, net, draw=False):
#         board = Board()
#         playerA = Player(A, net)
#         while True:
#             commands = playerA.call(board)
#             board.move(commands)
#             if draw: print(board)
#             result = board.winner() 
#             if result is not None:
#                 team, diff = result
#                 if team==B: diff = -diff
#                 progress = 10* board.turn / MAXTURN
#                 stepped = board.statistics['stepped'][playerA.team] * 10
#                 print("Diff: {}, progress: {}, stepped: {}".format(diff, progress, stepped))
#                 reward = - (diff + progress + stepped)
#                 return torch.tensor(reward, requires_grad=True)

class loss_turn_dummy(torch.nn.Module):
    def __init__(self):
        super(loss_turn_dummy,self).__init__()
    
    def forward(self, board, team, id, draw=False):
        if draw: print(board)
        return torch.tensor(-board.reward[team][id], dtype=torch.float, requires_grad=True)

def train():
    print("Starting training...")
    net = KaPo21Net(E2E).to(DEVICE)
    lossFunc = loss_turn_dummy()
    optimizer = torch.optim.Adam(net.parameters(), lr=LEARNRATE)
    
    for epoch in range(EPOCHS):
        print("Epoch {}-------------------------".format(epoch))
        board = Board()
        playerA = Player(A, net)
        while True:
            commands = playerA.call(board)
            board.move(commands)
            loss = lossFunc(board, playerA.team, 0, True)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            print("Loss: {}".format(loss))
            result = board.winner() 
            if result is not None:
                team, diff = result
                print("Team {} won by rate of {}".format(name(team), diff))
                break
        
# %%
def main():
    train()

main()