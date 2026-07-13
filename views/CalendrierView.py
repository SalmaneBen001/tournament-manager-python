import tkinter as tk
from tkinter import ttk

class CalendrierView(ttk.Frame):
    """affichage de l'onglet calendrier"""

    def __init__(self, parent, controleur):
        super().__init__(parent)
        self.controleur = controleur
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg="#f5f5f7")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.conteneur_journees = ttk.Frame(self.canvas)

        self.conteneur_journees.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.id_fenetre_canvas = self.canvas.create_window((0, 0), window=self.conteneur_journees, anchor="nw")
        def _redimensionner_conteneur(event):
            self.canvas.itemconfigure(self.id_fenetre_canvas, width=event.width)

        self.canvas.bind("<Configure>", _redimensionner_conteneur)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.rafraichir()

    def rafraichir(self):
        """affichage du calendrier avec titres dynamiques pour la Coupe"""
        for widget in self.conteneur_journees.winfo_children():
            widget.destroy()
        if not self.controleur.tournoi:
            return
        t_actif = self.controleur.tournoi
        structure_matchs = getattr(t_actif, "matchs", {})
        
        for num_journee in sorted(structure_matchs.keys()):
            liste_matchs = structure_matchs[num_journee]
            if hasattr(t_actif, "obtenir_nom_tour") and callable(getattr(t_actif, "obtenir_nom_tour")):
                try:
                    texte_cadre = f" {t_actif.obtenir_nom_tour(num_journee)} "
                except Exception as e:
                    print(f"[CalendrierView] Erreur obtenir_nom_tour({num_journee}): {e}")
                    texte_cadre = f" Journée {num_journee} "
            else:
                texte_cadre = f" Journée {num_journee} "
            
            cadre_journee = ttk.LabelFrame(self.conteneur_journees, text=texte_cadre, padding=10)
            cadre_journee.pack(fill="x", expand=True, padx=10, pady=10)

            for match in liste_matchs:
                cadre_match = ttk.Frame(cadre_journee)
                cadre_match.pack(fill="x", expand=True, pady=4)

                est_termine = match.est_termine()
                style_statut = "MatchTermine.TLabel" if est_termine else "MatchAJouer.TLabel"
                texte_statut = "Terminé" if est_termine else "À jouer"

                if est_termine:
                    affichage_match = f"{match.equipe_dom.nom}   {match.score_dom} - {match.score_ext}   {match.equipe_ext.nom}"
                else:
                    affichage_match = f"{match.equipe_dom.nom}   vs   {match.equipe_ext.nom}"
                lbl_match = ttk.Label(cadre_match, text=affichage_match, style=style_statut)
                lbl_match.pack(side="left", padx=5, fill="x", expand=True)

                lbl_statut = ttk.Label(cadre_match, text=texte_statut, style=style_statut)
                lbl_statut.pack(side="right", padx=15)

                ttk.Separator(cadre_journee, orient="horizontal").pack(fill="x", pady=2)

                match_id = getattr(match, "id", None)
                cadre_match.bind("<Double-1>", lambda event, m_id=match_id: self.controleur.afficher_match(m_id))
                lbl_match.bind("<Double-1>", lambda event, m_id=match_id: self.controleur.afficher_match(m_id))
