class StatistiquesManager:
    """gestion des statistiques du tournoi"""

    def __init__(self, tournoi):
        self.tournoi = tournoi

    def _joueurs(self):
        """retourne la liste des joueurs du tournoi si disponible, sinon une liste vide"""
        if not self.tournoi or not getattr(self.tournoi, "equipes", None):
            return []
        return [
            joueur
            for equipe in self.tournoi.equipes.values()
            for joueur in getattr(equipe, "joueurs", [])
        ]

    def _nom_equipe(self, equipe_id):
        """retourne le nom d'une équipe à partir de son identifiant si possible"""
        if not self.tournoi or not hasattr(self.tournoi, "recuperer_eq_par_id"):
            return None
        equipe = self.tournoi.recuperer_eq_par_id(equipe_id)
        return equipe.nom if equipe else None

    def top_buteurs(self):
        """retourne les dix meilleurs buteurs du tournoi"""
        return sorted(self._joueurs(), key=lambda joueur: joueur.buts, reverse=True)[:10]

    def top_passeurs(self):
        """retourne les dix meilleurs passeurs du tournoi"""
        return sorted(self._joueurs(), key=lambda joueur: joueur.passes, reverse=True)[:10]

    def mvp(self):
        """retourne le meilleur joueur du tournoi (MVP)"""
        joueurs = self._joueurs()
        if not joueurs:
            return None
        return max(joueurs, key=lambda joueur: joueur.calculer_mvp_score())

    def analyse_confrontation(self, eq1, eq2):
        """analyse de l'historique des confrontations entre deux équipes"""
        eq1_vs_eq2 = eq1.historique_confrontations.get(eq2.nom, {
            f"victoires_{eq1.nom}": 0,
            f"victoires_{eq2.nom}": 0,
            "nuls": 0
        })

        total_matchs_joues = sum(eq1_vs_eq2.values())

        return {
            "equipes": [eq1.nom, eq2.nom],
            "total_matchs_joues": total_matchs_joues,
            "historique_directe": eq1_vs_eq2,
            "comparaison_globale": {
                "buts_pour": {
                    eq1.nom: getattr(eq1, "buts_pour", 0),
                    eq2.nom: getattr(eq2, "buts_pour", 0)
                },
                "buts_contre": {
                    eq1.nom: getattr(eq1, "buts_contre", 0),
                    eq2.nom: getattr(eq2, "buts_contre", 0)
                }
            },
            "meilleurs_elements": {
                eq1.nom: max(eq1.joueurs, key=lambda j: j.calculer_mvp_score(), default=None),
                eq2.nom: max(eq2.joueurs, key=lambda j: j.calculer_mvp_score(), default=None)
            }
        }

    def _joueurs_to_dict(self, joueurs, stat_attr):
        """conversion d'une liste de joueurs classés en dictionnaire"""
        return [
            {
                "rang": rang,
                "joueur": joueur.nom,
                "equipe": self._nom_equipe(joueur.equipe_id),
                "statistiques": getattr(joueur, stat_attr),
                "matchs_joues": joueur.matchs_joues,
            }
            for rang, joueur in enumerate(joueurs, start=1)
        ]

    def top_buteurs_to_dict(self):
        """conversion des top buteurs en dictionnaire"""
        return self._joueurs_to_dict(self.top_buteurs(), "buts")

    def top_passeurs_to_dict(self):
        """conversion des top passeurs en dictionnaire"""
        return self._joueurs_to_dict(self.top_passeurs(), "passes")

    def mvp_to_dict(self):
        """conversion du mvp en dictionnaire"""
        joueur_mvp = self.mvp()
        if not joueur_mvp:
            return None

        return {
            "joueur": joueur_mvp.nom,
            "equipe": self._nom_equipe(joueur_mvp.equipe_id),
            "score_mvp": joueur_mvp.calculer_mvp_score(),
            "statistiques": {
                "matchs_joues": joueur_mvp.matchs_joues,
                "buts": joueur_mvp.buts,
                "passes": joueur_mvp.passes,
                "cartons_jaunes": joueur_mvp.cartons_jaunes,
                "cartons_rouges": joueur_mvp.cartons_rouges,
            }
        }
