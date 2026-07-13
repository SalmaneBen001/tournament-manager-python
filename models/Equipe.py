from models.Joueur import Joueur

class Equipe:
    """gestion des équipes"""
    id = 0

    def __init__(self, nom, couleur, joueurs=None, points=0, victoires=0, nuls=0, defaites=0, buts_pour=0,
                 buts_contre=0, id=None):
        if id is None:
            Equipe.id += 1
            self.id = Equipe.id
        else:
            self.id = id
            if id > Equipe.id:
                Equipe.id = id
        self.nom = nom
        self.couleur = couleur
        self.joueurs = joueurs if joueurs is not None else []
        self.matchs_joues = 0
        self.points = points
        self.victoires = victoires
        self.nuls = nuls
        self.defaites = defaites
        self.buts_pour = buts_pour
        self.buts_contre = buts_contre
        self.matches_stats = []
        self.historique_confrontations = {}

    def ajouter_joueur(self, joueur):
        """ajout d'un joueur dans l'équipe"""
        if joueur not in self.joueurs:
            self.joueurs.append(joueur)
            joueur.equipe_id = self.id
        else:
            print(f"Le joueur appartient déjà à l'équipe '{self.nom}' ")

    def calculer_classement(self):
        """calcul du classement de l'équipe"""
        self.points = self.victoires * 3 + self.nuls

    def get_forme_recente(self):
        """retourne les statistiques des cinq derniers matchs"""
        if not self.matches_stats:
            return "l'équipe n'a encore joué aucun match"
        else:
            return ", ".join(self.matches_stats[-5:])

    def modifier_equipe(self, nom, couleur):
        """modification de l'équipe"""
        self.nom = nom
        self.couleur = couleur

    def retirer_joueur(self, joueur):
        """retrait d'un joueur de l'équipe"""
        if joueur in self.joueurs:
            self.joueurs.remove(joueur)
            joueur.equipe_id = None
        else:
            print(f"Le joueur {joueur.nom} n'appartient pas à l'équipe '{self.nom}'")

    def recuperer_j_par_id(self, id):
        """récupère un joueur par son id"""
        for j in self.joueurs:
            if str(id) == str(j.id):
                return j
        return None

    def to_dict(self):
        """conversion d'un objet équipe à un dictionnaire"""
        return {
            "id": self.id,
            "nom": self.nom,
            "couleur": self.couleur,
            "joueurs": [j.to_dict() for j in self.joueurs],
            "points": self.points,
            "victoires": self.victoires,
            "nuls": self.nuls,
            "defaites": self.defaites,
            "buts_pour": self.buts_pour,
            "buts_contre": self.buts_contre,
            "matches_stats": self.matches_stats,
            "historique_confrontations": self.historique_confrontations
        }

    @classmethod
    def from_dict(cls, equipe):
        """création d'une équipe existante depuis un dictionnaire"""
        liste_joueurs = []
        if "joueurs" in equipe:
            for j_dict in equipe["joueurs"]:
                liste_joueurs.append(Joueur.from_dict(j_dict))

        nouvelle_equipe = cls(
            nom=equipe["nom"],
            couleur=equipe["couleur"],
            joueurs=liste_joueurs,
            points=equipe.get("points", 0),
            victoires=equipe.get("victoires", 0),
            nuls=equipe.get("nuls", 0),
            defaites=equipe.get("defaites", 0),
            buts_pour=equipe.get("buts_pour", 0),
            buts_contre=equipe.get("buts_contre", 0),
            id=equipe.get("id", None)
        )

        nouvelle_equipe.matches_stats = equipe.get("matches_stats", [])
        nouvelle_equipe.historique_confrontations = equipe.get("historique_confrontations", {})
        return nouvelle_equipe
