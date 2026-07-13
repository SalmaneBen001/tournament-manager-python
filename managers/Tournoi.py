from functools import cmp_to_key
from models.Match import Match
import random
import math
from models.Equipe import Equipe

class Tournoi:
    """gestion de tournoi"""

    def __init__(self, nom, sport, equipes, journee_courante=1, matchs=None, type=None):
        self.nom = nom
        self.sport = sport
        self.equipes = equipes
        self.matchs = matchs if matchs is not None else {}
        self.journee_courante = journee_courante
        self.type = type

    def recuperer_eq_par_id(self, eq_id):
        """récupère une équipe par son id"""
        for equipe in self.equipes.values():
            if str(eq_id) == str(equipe.id):
                return equipe
        return None

    def recuperer_j_par_id(self, j_id, *args):
        """Récupère un joueur par son ID en ignorant les arguments superflus lors du chargement JSON"""
        for equipe in self.equipes.values():
            joueur = equipe.recuperer_j_par_id(j_id)
            if joueur is not None:
                return joueur
        return None

    def recuperer_eq_par_nom(self, nom):
        """Récupère une équipe par son nom"""
        for equipe in self.equipes.values():
            if equipe.nom == nom:
                return equipe
        return None

    def generer_calendrier(self):
        """génération du calendrier"""
        raise NotImplementedError("Veuillez définir la méthode de génération du calendrier dans les sous-classes!")

    def mettre_a_jour_classement(self, generer_tour_suivant=True):
        """màj du classement du tournoi"""
        # Réinitialisation complète des données pour le recalcul
        for equipe in self.equipes.values():
            equipe.matchs_joues = 0
            equipe.points = 0
            equipe.victoires = 0
            equipe.nuls = 0
            equipe.defaites = 0
            equipe.buts_pour = 0
            equipe.buts_contre = 0
            equipe.matches_stats = []
            equipe.historique_confrontations = {}
            for joueur in equipe.joueurs:
                joueur.matchs_joues = 0
                joueur.buts = 0
                joueur.passes = 0
                joueur.cartons_jaunes = 0
                joueur.cartons_rouges = 0
                joueur.victoires = 0

        # Traitement séquentiel de tous les matchs enregistrés
        for matchs in self.matchs.values():
            for match in matchs:
                if match.est_termine():
                    eq_dom = match.equipe_dom
                    eq_ext = match.equipe_ext
                    eq_dom.matchs_joues += 1
                    eq_ext.matchs_joues += 1

                    score_dom = match.score_dom
                    score_ext = match.score_ext
                    eq_dom.buts_pour += score_dom
                    eq_ext.buts_pour += score_ext
                    eq_dom.buts_contre += score_ext
                    eq_ext.buts_contre += score_dom

                    for joueur in eq_dom.joueurs + eq_ext.joueurs:
                        joueur.matchs_joues += 1

                    if score_dom > score_ext:
                        eq_dom.victoires += 1
                        eq_ext.defaites += 1
                        eq_dom.matches_stats.append("V")
                        eq_ext.matches_stats.append("D")
                        for joueur in eq_dom.joueurs:
                            joueur.victoires += 1
                    elif score_ext > score_dom:
                        eq_ext.victoires += 1
                        eq_dom.defaites += 1
                        eq_dom.matches_stats.append("D")
                        eq_ext.matches_stats.append("V")
                        for joueur in eq_ext.joueurs:
                            joueur.victoires += 1
                    else:
                        eq_dom.nuls += 1
                        eq_ext.nuls += 1
                        eq_dom.matches_stats.append("N")
                        eq_ext.matches_stats.append("N")

                    # Historique des confrontations directes
                    if eq_ext.nom not in eq_dom.historique_confrontations:
                        eq_dom.historique_confrontations[eq_ext.nom] = {f"victoires_{eq_dom.nom}": 0,
                                                                        f"victoires_{eq_ext.nom}": 0, "nuls": 0}
                    if eq_dom.nom not in eq_ext.historique_confrontations:
                        eq_ext.historique_confrontations[eq_dom.nom] = {f"victoires_{eq_dom.nom}": 0,
                                                                        f"victoires_{eq_ext.nom}": 0, "nuls": 0}

                    if score_dom > score_ext:
                        eq_dom.historique_confrontations[eq_ext.nom][f"victoires_{eq_dom.nom}"] += 1
                        eq_ext.historique_confrontations[eq_dom.nom][f"victoires_{eq_dom.nom}"] += 1
                    elif score_ext > score_dom:
                        eq_dom.historique_confrontations[eq_ext.nom][f"victoires_{eq_ext.nom}"] += 1
                        eq_ext.historique_confrontations[eq_dom.nom][f"victoires_{eq_ext.nom}"] += 1
                    else:
                        eq_dom.historique_confrontations[eq_ext.nom]["nuls"] += 1
                        eq_ext.historique_confrontations[eq_dom.nom]["nuls"] += 1

                    # Mise à jour des statistiques individuelles
                    for joueur, buts in match.buteurs.items():
                        if joueur and not isinstance(joueur, str) and hasattr(joueur, "buts"):
                            joueur.buts += buts

                    for joueur, passes in match.passeurs.items():
                        if joueur and not isinstance(joueur, str) and hasattr(joueur, "passes"):
                            joueur.passes += passes

                    dict_jaunes = match.cartons.get("jaunes", {})
                    for joueur in dict_jaunes.keys():
                        if hasattr(joueur, "cartons_jaunes"):
                            joueur.cartons_jaunes += 1

                    dict_rouges = match.cartons.get("rouges", {})
                    for joueur in dict_rouges.keys():
                        if hasattr(joueur, "cartons_rouges"):
                            joueur.cartons_rouges += 1

        for equipe in self.equipes.values():
            equipe.calculer_classement()

        # Calcul automatique de l'avancement de la journée courante
        structure_matchs = getattr(self, "matchs", {})
        for num_j in sorted(structure_matchs.keys()):
            matchs_j = structure_matchs[num_j]
            if any(m.est_termine() for m in matchs_j):
                if all(m.est_termine() for m in matchs_j):
                    journee_suivante = num_j + 1
                    matchs_suivants = structure_matchs.get(journee_suivante, [])
                    if matchs_suivants and any(m.est_termine() for m in matchs_suivants):
                        continue
                    else:
                        self.journee_courante = num_j
                        break
                else:
                    self.journee_courante = num_j
                    break
            else:
                if num_j == 1:
                    self.journee_courante = 1
                    break

        j_actuelle = getattr(self, "journee_courante", 1)
        matchs_de_la_journee = structure_matchs.get(j_actuelle, [])
        if generer_tour_suivant and matchs_de_la_journee and all(m.est_termine() for m in matchs_de_la_journee):
            if hasattr(self, "generer_tour_suivant"):
                self.generer_tour_suivant()

    def get_classement(self):
        """retourne le classement des équipes avec critères de départage"""

        def sort(eq1, eq2):
            if eq1.points != eq2.points:
                return eq1.points - eq2.points
            diff_eq1 = eq1.buts_pour - eq1.buts_contre
            diff_eq2 = eq2.buts_pour - eq2.buts_contre
            if diff_eq1 != diff_eq2:
                return diff_eq1 - diff_eq2
            if eq1.buts_pour != eq2.buts_pour:
                return eq1.buts_pour - eq2.buts_pour
            if eq2.nom in eq1.historique_confrontations:
                face_a_face = eq1.historique_confrontations[eq2.nom]
                victoires_eq1 = face_a_face.get(f"victoires_{eq1.nom}", 0)
                victoires_eq2 = face_a_face.get(f"victoires_{eq2.nom}", 0)
                if victoires_eq1 != victoires_eq2:
                    return victoires_eq1 - victoires_eq2
            return 0

        return sorted(self.equipes.values(), key=cmp_to_key(sort), reverse=True)

    def predire_resultat(self, eq_dom, eq_ext):
        """Simulation Monte Carlo prédictive basée sur la forme récente"""

        def score_forme(equipe):
            recents = equipe.matches_stats[-5:]
            if not recents:
                return 5
            return sum(3 if r == "V" else 1 if r == "N" else 0 for r in recents)

        def score_historique(eq1, eq2):
            face_a_face = eq1.historique_confrontations.get(eq2.nom, {})
            victoires = face_a_face.get(f"victoires_{eq1.nom}", 0)
            total = victoires + face_a_face.get(f"victoires_{eq2.nom}", 0) + face_a_face.get("nuls", 0)
            return (victoires / total) * 10 if total > 0 else 0

        p_dom = score_forme(eq_dom) + score_historique(eq_dom, eq_ext) + 2
        p_ext = score_forme(eq_ext) + score_historique(eq_ext, eq_dom)

        v_dom, v_ext, nuls = 0, 0, 0
        for _ in range(1000):
            mode_dom = max(0.0, min(5.0, p_dom / 5.0))
            mode_ext = max(0.0, min(5.0, p_ext / 5.0))

            b_dom = int(random.triangular(0, 5, mode_dom))
            b_ext = int(random.triangular(0, 5, mode_ext))

            if b_dom > b_ext:
                v_dom += 1
            elif b_ext > b_dom:
                v_ext += 1
            else:
                nuls += 1

        return (f"Victoire {eq_dom.nom} : {v_dom / 10}% | "
                f"Match nul : {nuls / 10}% | "
                f"Victoire {eq_ext.nom} : {v_ext / 10}%")

    def to_dict(self):
        equipes_dict = {str(eq_id): eq.to_dict() for eq_id, eq in self.equipes.items()}
        matchs_dict = {}
        for journee, liste_matchs in self.matchs.items():
            matchs_dict[str(journee)] = [m.to_dict() for m in liste_matchs]

        return {
            "nom": self.nom,
            "sport": self.sport,
            "journee_courante": self.journee_courante,
            "type": self.type,
            "equipes": equipes_dict,
            "matchs": matchs_dict
        }

    @classmethod
    def from_dict(cls, data, generer_tour_suivant=False):
        equipes_reconstituees = {}
        if "equipes" in data:
            for eq_id, eq_data in data["equipes"].items():
                equipe_obj = Equipe.from_dict(eq_data)
                equipes_reconstituees[equipe_obj.id] = equipe_obj

        matchs_reconstitues = {}
        nouveau_tournoi = cls(
            data["nom"],
            data["sport"],
            equipes_reconstituees,
            data.get("journee_courante", 1),
            matchs_reconstitues,
            data.get("type")
        )

        if "matchs" in data:
            for journee_str, liste_m_data in data["matchs"].items():
                journee_int = int(journee_str)
                matchs_reconstitues[journee_int] = [
                    Match.from_dict(
                        match=m_data,
                        recuperer_eq_par_id=nouveau_tournoi.recuperer_eq_par_id,
                        recuperer_j_par_id=nouveau_tournoi.recuperer_j_par_id
                    )
                    for m_data in liste_m_data
                ]

        nouveau_tournoi.matchs = matchs_reconstitues
        nouveau_tournoi.mettre_a_jour_classement(generer_tour_suivant=generer_tour_suivant)
        return nouveau_tournoi

    def resultats_journee(self, journee):
        return self.matchs.get(int(journee), [])


class ChampionnatTournoi(Tournoi):
    def __init__(self, nom, sport, equipes, journee_courante=1, matchs=None, type="Championnat"):
        super().__init__(nom, sport, equipes, journee_courante, matchs, type)

    def generer_calendrier(self):
        """Génération d'un calendrier complet Round-Robin (Algorithme de Berger)"""
        equipes = list(self.equipes.values())
        if len(equipes) % 2 != 0:
            equipes.append(None)

        n = len(equipes)
        tours_aller = n - 1
        self.matchs = {}

        # Phase Aller
        for journee in range(tours_aller):
            num_journee = journee + 1
            self.matchs[num_journee] = []

            for i in range(n // 2):
                eq_dom = equipes[i]
                eq_ext = equipes[n - 1 - i]

                if eq_dom is not None and eq_ext is not None:
                    if journee % 2 == 0:
                        self.matchs[num_journee].append(Match(num_journee, eq_dom, eq_ext))
                    else:
                        self.matchs[num_journee].append(Match(num_journee, eq_ext, eq_dom))

            # Rotation Berger valide : l'élément à l'index 0 reste fixe
            equipes = [equipes[0]] + [equipes[-1]] + equipes[1:-1]

        # Phase Retour
        for journee in range(tours_aller):
            num_journee_aller = journee + 1
            num_journee_retour = journee + 1 + tours_aller
            self.matchs[num_journee_retour] = []

            for match_aller in self.matchs[num_journee_aller]:
                eq_dom_aller = match_aller.equipe_dom
                eq_ext_aller = match_aller.equipe_ext
                match_retour = Match(num_journee_retour, eq_ext_aller, eq_dom_aller)
                self.matchs[num_journee_retour].append(match_retour)

        return self.matchs


class CoupeTournoi(Tournoi):
    def __init__(self, nom, sport, equipes, journee_courante=1, matchs=None, type="Coupe"):
        super().__init__(nom, sport, equipes, journee_courante, matchs, type)
        self.equipes_exemptees = []
        self.taille_tableau = None

    def generer_calendrier(self):
        """Génération du premier tour de la coupe"""
        equipes = list(self.equipes.values())
        nb_equipes = len(equipes)
        if nb_equipes < 2:
            raise ValueError("Il faut au moins 2 équipes pour générer une coupe")

        puissance_sup = 2 ** math.ceil(math.log2(nb_equipes))
        self.taille_tableau = puissance_sup
        random.shuffle(equipes)

        self.journee_courante = 1
        self.matchs = {self.journee_courante: []}
        self.equipes_exemptees = []

        # On conserve des places de tableau pour les équipes exemptées
        while len(equipes) > (puissance_sup - nb_equipes) and len(equipes) >= 2:
            eq_dom = equipes.pop(0)
            eq_ext = equipes.pop(0)
            self.matchs[self.journee_courante].append(Match(self.journee_courante, eq_dom, eq_ext))

        self.equipes_exemptees = equipes
        return self.matchs

    def generer_tour_suivant(self):
        """Génération robuste et sécurisée du tour suivant à élimination directe, avec match pour la 3e place"""
        tour_precedent = int(self.journee_courante)
        matchs_tour_prec = self.matchs.get(tour_precedent) or self.matchs.get(tour_precedent)

        if not matchs_tour_prec:
            raise ValueError(f"Le tour précédent ({tour_precedent}) n'existe pas ou est vide.")

        qualifies = []
        elimines = []
        
        for match in matchs_tour_prec:
            if not match.est_termine():
                raise ValueError(
                    f"Impossible de générer le tour suivant : le match {match.equipe_dom.nom} vs {match.equipe_ext.nom} n'est pas terminé !")
            if match.score_dom > match.score_ext:
                qualifies.append(match.equipe_dom)
                elimines.append(match.equipe_ext)
            elif match.score_ext > match.score_dom:
                qualifies.append(match.equipe_ext)
                elimines.append(match.equipe_dom)
            else:
                raise ValueError(
                    f"Match nul détecté dans le match #{match.id}. Les matchs de Coupe doivent obligatoirement avoir un vainqueur !")
        
        if tour_precedent == 1:
            qualifies.extend(self.equipes_exemptees)
            self.equipes_exemptees = []
        
        if len(qualifies) == 1:
            print(f"Félicitations à {qualifies[0].nom} qui remporte la {self.nom} !")
            return self.matchs
        
        self.journee_courante = tour_precedent + 1
        nouveau_tour = self.journee_courante
        self.matchs[nouveau_tour] = []

        if len(matchs_tour_prec) == 2 and len(qualifies) == 2 and len(elimines) == 2:

            eq1_final = qualifies[0]
            eq2_final = qualifies[1]
            match_final = Match(nouveau_tour, eq1_final, eq2_final)
            self.matchs[nouveau_tour].append(match_final)
            print(f"[Système] Finale créée : {eq1_final.nom} vs {eq2_final.nom}")

            tour_troisieme_place = 1000 + nouveau_tour
            self.matchs[tour_troisieme_place] = [Match(tour_troisieme_place, elimines[0], elimines[1])]
            print(f"[Système] Match pour la 3e place créé : {elimines[0].nom} vs {elimines[1].nom}")
        else:
            random.shuffle(qualifies)
            while len(qualifies) >= 2:
                eq_dom = qualifies.pop(0)
                eq_ext = qualifies.pop(0)
                nouveau_match = Match(nouveau_tour, eq_dom, eq_ext)
                self.matchs[nouveau_tour].append(nouveau_match)
            print(f"[Système] Tour {nouveau_tour} généré avec succès ({len(self.matchs[nouveau_tour])} matchs créés)")
        
        return self.matchs

    def to_dict(self):
        data = super().to_dict()
        data["equipes_exemptees"] = [eq.id for eq in self.equipes_exemptees if eq is not None]
        data["taille_tableau"] = self.taille_tableau
        return data

    @classmethod
    def from_dict(cls, data):
        coupe = super().from_dict(data, generer_tour_suivant=False)
        exemptes_ids = data.get("equipes_exemptees", [])
        coupe.equipes_exemptees = [coupe.recuperer_eq_par_id(eq_id) for eq_id in exemptes_ids]
        coupe.taille_tableau = data.get("taille_tableau")

        if coupe.taille_tableau is None:
            nb_equipes = len(coupe.equipes)
            if nb_equipes >= 2:
                coupe.taille_tableau = 2 ** math.ceil(math.log2(nb_equipes))
        return coupe

    def obtenir_matchs_specials_coupe(self):
        """Retourne le match de finale et le match pour la 3e place s'ils existent"""
        final_match = None
        troisieme_place_match = None

        for num_tour, matchs_du_tour in sorted(self.matchs.items(), key=lambda item: int(item[0])):
            tour_int = int(num_tour)
            if tour_int >= 1000:
                if matchs_du_tour:
                    troisieme_place_match = matchs_du_tour[0]
                continue

            if matchs_du_tour and self.obtenir_nom_tour(tour_int) == "Finale":
                final_match = matchs_du_tour[0]

        return final_match, troisieme_place_match

    def obtenir_nom_tour(self, num_tour=None):
        """retourne le nom textuel du tour au lieu du numéro"""
        if num_tour is None:
            num_tour = self.journee_courante
        tour_int = int(num_tour)

        if tour_int >= 1000:
            return "Troisième place"
        
        matchs_du_tour = self.matchs.get(tour_int, []) or self.matchs.get(tour_int, [])
        nb_matchs = len(matchs_du_tour)

        if tour_int == 1 and self.taille_tableau:
            total_equipes = self.taille_tableau
        else:
            total_equipes = nb_matchs * 2

        nom_stage = {
            2: "Finale",
            4: "Demi-finale",
            8: "Quart de finale",
            16: "Huitième de finale",
            32: "Seizième de finale",
            64: "Trente-deuxième de finale"
        }.get(total_equipes)

        if nom_stage:
            return nom_stage

        if total_equipes > 2:
            return f"Tour {tour_int} ({total_equipes} équipes)"

        return f"Tour {tour_int}"
