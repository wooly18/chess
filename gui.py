from board import Board
import engine
import time

bot = engine.Engine(engine.Board())

for _ in range(100):
    bot.history[-1].printBoard()
    move, adv, depth = bot.makeMove(1)
    print(f'Move: {bot.history[-1].idxToCoord(move>>11)} to ' \
      f'{bot.history[-1].idxToCoord((move>>4)&0b1111111)}\nAdvantage: '\
      f'{adv}\n Depth: {depth}')
    bot.history.append(Board(bot.history[-1], move))
    time.sleep(0.1)