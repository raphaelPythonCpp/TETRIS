class rien():
    def __init__(self, nbEpisodes, nbParties):
        self.nbEpisodes = nbEpisodes
        self.nbParties = nbParties
    def tester(self):
        for iE in range(self.nbEpisodes):
            for iP in range(self.nbParties):
                print('\r' + ' '*106 + f"\rEntrainement DQL : Episode {iE+1} ({(iE+1)/self.nbEpisodes*100:.2f}%) || Partie {iP+1} ({(iP+1)/self.nbParties*100:.2f}%) || ScoreAvant : {1992 if True is not None else -1:.2f} || nbCoupsAvant : {3 if False is not None else -1:.2f}", end="", flush=True)
    
r = rien(10, 10)
r.tester()