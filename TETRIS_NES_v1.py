import torch
from datetime import datetime

class Neural_Evolution_Strategies(torch.nn.Module):
    def __init__(self, jeu, algo, nbConstantes):
        super().__init__()

        self.jeu = jeu
        self.algo = algo

        self.nbConstantes = nbConstantes
        self.contexte = torch.nn.Parameter(torch.zeros(self.nbConstantes))
        self.reseau = torch.nn.Sequential(torch.nn.Linear(self.nbConstantes, 64), torch.nn.ReLU(), torch.nn.Linear(64, self.nbConstantes))
        self.log_sigma = torch.nn.Parameter(torch.full((self.nbConstantes,), -1.0))
        self.optimiseur = torch.optim.Adam(self.parameters(), lr=1e-2)

    def reset(self):
        pass

    def entrainement(self, nbGenerations, tailleBatch):
        tAvant = datetime.now()
        sauvegardeFichiers = True
        lScoresMoyensTotal = [(None,None) for iG in range(nbGenerations)]
        lNbCoupsMoyensTotal = [(None, None) for iG in range(nbGenerations)]
        lLMeilleursConstantesTotal = [[None]*self.nbConstantes for iG in range(nbGenerations)]
        for iG in range(nbGenerations):
            #Génération
            listeLConstantes, epsilon, mu, sigma = self.forward(tailleBatch)
            #Evaluation
            lScoresMoyens = []
            lNbCoupsMoyens = []
            for iC,lConstantes in enumerate(listeLConstantes):
                print('\r'+' '*100+'\r'+f"Entrainement NES : Génération {iG+1} ({(iG+1)/nbGenerations*100:.2f}%) Essai {iC+1} ({(iC+1)/tailleBatch*100:.2f}%)",end="",flush=True)
                scoreMoyen,nbCoupsMoyens = self.jeu.evaluation_algo(nbParties=100, lConstantes=lConstantes.detach().numpy(), affichage=False)
                lScoresMoyens.append(scoreMoyen)
                lNbCoupsMoyens.append(nbCoupsMoyens)
            lScoresMoyens = torch.tensor(lScoresMoyens, dtype=torch.float32)
            lNbCoupsMoyens = torch.tensor(lNbCoupsMoyens, dtype=torch.float32)
            #Standardisation
            lScoresMoyensNormalises = (lScoresMoyens - lScoresMoyens.mean()) / (lScoresMoyens.std() + 1e-8)
            lNbCoupsMoyensNormalises = (lNbCoupsMoyens - lNbCoupsMoyens.mean()) / (lNbCoupsMoyens.std() + 1e-8)

            #Log-probabilité GAUSSIENNE
            log_prob = -0.5 * (((listeLConstantes - mu) / sigma)**2 + 2 * torch.log(sigma)).sum(dim=1)
            #Perte
            loss = -((lScoresMoyensNormalises) * log_prob).mean()
            #BackPropagation
            self.optimiseur.zero_grad()
            loss.backward()
            self.optimiseur.step()

            #Tri
            lRes = [(i, scoreMoyen.detach().item(), nbCoupsMoyens.detach().item(), [c.detach().item() for c in lConstantes]) for i,scoreMoyen,nbCoupsMoyens,lConstantes in zip(range(tailleBatch), lScoresMoyens, lNbCoupsMoyens, listeLConstantes)]
            lRes.sort(key=lambda res : (res[1], res[2]), reverse=True)
            print('\n',*[(round(scoreM), round(nbCoupsM)) for i, scoreM, nbCoupsM, lC in lRes])
            lScoresMoyensTotal[iG] = (lRes[0][1], lRes[-1][1])
            lNbCoupsMoyensTotal[iG] = (lRes[0][2], lRes[-1][2])
            lLMeilleursConstantesTotal[iG] = [round(constante, 2) for constante in lRes[0][3]]
            if sauvegardeFichiers:
                with open("lScoresMoyensTotal_NES.txt", "w") as fichier:
                    fichier.write(str(lScoresMoyensTotal))
                with open("lNbCoupsMoyensTotal_NES.txt", "w") as fichier:
                    fichier.write(str(lNbCoupsMoyensTotal))
                with open("lLMeilleursConstantesTotal_NES.txt", "w") as fichier:
                    fichier.write(str(lLMeilleursConstantesTotal))

        lConstantesFinales = lLMeilleursConstantesTotal[-1]
        print(f"\n==> {lConstantesFinales}")
        self.algo.lConstantes = lConstantesFinales
        t = datetime.now()
        print(f"{tAvant.hour}:{tAvant.minute}'{tAvant.second}\" -> {t.hour}:{t.minute}'{t.second}\"")
        #return lConstantesFinales
    
    def forward(self, tailleBatch):
        mu = torch.tanh(self.reseau(self.contexte))
        sigma = torch.exp(self.log_sigma)
        epsilon = torch.randn(tailleBatch, self.nbConstantes)
        lConstantes = torch.tanh(mu + sigma * epsilon)
        return lConstantes, epsilon, mu, sigma



"""
🧠 Comparaison rapide
Méthode	       Complexité	Perf	Pertinence
GA	           moyenne	    OK	    déjà fait
ES	           faible	    🔥	    excellent
NN surrogate   moyenne	    🔥	    très bon
NES	           moyenne	   🔥🔥	    meilleur choix (CELLE-CI !!!)
RL complet	   très élevée🔥🔥🔥   overkill
"""