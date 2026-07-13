from tkinter import ttk

class JoueursView(ttk.Frame):
    """affichage des statistiques des joueurs"""
    def __init__(self, parent, controleur):
        super().__init__(parent)
        self.controleur = controleur
        self.cadre_mvp = ttk.LabelFrame(self, text=" Meilleur Joueur du Tournoi (MVP) ", padding=15)
        self.cadre_mvp.pack(fill="x", padx=10, pady=10)
        self.lbl_mvp_nom = ttk.Label(self.cadre_mvp, text="Aucun tournoi actif", font=("Helvetica", 12, "bold"))
        self.lbl_mvp_nom.pack(anchor="w")
        self.lbl_mvp_score = ttk.Label(self.cadre_mvp, text="Score MVP : --", font=("Helvetica", 10, "italic"))
        self.lbl_mvp_score.pack(anchor="w", pady=2)
        self.conteneur_tables = ttk.Frame(self)
        self.conteneur_tables.pack(fill="both", expand=True, padx=5, pady=5)
        self._configurer_tableau_buteurs()
        self._configurer_tableau_passeurs()
        self.rafraichir()

    def _configurer_tableau_buteurs(self):
        """configure la structure du tableau des buteurs"""
        cadre_buteurs = ttk.LabelFrame(self.conteneur_tables, text=" Meilleurs Buteurs ", padding=5)
        cadre_buteurs.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.colonnes_buteurs = ("Joueur", "Equipe", "Buts")
        self.tree_buteurs = ttk.Treeview(cadre_buteurs, columns=self.colonnes_buteurs, show="headings")
        self.tree_buteurs.pack(fill="both", expand=True)
        for col in self.colonnes_buteurs:
            self.tree_buteurs.heading(col, text=col, anchor="center")
            self.tree_buteurs.column(
                col,
                width=100,
                anchor="center" if col == "Buts" else "w"
            )

    def _configurer_tableau_passeurs(self):
        """configure la structure du tableau des passeurs"""
        cadre_passeurs = ttk.LabelFrame(self.conteneur_tables, text=" Meilleurs Passeurs ", padding=5)
        cadre_passeurs.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        self.colonnes_passeurs = ("Joueur", "Equipe", "Passes")
        self.tree_passeurs = ttk.Treeview(cadre_passeurs, columns=self.colonnes_passeurs, show="headings")
        self.tree_passeurs.pack(fill="both", expand=True)
        for col in self.colonnes_passeurs:
            self.tree_passeurs.heading(col, text=col, anchor="center")
            self.tree_passeurs.column(
                col,
                width=100,
                anchor="center" if col == "Passes" else "w"
            )

    def rafraichir(self):
        """affichage des données depuis stats"""
        for item in self.tree_buteurs.get_children():
            self.tree_buteurs.delete(item)
        for item in self.tree_passeurs.get_children():
            self.tree_passeurs.delete(item)
        if not self.controleur.tournoi or not self.controleur.stats:
            return
        dict_buteurs = self.controleur.stats.top_buteurs_to_dict()
        dict_passeurs = self.controleur.stats.top_passeurs_to_dict()
        dict_mvp = self.controleur.stats.mvp_to_dict()
        for joueur in dict_buteurs:
            self.tree_buteurs.insert(
                "",
                "end",
                values=(joueur["joueur"], joueur["equipe"], joueur["statistiques"])
            )
        for joueur in dict_passeurs:
            self.tree_passeurs.insert(
                "",
                "end",
                values=(joueur["joueur"], joueur["equipe"], joueur["statistiques"])
            )
        if dict_mvp:
            self.lbl_mvp_nom.config(text=f" {dict_mvp['joueur']} ({dict_mvp['equipe']})")
            self.lbl_mvp_score.config(text=f"Score de performance globale (MVP) : {dict_mvp['score_mvp']:.2f} pts")
        else:
            self.lbl_mvp_nom.config(text="Aucune donnée disponible")
            self.lbl_mvp_score.config(text="Score MVP : --")