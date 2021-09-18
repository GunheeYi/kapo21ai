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
LEARNRATE = 0.00001

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

def train():
    print("Starting training...")
    net = KaPo21Net(E2E).to(DEVICE)
    lossFunc = loss_dummy()
    optimizer = torch.optim.Adam(net.parameters(), lr=LEARNRATE)
    
    for epoch in range(EPOCHS):
        loss = lossFunc(net, True)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print("Epoch {}, loss {}".format(epoch, loss))
        
# %%
def main():
    train()

main()