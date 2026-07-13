import tkinter as tk
from tkinter import ttk, messagebox

class SaisieResultatView(tk.Toplevel):
    """affichage onglet saisie de résultat"""

    def __init__(self, parent, match):
        super().__init__(parent)
        self.parent = parent
        self.match = match
        nom_etape = f"Journée {match.journee}"
        ctrl = getattr(parent, "controleur", parent)
        tournoi_actif = getattr(parent, "tournoi", getattr(ctrl, "tournoi", None))
        if tournoi_actif and hasattr(tournoi_actif, "obtenir_nom_tour") and tournoi_actif.type == "Coupe":
            nom_etape = tournoi_actif.obtenir_nom_tour(match.journee)
        self.title(f"{nom_etape} - Saisie : {match.equipe_dom.nom} vs {match.equipe_ext.nom}")
        self.geometry("550x700")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._creer_widgets_formulaire()
        self.bind("<Return>", lambda event: self._valider_et_enregistrer())
        self.spin_score_dom.focus_set()

    def _creer_widgets_formulaire(self):
        """création d'objets de formulaire"""
        cadre_scores = ttk.LabelFrame(self, text=" Score du Match ", padding=15)
        cadre_scores.pack(fill="x", padx=15, pady=5)

        cadre_dom = ttk.Frame(cadre_scores)
        cadre_dom.pack(side="left", expand=True)
        ttk.Label(cadre_dom, text=self.match.equipe_dom.nom, font=("Helvetica", 10, "bold")).pack(pady=2)

        self.spin_score_dom = ttk.Spinbox(cadre_dom, from_=0, to=99, width=5, font=("Helvetica", 12))
        self.spin_score_dom.insert(0, str(self.match.score_dom if hasattr(self.match, "score_dom") else 0))
        self.spin_score_dom.pack(pady=5)

        ttk.Label(cadre_scores, text="VS", font=("Helvetica", 14, "bold")).pack(side="left", pady=10)

        cadre_ext = ttk.Frame(cadre_scores)
        cadre_ext.pack(side="right", expand=True)
        ttk.Label(cadre_ext, text=self.match.equipe_ext.nom, font=("Helvetica", 10, "bold")).pack(pady=2)

        self.spin_score_ext = ttk.Spinbox(cadre_ext, from_=0, to=99, width=5, font=("Helvetica", 12))
        self.spin_score_ext.insert(0, str(self.match.score_ext if hasattr(self.match, "score_ext") else 0))
        self.spin_score_ext.pack(pady=5)

        cadre_stats = ttk.LabelFrame(self, text=" Buteurs & Passeurs ", padding=15)
        cadre_stats.pack(fill="x", padx=15, pady=5)

        ttk.Label(cadre_stats, text="Buteurs :").pack(anchor="w", pady=2)
        self.ent_buteurs = ttk.Entry(cadre_stats, width=50)
        self.ent_buteurs.pack(fill="x", pady=5)

        ttk.Label(cadre_stats, text="Passeurs :").pack(anchor="w", pady=2)
        self.ent_passeurs = ttk.Entry(cadre_stats, width=50)
        self.ent_passeurs.pack(fill="x", pady=5)

        cadre_disciplinaire = ttk.LabelFrame(self, text=" Cartons du Match ", padding=10)
        cadre_disciplinaire.pack(fill="both", expand=True, padx=15, pady=5)

        canvas = tk.Canvas(cadre_disciplinaire, borderwidth=0, highlightthickness=0, height=200)
        scrollbar = ttk.Scrollbar(cadre_disciplinaire, orient="vertical", command=canvas.yview)
        cadre_defilable = ttk.Frame(canvas)

        cadre_defilable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=cadre_defilable, anchor="nw", width=480)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _sur_molette(event):
            try:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        canvas.bind_all("<MouseWheel>", _sur_molette)

        dict_cartons_existants = self.match.cartons
        jaunes_enregistres = dict_cartons_existants.get("jaunes", {})
        rouges_enregistres = dict_cartons_existants.get("rouges", {})

        self.vars_jaunes = {}
        self.vars_rouges = {}

        cadre_defilable.columnconfigure(0, weight=1)
        cadre_defilable.columnconfigure(1, weight=1)

        cadre_joueurs_dom = ttk.Frame(cadre_defilable, padding=5)
        cadre_joueurs_dom.grid(row=0, column=0, sticky="nsew")
        ttk.Label(cadre_joueurs_dom, text=self.match.equipe_dom.nom, font=("Helvetica", 9, "bold")).pack(anchor="w",
                                                                                                         pady=5)

        for joueur in self.match.equipe_dom.joueurs:
            cadre_ligne = ttk.Frame(cadre_joueurs_dom)
            cadre_ligne.pack(fill="x", pady=2)

            var_j = tk.BooleanVar(value=(joueur in jaunes_enregistres))
            self.vars_jaunes[joueur] = var_j
            ttk.Checkbutton(cadre_ligne, variable=var_j).pack(side="left")

            tk.Label(cadre_ligne, text=" J ", bg="#FFD700", fg="black", font=("Helvetica", 8, "bold"), width=2).pack(
                side="left", padx=2)

            var_r = tk.BooleanVar(value=(joueur in rouges_enregistres))
            self.vars_rouges[joueur] = var_r
            ttk.Checkbutton(cadre_ligne, variable=var_r).pack(side="left", padx=(5, 0))

            tk.Label(cadre_ligne, text=" R ", bg="#DC143C", fg="white", font=("Helvetica", 8, "bold"), width=2).pack(
                side="left", padx=2)
            ttk.Label(cadre_ligne, text=joueur.nom, font=("Helvetica", 9)).pack(side="left", padx=5)

        cadre_joueurs_ext = ttk.Frame(cadre_defilable, padding=5)
        cadre_joueurs_ext.grid(row=0, column=1, sticky="nsew")
        ttk.Label(cadre_joueurs_ext, text=self.match.equipe_ext.nom, font=("Helvetica", 9, "bold")).pack(anchor="w",
                                                                                                         pady=5)

        for joueur in self.match.equipe_ext.joueurs:
            cadre_ligne = ttk.Frame(cadre_joueurs_ext)
            cadre_ligne.pack(fill="x", pady=2)

            var_j = tk.BooleanVar(value=(joueur in jaunes_enregistres))
            self.vars_jaunes[joueur] = var_j
            ttk.Checkbutton(cadre_ligne, variable=var_j).pack(side="left")

            tk.Label(cadre_ligne, text=" J ", bg="#FFD700", fg="black", font=("Helvetica", 8, "bold"), width=2).pack(
                side="left", padx=2)

            var_r = tk.BooleanVar(value=(joueur in rouges_enregistres))
            self.vars_rouges[joueur] = var_r
            ttk.Checkbutton(cadre_ligne, variable=var_r).pack(side="left", padx=(5, 0))

            tk.Label(cadre_ligne, text=" R ", bg="#DC143C", fg="white", font=("Helvetica", 8, "bold"), width=2).pack(
                side="left", padx=2)
            ttk.Label(cadre_ligne, text=joueur.nom, font=("Helvetica", 9)).pack(side="left", padx=5)

        cadre_boutons = ttk.Frame(self, padding=10)
        cadre_boutons.pack(fill="x", side="bottom")

        btn_enregistrer = ttk.Button(cadre_boutons, text="Enregistrer le résultat",
                                     command=self._valider_et_enregistrer)
        btn_enregistrer.pack(pady=5, ipadx=20, ipady=5)

    def _obtenir_tournoi_actif(self):
        """renvoie le tournoi actif depuis le parent ou son contrôleur (s'il existe)"""
        if hasattr(self.parent, "tournoi") and self.parent.tournoi is not None:
            return self.parent.tournoi
        ctrl = getattr(self.parent, "controleur", None)
        if ctrl and hasattr(ctrl, "tournoi"):
            return ctrl.tournoi
        return None

    def _valider_et_enregistrer(self):
        """récupération de la saisie et insertion des données"""
        try:
            sc_dom = int(self.spin_score_dom.get())
            sc_ext = int(self.spin_score_ext.get())
        except ValueError:
            messagebox.showerror("Saisie invalide", "Les scores doivent être des nombres entiers")
            return

        tournoi_actif = self._obtenir_tournoi_actif()
        if getattr(tournoi_actif, "type", None) == "Coupe" and sc_dom == sc_ext:
            messagebox.showerror(
                "Score invalide",
                "Un match de Coupe doit obligatoirement avoir un vainqueur."
            )
            return

        # Traitement des buteurs
        liste_buteurs = [b.strip() for b in self.ent_buteurs.get().split(",") if b.strip()]
        dict_buteurs_metier = {}
        for element in liste_buteurs:
            if ":" in element:
                nom, qty_str = element.split(":", 1)
                nom = nom.strip()
                try:
                    quantite = int(qty_str.strip())
                except ValueError:
                    messagebox.showerror("Saisie invalide", f"Quantité invalide pour le buteur: {element}")
                    return
            else:
                nom = element
                quantite = 1

            joueur_obj = None
            for joueur in self.match.equipe_dom.joueurs + self.match.equipe_ext.joueurs:
                if joueur.nom.lower() == nom.lower():
                    joueur_obj = joueur
                    break

            if joueur_obj:
                dict_buteurs_metier[joueur_obj] = dict_buteurs_metier.get(joueur_obj, 0) + quantite
            else:
                messagebox.showerror("Joueur introuvable", f"Le buteur '{nom}' ne joue pas dans ce match.")
                return

        # Traitement des passeurs
        liste_passeurs = [p.strip() for p in self.ent_passeurs.get().split(",") if p.strip()]
        dict_passeurs_metier = {}
        for p in liste_passeurs:
            if ":" in p:
                nom, qty_str = p.split(":", 1)
                nom = nom.strip()
                try:
                    quantite = int(qty_str.strip())
                except ValueError:
                    messagebox.showerror("Saisie invalide", f"Quantité invalide pour le passeur: {p}")
                    return
            else:
                nom = p
                quantite = 1

            joueur_obj = None
            for joueur in self.match.equipe_dom.joueurs + self.match.equipe_ext.joueurs:
                if joueur.nom.lower() == nom.lower():
                    joueur_obj = joueur
                    break

            if joueur_obj:
                dict_passeurs_metier[joueur_obj] = dict_passeurs_metier.get(joueur_obj, 0) + quantite
            else:
                messagebox.showerror("Joueur introuvable", f"Le passeur '{nom}' ne joue pas dans ce match.")
                return

        total_buts_saisis = sum(dict_buteurs_metier.values())
        if total_buts_saisis != sc_dom + sc_ext:
            messagebox.showerror(
                "Saisie incohérente",
                f"Le total des buts saisis ({total_buts_saisis}) ne correspond pas au score "
                f"({sc_dom + sc_ext} buts)."
            )
            return

        # Traitement des cartons
        dict_jaunes_metier = {}
        for joueur, var_bool in self.vars_jaunes.items():
            if var_bool.get():
                dict_jaunes_metier[joueur] = dict_jaunes_metier.get(joueur, 0) + 1

        dict_rouges_metier = {}
        for joueur, var_bool in self.vars_rouges.items():
            if var_bool.get():
                dict_rouges_metier[joueur] = dict_rouges_metier.get(joueur, 0) + 1

        donnees_cartons = {
            "jaunes": dict_jaunes_metier,
            "rouges": dict_rouges_metier
        }

        # Enregistrement et sauvegarde automatique
        try:
            self.match.enregistrer_resultat(
                score_dom=sc_dom,
                score_ext=sc_ext,
                buteurs=dict_buteurs_metier,
                passeurs=dict_passeurs_metier,
                cartons=donnees_cartons
            )
            if tournoi_actif:
                tournoi_actif.mettre_a_jour_classement(generer_tour_suivant=False)
                structure_matchs = getattr(tournoi_actif, "matchs", {})
                j_actuelle = getattr(tournoi_actif, "journee_courante", 1)
                matchs_du_tour = structure_matchs.get(j_actuelle, []) or structure_matchs.get(str(j_actuelle), [])
                match_journee = getattr(self.match, "journee", j_actuelle)
                if matchs_du_tour and str(match_journee) == str(j_actuelle) and all(m.est_termine() for m in matchs_du_tour):
                    if hasattr(tournoi_actif, "generer_tour_suivant"):
                        print(
                            f"[Système] Tous les matchs du tour {j_actuelle} sont finis. Déclenchement du tour suivant...")
                        tournoi_actif.generer_tour_suivant()
            if hasattr(self.parent, "notifier_changement_donnees"):
                self.parent.notifier_changement_donnees()
            ctrl = getattr(self.parent, "controleur", self.parent)
            if hasattr(ctrl, "chemin_sauvegarde_actif") and ctrl.chemin_sauvegarde_actif is not None:
                nom_sauvegarde = ctrl.chemin_sauvegarde_actif
                if tournoi_actif and hasattr(tournoi_actif, "to_dict"):
                    donnees_a_jour = tournoi_actif.to_dict()
                    if hasattr(ctrl, "data_manager") and ctrl.data_manager is not None:
                        ctrl.data_manager.sauvegarder_json(nom_sauvegarde, donnees_a_jour)
                        print(f"[Système] Auto-save : Tournoi sauvegardé avec succès dans '{nom_sauvegarde}'")

            self.destroy()
            messagebox.showinfo("Succès", "Le résultat du match a été enregistré et le tournoi mis à jour.")

        except Exception as e:
            messagebox.showerror("Erreur métier", f"Impossible d'enregistrer le résultat.\nDétails : {str(e)}")
