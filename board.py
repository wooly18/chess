class Board:
    def __init__(self, fen=None):
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

        print(self.getFen())
    
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
        rank = int(coord[1])
        file = ord(coord[0].lower()) - 97
        return (rank << 4) + file

    def idxToCoord(self, idx):
        rank = idx >> 4
        file = chr((idx & 7) + 97)
        return f"{file}{rank}"