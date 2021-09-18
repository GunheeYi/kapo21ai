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

EPOCHS = 10
LEARNRATE = 0.01

class loss_dummy(torch.nn.Module):
    def __init__(self):
        super(loss_dummy,self).__init__()
    
    def forward(self, net, draw=False):
        board = Board()
        playerA = Player(A, net)
        while True:
            commands = playerA.call(board)
            board.move(commands)
            if draw: print(board)
            if result:=board.winner() is not None:
                team, diff = result
                return diff if team==A else -diff

def train():
    print("Starting training...")
    for epoch in range(10):
        net = KaPo21Net(RANGE).to('cpu')
        optimizer = torch.optim.Adam(net.parameters(), lr=LEARNRATE)
        loss = loss_dummy(net)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print("Epoch {}, loss {}".format(epoch, loss))
    loss_dummy(net, True)
        


# %%
def main():
    train()