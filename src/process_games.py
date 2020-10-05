#
# Script to extract piece counts and
# piece occurrence on all the square
#

# packages
import chess.pgn        # pip install python-chess
import json
from heatmaps import heatmaps

# PGN data extractor
class DataExtractor():
    # rating threshold
    rating_threshold = 2500

    # PGN file list to process
    pgn_files = [
        './pgn/CCRL-2020-03.pgn',
        './pgn/CCRL-2020-04.pgn',
        './pgn/CCRL-2020-05.pgn',
    ]
    
    # game count
    game_count = 0
    
    # opening phase score
    opening_phase_score = 28
    
    # endgame phase score
    endgame_phase_score = 15
    
    # heatmaps
    heatmaps = heatmaps
    
    # get game phase
    def get_game_phase(self, pieces):
        # count material
        white_pieces = pieces['P'] + pieces['N'] + pieces['B'] + pieces['R'] + pieces['Q']
        black_pieces = pieces['p'] + pieces['n'] + pieces['b'] + pieces['r'] + pieces['q']
        
        #count game phase score
        game_phase_score = white_pieces + black_pieces
        
        # calculate game phase based on material occurrence
        if game_phase_score >= self.opening_phase_score: return 'opening'
        elif game_phase_score <= self.endgame_phase_score: return 'endgame'
        else: return 'middlegame'
    
    # count pieces
    def count_pieces(self, fen, headers):
        # extract position
        fen = fen.split()[0]
        
        # count pieces
        pieces = {
            'P': fen.count('P'),
            'N': fen.count('N'),
            'B': fen.count('B'),
            'R': fen.count('R'),
            'Q': fen.count('Q'),
            
            'p': fen.count('p'),
            'n': fen.count('n'),
            'b': fen.count('b'),
            'r': fen.count('r'),
            'q': fen.count('q'),
            
            'result': headers['Result'],
        }
        
        # get game phase based on material occurrence
        pieces['game_phase'] = self.get_game_phase(pieces)
        
        # return piece count
        return pieces
    
    # update square stats
    def update_square_stats(self, move, board, piece_count, headers):
        # take move back
        board.pop()
        
        # skip captures
        if board.piece_at(move.to_square) is not None:
            # restore move
            board.push(move)
            return
        
        # restore move
        board.push(move)
        
        # get game phase
        game_phase = piece_count['game_phase']
        
        # update squares only for opening end endgame phases
        if game_phase != 'middlegame':
            # loop over board squares
            for square in range(0, 63):
                # found piece
                if (board.piece_at(square)):
                    # extract piece
                    piece = str(board.piece_at(square))
                    
                    # on win
                    if headers['Result'] == '1-0':
                        self.heatmaps[game_phase][piece][square]['win'] += 1
                    
                    # on loss
                    elif headers['Result'] == '0-1':
                        self.heatmaps[game_phase][piece][square]['loss'] += 1
                    
                    # on draw
                    elif headers['Result'] == '1/2-1/2':
                        self.heatmaps[game_phase][piece][square]['draw'] += 1
            
    # process PGN games
    def process_games(self, pgn):        
        # open PGN game
        with open(pgn) as f:
            # get current game
            current_game = chess.pgn.read_game(f)
            
            while current_game :
                # export piece weights every 100 games
                if (self.game_count % 100 == 0): self.export_heatmaps()

                # increment game count
                self.game_count += 1
                print('processing game %d' % self.game_count)
        
                # process moves
                self.process_moves(current_game)
                
                # get next game
                current_game = chess.pgn.read_game(f)

    # process game moves
    def process_moves(self, game):
        # init board
        board = game.board()

        # loop over moves
        for move in game.mainline_moves():
            # make move on board
            board.push(move)
            
            # count pieces
            piece_count = self.count_pieces(board.fen(), game.headers)
            
            # update square stats
            self.update_square_stats(move, board, piece_count, game.headers)
            
            # store piece count
            with open('./json/pieces.json', 'a') as f:
                f.write(json.dumps(piece_count) + '\n')
    
    # export heatmaps to JSON
    def export_heatmaps(self):
        # store heatmaps
        with open('./json/heatmaps.json', 'w') as f:
            f.write(json.dumps(self.heatmaps, indent=2))

    # extract data
    def run(self):
        # create output file
        with open('./json/pieces.json', 'w') as f: f.write('')
        
        # loop over PGNs
        for pgn in self.pgn_files:
            # process PGN
            self.process_games(pgn)
        
        # export heatmaps
        self.export_heatmaps()
        
        print('\nTotal games processed: %d' % self.game_count)

# main driver
if __name__ == '__main__':
    data_extractor = DataExtractor()
    data_extractor.run()

