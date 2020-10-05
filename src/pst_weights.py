#
# Script to calculate positional square table weight
# for every piece on every square in the opening and endgame
#

# packages
import json
import math

# PST weights
class PSTWeights():
    # square endianess convertion table
    map_square = [
        56, 57, 58, 59, 60, 61, 62, 63,
        48, 49, 50, 51, 52, 53, 54, 55,
        40, 42, 42, 43, 44, 45, 46, 47,
        32, 33, 34, 35, 36, 37, 38, 39,
        24, 25, 26, 27, 28, 29, 30, 31,
        16, 17, 18, 19, 20, 21, 22, 23,
         8,  9, 10, 11, 12, 13, 14, 15,
         0,  1,  2,  3,  4,  5,  6,  7 
    ]
    
    # load heatmaps
    def load_heatmaps(self):
        with open('./json/heatmaps_33k.json') as f:
            self.heatmaps = json.loads(f.read())
    
    # convert winning percantage to regression coef
    def get_square_weight(self, per_eff):
        per_eff_tr=float(per_eff)/100        
        lg=math.log(per_eff_tr/(1-per_eff_tr))
        return int(lg * 100)
    
    # get square win rate
    def get_win_rate(self, square):
        return ((square['win'] + 0.5 * square['draw']) / (square['win'] + square['draw'] + square['loss'])) * 100
    
    # calculate winning percentage
    def calculte_winning_percentage(self):
        # loop over game phases
        for game_phase in ['opening', 'endgame']:
            # loop over pieces
            for piece in ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']:
                # loop over board squares
                for square in range(0, 63):
                    # calculate win rate for each square
                    try:
                        self.heatmaps[game_phase][piece][square]['win_rate'] = self.get_win_rate(self.heatmaps[game_phase][piece][square])
                    
                    except:
                        self.heatmaps[game_phase][piece][square]['win_rate'] = 0
    
    # calculate PST weights
    def calculate_pst_weights(self):
        # loop over game phases
        for game_phase in ['opening', 'endgame']:
            # loop over pieces
            for piece in ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']:
                # loop over board squares
                for square in range(0, 63):
                    # calculate win rate for each square
                    try:
                        self.heatmaps[game_phase][piece][square]['weight'] = self.get_square_weight(self.heatmaps[game_phase][piece][square]['win_rate'])
                        
                    except:
                        self.heatmaps[game_phase][piece][square]['weight'] = 0

    # export PST tables
    def export_pst_tables(self):
        # loop over game phases
        for game_phase in ['opening', 'endgame']:
            print('\n\n // %s PST scores\n' % game_phase)
            
            # loop over pieces
            for piece in ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']:
                print("\n // '%s' scores" % piece)
                
                # loop over ranks
                for r in range(0, 8):
                    # loop over files
                    for f in range(0, 8):
                        # init & map square
                        square = self.map_square[(r * 8 + f)]
                        
                        try:
                            print(' %s,' % self.heatmaps[game_phase][piece][square]['weight'], end='')
                        
                        except:
                            print(' 0,', end='')

                    print()

    # calculate PST weights
    def run(self):
        # load heat maps
        self.load_heatmaps()
        
        # calculate winning percentage for all heatmaps
        self.calculte_winning_percentage()
        
        # calculate PST weights
        self.calculate_pst_weights()
        
        # export PST tables
        self.export_pst_tables()

# main driver
if __name__ == '__main__':
    pst_weights =  PSTWeights()
    pst_weights.run()

