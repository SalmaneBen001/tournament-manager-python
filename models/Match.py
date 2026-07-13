class Match:
    """gestion des matchs"""
    id = 0

    def __init__(self, journee, equipe_dom, equipe_ext, score_dom=0, score_ext=0, statut="à venir", buteurs=None,
                 passeurs=None, cartons=None, id=None):
        if id is None:
            self.id = Match.generer_id()
        else:
            self.id = id
            if id > Match.id:
                Match.id = id

        self.journee = journee
        self.equipe_dom = equipe_dom
        self.equipe_ext = equipe_ext
        self._score_dom = score_dom
        self._score_ext = score_ext
        self._statut = statut
        self._buteurs = buteurs.copy() if buteurs is not None else {}
        self._passeurs = passeurs.copy() if passeurs is not None else {}
        self._cartons = cartons.copy() if cartons is not None else {"jaunes": {}, "rouges": {}}

    @staticmethod
    def generer_id():
        """génération d'un identifiant unique du match"""
        Match.id += 1
        return Match.id

    @property
    def score_dom(self):
        """retourne le score de l'équipe domicile"""
        return self._score_dom

    @property
    def score_ext(self):
        """retourne le score de l'équipe extérieur"""
        return self._score_ext

    @property
    def statut(self):
        """retourne le statut du match"""
        return self._statut

    @property
    def buteurs(self):
        """retourne les buteurs du match"""
        return self._buteurs.copy()

    @property
    def passeurs(self):
        """retourne les passeurs du match"""
        return self._passeurs.copy()

    @property
    def cartons(self):
        """retourne les cartons du match"""
        return self._cartons.copy()

    def enregistrer_resultat(self, score_dom, score_ext, buteurs, passeurs, cartons):
        """enregistrement du résultat du match"""
        self._score_dom = score_dom
        self._score_ext = score_ext
        self._statut = "terminé"
        self._buteurs = buteurs
        self._passeurs = passeurs
        self._cartons = cartons

    def est_termine(self):
        """informe si le match est terminé ou non"""
        return self._statut == "terminé"

    def modifier_match(self, journee, equipe_dom, equipe_ext):
        """modification d'un match"""
        self.journee = journee
        self.equipe_dom = equipe_dom
        self.equipe_ext = equipe_ext

    def to_dict(self):
        """conversion du match à un dictionnaire"""
        id_dom = self.equipe_dom.id if hasattr(self.equipe_dom, "id") else self.equipe_dom.nom
        id_ext = self.equipe_ext.id if hasattr(self.equipe_ext, "id") else self.equipe_ext.nom

        buteurs_json = {}
        for joueur_obj, quantite in self._buteurs.items():
            if isinstance(joueur_obj, str):
                buteurs_json[joueur_obj] = quantite
            else:
                buteurs_json[str(joueur_obj.id)] = quantite

        passeurs_json = {}
        for joueur_obj, quantite in self._passeurs.items():
            if isinstance(joueur_obj, str):
                passeurs_json[joueur_obj] = quantite
            else:
                passeurs_json[str(joueur_obj.id)] = quantite

        cartons_json = {"jaunes": {}, "rouges": {}}
        if hasattr(self, "_cartons") and isinstance(self._cartons, dict):
            for joueur_obj, q in self._cartons.get("jaunes", {}).items():
                cle = joueur_obj if isinstance(joueur_obj, str) else str(joueur_obj.id)
                cartons_json["jaunes"][cle] = q
            for joueur_obj, q in self._cartons.get("rouges", {}).items():
                cle = joueur_obj if isinstance(joueur_obj, str) else str(joueur_obj.id)
                cartons_json["rouges"][cle] = q

        return {
            "id": self.id,
            "journee": self.journee,
            "equipe_dom": id_dom,
            "equipe_ext": id_ext,
            "score_dom": self._score_dom,
            "score_ext": self._score_ext,
            "statut": self._statut,
            "buteurs": buteurs_json,
            "passeurs": passeurs_json,
            "cartons": cartons_json
        }

    @classmethod
    def from_dict(cls, match, recuperer_eq_par_id, recuperer_j_par_id):
        """création d'un match existant depuis un dictionnaire"""
        eq_dom = match["equipe_dom"]
        eq_ext = match["equipe_ext"]

        eq_dom = recuperer_eq_par_id(eq_dom)
        eq_ext = recuperer_eq_par_id(eq_ext)

        buteurs = {}
        for j_id, buts in match.get("buteurs", {}).items():
            joueur_obj = recuperer_j_par_id(j_id, eq_dom, eq_ext)
            buteurs[joueur_obj if joueur_obj else j_id] = buts

        passeurs = {}
        for j_id, passes in match.get("passeurs", {}).items():
            joueur_obj = recuperer_j_par_id(j_id, eq_dom, eq_ext)
            passeurs[joueur_obj if joueur_obj else j_id] = passes
        cartons = {"jaunes": {}, "rouges": {}}
        cartons_data = match.get("cartons", {})

        if isinstance(cartons_data, dict):
            for couleur in ["jaunes", "rouges"]:
                for j_id, q in cartons_data.get(couleur, {}).items():
                    joueur_obj = recuperer_j_par_id(j_id, eq_dom, eq_ext)
                    cartons[couleur][joueur_obj if joueur_obj else j_id] = q
        return cls(
            journee=match["journee"],
            equipe_dom=eq_dom,
            equipe_ext=eq_ext,
            score_dom=match.get("score_dom", 0),
            score_ext=match.get("score_ext", 0),
            statut=match.get("statut", "à venir"),
            buteurs=buteurs,
            passeurs=passeurs,
            cartons=cartons,
            id=match.get("id")
        )
