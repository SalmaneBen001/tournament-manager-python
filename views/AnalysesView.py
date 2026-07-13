from tkinter import ttk

class AnalysesView(ttk.Frame):
    """l'onglet d'analyses comparatives et de prédictions"""

    def __init__(self, parent, controleur):
        super().__init__(parent)
        self.controleur = controleur
        self.cadre_selection = ttk.LabelFrame(self, text=" Sélection des équipes pour Face-à-Face ", padding=10)
        self.cadre_selection.pack(fill="x", padx=10, pady=10)
        ttk.Label(self.cadre_selection, text="Équipe Domicile :").pack(side="left", padx=5)
        self.combo_equipe_dom = ttk.Combobox(self.cadre_selection, state="readonly", width=20)
        self.combo_equipe_dom.pack(side="left", padx=5)
        ttk.Label(self.cadre_selection, text="vs").pack(side="left", padx=10)
        ttk.Label(self.cadre_selection, text="Équipe Extérieur :").pack(side="left", padx=5)
        self.combo_equipe_ext = ttk.Combobox(self.cadre_selection, state="readonly", width=20)
        self.combo_equipe_ext.pack(side="left", padx=5)
        self.btn_analyser = ttk.Button(self.cadre_selection, text="Lancer l'analyse", command=self._executer_analyse)
        self.btn_analyser.pack(side="left", padx=15)
        self.conteneur_resultats = ttk.Frame(self)
        self.conteneur_resultats.pack(fill="both", expand=True, padx=5, pady=5)
        self._configurer_historique()
        self._configurer_predictions()
        self.rafraichir_listes_equipes()

    def _configurer_historique(self):
        """configure le tableau affichant l'historique des confrontations"""
        cadre_hist = ttk.LabelFrame(self.conteneur_resultats, text=" Historique des Confrontations ", padding=5)
        cadre_hist.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.colonnes_historique = ("Type de Bilan", "Quantité", "Détail")
        self.tree_historique = ttk.Treeview(cadre_hist, columns=self.colonnes_historique, show="headings")
        self.tree_historique.pack(fill="both", expand=True)
        for col in self.colonnes_historique:
            self.tree_historique.heading(col, text=col, anchor="center")
            self.tree_historique.column(col, width=100, anchor="center")

    def _configurer_predictions(self):
        """configure la zone d'affichage des prédictions"""
        cadre_pred = ttk.LabelFrame(self.conteneur_resultats, text=" Prédictions (Simulation Monte Carlo) ", padding=15)
        cadre_pred.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        self.lbl_intro_pred = ttk.Label(cadre_pred, text="Probabilités estimées pour la rencontre :",
                                        font=("Helvetica", 10, "bold"))
        self.lbl_intro_pred.pack(anchor="w", pady=5)
        self.lbl_proba_dom = ttk.Label(cadre_pred, text="Victoire Domicile : -- %", font=("Helvetica", 10))
        self.lbl_proba_dom.pack(anchor="w", pady=2)
        self.lbl_proba_nul = ttk.Label(cadre_pred, text="Match Nul : -- %", font=("Helvetica", 10))
        self.lbl_proba_nul.pack(anchor="w", pady=2)
        self.lbl_proba_ext = ttk.Label(cadre_pred, text="Victoire Extérieur : -- %", font=("Helvetica", 10))
        self.lbl_proba_ext.pack(anchor="w", pady=2)

    def rafraichir_listes_equipes(self):
        """tri des noms d'équipes affichées dans le combobox pour une bonne expérience utilisateur"""
        if not self.controleur.tournoi:
            self.combo_equipe_dom.config(values=[])
            self.combo_equipe_ext.config(values=[])
            return
        noms_equipes = sorted([equipe.nom for equipe in self.controleur.tournoi.equipes.values()])
        self.combo_equipe_dom.config(values=noms_equipes)
        self.combo_equipe_ext.config(values=noms_equipes)

    def _executer_analyse(self):
        """Récupère les données de confrontation et de simulation pour mettre à jour l'affichage."""
        nom_dom = self.combo_equipe_dom.get()
        nom_ext = self.combo_equipe_ext.get()
        if not nom_dom or not nom_ext or nom_dom == nom_ext:
            return
        if not self.controleur.tournoi or not self.controleur.stats:
            return
        for item in self.tree_historique.get_children():
            self.tree_historique.delete(item)
        eq_dom = self.controleur.tournoi.recuperer_eq_par_nom(nom_dom)
        eq_ext = self.controleur.tournoi.recuperer_eq_par_nom(nom_ext)
        if not eq_dom or not eq_ext:
            return
        analyse_globale = self.controleur.stats.analyse_confrontation(eq_dom, eq_ext)
        bilan_direct = analyse_globale.get("historique_directe", {})
        victoires_dom = bilan_direct.get(f"victoires_{nom_dom}", 0)
        victoires_ext = bilan_direct.get(f"victoires_{nom_ext}", 0)
        matchs_nuls = bilan_direct.get("nuls", 0)
        self.tree_historique.insert("", "end", values=("Victoires Domicile", victoires_dom, nom_dom))
        self.tree_historique.insert("", "end", values=("Victoires Extérieur", victoires_ext, nom_ext))
        self.tree_historique.insert("", "end", values=("Matchs Nuls", matchs_nuls, "Aucun"))
        try:
            chaine_prediction = self.controleur.tournoi.predire_resultat(eq_dom, eq_ext)
            morceaux = chaine_prediction.split(" | ")
            if len(morceaux) == 3:
                self.lbl_proba_dom.config(text=morceaux[0])
                self.lbl_proba_nul.config(text=morceaux[1])
                self.lbl_proba_ext.config(text=morceaux[2])
            else:
                self.lbl_proba_dom.config(text=chaine_prediction)
                self.lbl_proba_nul.config(text="")
                self.lbl_proba_ext.config(text="")

        except Exception as e:
            self.lbl_proba_dom.config(text=f"Victoire {nom_dom} : -- %")
            self.lbl_proba_nul.config(text="Match Nul : -- %")
            self.lbl_proba_ext.config(text=f"Victoire {nom_ext} : -- %")
            print(f"[Erreur Simulation] {str(e)}")
