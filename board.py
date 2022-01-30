class Board:
    def __init__(self, parent=None, move=None, fen=None):
        if parent:
            self.board = parent.board.copy()
            self.turn = not parent.turn
            self.castle = parent.castle.copy()
            self.enPassant = parent.enPassant
            self.hMove = parent.hMove + 1
            self.fMove = parent.fMove
            self.fMove += 1 if self.turn else 0

            self.makeMove(move)

        else:
            self.parseFen(fen)

    #Utility Functions
    def parseFen(self, fen):
        if not fen: #Use default board position
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        #get board state from fen
        board, turn, castle, enPassant, hMove, fMove = fen.split(' ')

        #init board
        self.board = [None] * 128 #0x88 board for out of board detection
        for i, row in enumerate(board.split('/')):
            j = 0
            file = 0
            while j < len(row):
                if row[j].isalpha():
                    self.board[(~i << 4) + file] = row[j]
                    file += 1
                else:
                    file += int(row[j])
                j += 1

        self.turn = turn == 'w' #turn is true when white to move

        #castling rights stored as two 2-bit integers [white, black]
        #LSB represents kingside castling, MSB queenside
        self.castle = [0, 0] 
        self.castle[0] += 1 if 'K' in castle else 0
        self.castle[0] += 2 if 'Q' in castle else 0
        self.castle[1] += 1 if 'k' in castle else 0
        self.castle[1] += 2 if 'q' in castle else 0

        #en passant square
        self.enPassant = None if enPassant == '-' \
                              else self.coordToIdx(enPassant)

        #move counters
        self.hMove = int(hMove)
        self.fMove = int(fMove)
    
    def getFen(self):
        #piece positions
        rows = []
        for i in range(8):
            currentRow = []
            emptyCounter = 0
            for j in range(8):
                char =  self.board[(~i << 4) + j]
                if not char is None:
                    if emptyCounter > 0:
                        currentRow.append(str(emptyCounter))
                        emptyCounter = 0
                    currentRow.append(char)
                else:
                    emptyCounter += 1
            if emptyCounter > 0:
                currentRow.append(str(emptyCounter))
                emptyCounter = 0
            rows.append(''.join(currentRow))
        
        turn = 'w' if self.turn else 'b'

        castle = ''
        castle += 'K' if self.castle[0] & 2 != 0 else ''
        castle += 'Q' if self.castle[0] & 1 != 0 else ''
        castle += 'k' if self.castle[1] & 2 != 0 else ''
        castle += 'q' if self.castle[0] & 1 != 0 else ''

        enPassant = '-' if self.enPassant is None \
                    else self.idxToCoord(self.enPassant)

        fen = f"{'/'.join(rows)} {turn} {castle if castle else '-'} " \
              f"{enPassant} {self.hMove} {self.fMove}"

        return fen

    def printBoard(self):
        pieces = {'R':'♜', 'N':'♞', 'B':'♝', 'Q':'♛', 'K':'♚', 'P':'♟',
                  'r':'♖', 'n':'♘', 'b':'♗', 'q':'♕', 'k':'♔', 'p':'♙'}
        for i in range(8):
            print(*(pieces.get(p, '·')
                    for p in self.board[~i << 4:(~i << 4) + 8]), sep=' ')

    def coordToIdx(self, coord):
        rank = int(coord[1]) - 1
        file = ord(coord[0].lower()) - 97
        return (rank << 4) + file

    def idxToCoord(self, idx):
        rank = (idx >> 4) + 1
        file = chr((idx & 7) + 97)
        return f"{file}{rank}"

    def getPieces(self, flag=0):
        wp = []
        bp = []

        for i in range(8):
            for j in range(8):
                idx = (i << 4) + j
                if self.board[idx]:
                    if self.board[idx].isupper():
                        wp.append(idx)
                    else:
                        bp.append(idx)

        if flag == -1:
            return bp
        elif flag == 1:
            return wp
        else:
            return wp, bp

    #Movement
    def makeMove(self, move):
        #0b0000000 0000000 0000 : fromidx, toidx, promotion, flag
        from_idx = move >> 11
        to_idx = (move >> 4) & 0b1111111
        promotion = (move >> 2) & 0b11
        flag = move & 0b11
        
        self.board[from_idx], self.board[to_idx] = None, self.board[from_idx]
        if flag == 0: #normal move
            pass
        elif flag == 1: #promotion
            promotion_pieces = ('n', 'b', 'r', 'q')
            if self.board[to_idx].isupper():
                self.board[to_idx] = promotion_pieces[promotion].upper()
            else:
                self.board[to_idx] = promotion_pieces[promotion]
        elif flag == 2: #enpassant
            if self.turn:
                self.board[to_idx + 16] = None
            else:
                self.board[to_idx - 16] = None
        else: #castle
            self.castle[1 if self.turn else 0] = 0
            if to_idx > from_idx: #kingside castle
                self.board[from_idx+1], self.board[to_idx+1] = self.board[to_idx+1], None
            else: #queenside
                self.board[from_idx-1], self.board[to_idx-2] = self.board[to_idx-2], None

        #Update castle
        if self.castle[0] or self.castle[1]:
            if self.board[to_idx] == 'K':
                self.castle[0] = 0
            elif self.board[to_idx] == 'K':
                self.castle[0] = 0
            
            if self.castle[0] & 1:
                if 7 in (from_idx, to_idx):
                    self.castle[0] &= 2
            if self.castle[0] & 2:
                if 0 in (from_idx, to_idx):
                    self.castle[0] &= 1

            if self.castle[1] & 1:
                if 119 in (from_idx, to_idx):
                    self.castle[1] &= 2
            if self.castle[1] & 2:
                if 112 in (from_idx, to_idx):
                    self.castle[1] &= 1

        #Update enPassant
        if self.board[to_idx].lower() == 'p' and abs(to_idx - from_idx) == 32:
            self.enPassant = (to_idx + from_idx) >> 1
        else:
            self.enPassant = None

    def moveGenerator(self, attack=False):
        moves = []
        left, right, up, down = -1, 1, 16, -16
        directions = {'n':(up*2+left, up*2+right, left*2+up, 
                          left*2+down, down*2+left, down*2+right,
                          right*2+up, right*2+down),
                      'b':(up+left, up+right, down+left, down+right),
                      'r':(left, right, up, down),
                      'q':(up+left, up+right, down+left, down+right,
                           left, right, up, down),
                      'k':(up+left, up+right, down+left, down+right,
                           left, right, up, down)}
        if self.turn:
            directions['p'] = (up, up*2, up+left, up+right)
        else:
            directions['p'] = (down, down*2, down+left, down+right)

        pieces = self.getPieces(1 if self.turn else -1)
        for p in pieces:
            scaffold = p << 11
            p_type = self.board[p].lower()
            for d in directions[p_type]:
                current = p
                for i in range(7):
                    current += d
                    if current & 136 != 0:
                        break

                    if self.board[current]: #break if own piece
                        if (self.turn and self.board[current].isupper()) \
                            or (not self.turn and self.board[current].islower()):
                            break

                    if p_type == 'p': #Pawn movement special cases
                        if abs(d) == 16 and (attack or self.board[p + d]): #push into enemy
                            break
                        if abs(d) == 32 and (attack or not p >> 4 in (1,6) or self.board[current] or self.board[current - d//2]):
                            break
                        if not attack and (abs(d) in (15, 17) and not self.board[current]):
                            if current == self.enPassant:
                                moves.append(scaffold+(current<<4)+2)
                            break
                        if current >> 4 in (0, 7): #promotion
                            for promote in range(4):
                                moves.append(scaffold+(current<<4)+(promote<<2)+1)
                            break
                    
                    if p_type == 'k' and not attack: #castling TO BE IMPLEMENTED
                        if (self.castle[not self.turn] & 1 and d == right) or \
                            (self.castle[not self.turn] & 2 and d == left):
                            if not self.board[current] and not self.board[current + d]:
                                if not any(idx in self.attackSet() for idx in (p, current, current+d)):
                                    moves.append(scaffold+((current+d)<<4)+3)

                    moves.append(scaffold+(current<<4))
                    
                    if p_type in 'pnk':
                        break
                    
                    if self.board[current]:
                        break

        return moves

    def attackSet(self):
        self.turn = not self.turn
        attack = {(idx >> 4) & 0b1111111 for idx in self.moveGenerator(attack=True)}
        self.turn = not self.turn
        return attack