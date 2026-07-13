class Joueur:
    """gestion des joueurs"""
    id = 0

    def __init__(self, nom, numero_maillot, poste, equipe_id, buts=0, passes=0, cartons_jaunes=0, cartons_rouges=0,
                 matchs_joues=0, victoires=0, id=None):
        if id is None:
            Joueur.id += 1
            self.id = Joueur.id
        else:
            self.id = id
            if id > Joueur.id:
                Joueur.id = id
        self.nom = nom
        self.numero_maillot = numero_maillot
        self.poste = poste
        self.equipe_id = equipe_id
        self.buts = buts
        self.passes = passes
        self.cartons_jaunes = cartons_jaunes
        self.cartons_rouges = cartons_rouges
        self.matchs_joues = matchs_joues
        self.victoires = victoires

    def calculer_mvp_score(self):
        """calcul de score du joueur"""
        if self.matchs_joues == 0:
            return 0
        return (self.buts * 3 + self.passes * 2 + self.victoires) / self.matchs_joues

    def modifier_joueur(self, nom, numero_maillot, poste, equipe_id):
        """modification des informations d'un joueur"""
        self.nom = nom
        self.numero_maillot = numero_maillot
        self.poste = poste
        self.equipe_id = equipe_id

    def to_dict(self):
        """conversion d'un objet joueur à un dictionnaire"""
        return {
            "id": self.id,
            "nom": self.nom,
            "numero_maillot": self.numero_maillot,
            "poste": self.poste,
            "equipe_id": self.equipe_id,
            "buts": self.buts,
            "passes": self.passes,
            "cartons_jaunes": self.cartons_jaunes,
            "cartons_rouges": self.cartons_rouges,
            "matchs_joues": self.matchs_joues,
            "victoires": self.victoires
        }

    @classmethod
    def from_dict(cls, joueur):
        """création d'un nouveau joueur depuis un dictionnaire"""
        nom = joueur["nom"]
        numero_maillot = joueur["numero_maillot"]
        poste = joueur["poste"]
        equipe_id = joueur["equipe_id"]
        buts = joueur["buts"]
        passes = joueur["passes"]
        cartons_jaunes = joueur["cartons_jaunes"]
        cartons_rouges = joueur["cartons_rouges"]
        matchs_joues = joueur["matchs_joues"]
        victoires = joueur.get("victoires", 0)
        id = joueur.get("id", None)
        nouveau_joueur = cls(nom, numero_maillot, poste, equipe_id, buts, passes, cartons_jaunes, cartons_rouges,
                             matchs_joues, victoires, id)
        return nouveau_joueur
