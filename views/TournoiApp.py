import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from views.ClassementView import ClassementView
from views.JoueursView import JoueursView
from views.AnalysesView import AnalysesView
from views.CalendrierView import CalendrierView
from views.ConfigurationView import ConfigurationView

class TournoiApp(tk.Tk):
    """fenêtre principale et contrôleur central du gestionnaire"""

    def __init__(self, tournoi=None, stats_manager=None, data_manager=None):
        super().__init__()
        self.tournoi = tournoi
        self.stats = stats_manager
        self.data_manager = data_manager
        self.chemin_sauvegarde_actif = None
        self.title("Gestionnaire de Tournoi")
        self.geometry("1100x800")
        self.minsize(900, 650)
        self._configurer_styles_global()
        self._creer_structure_onglets()
        self.protocol("WM_DELETE_WINDOW", self.au_moment_de_fermer)

    def _configurer_styles_global(self):
        """configure un ttk.Style global pour harmoniser les couleurs et polices"""
        self.style = ttk.Style()
        self.style.theme_use("clam")
        couleur_fond = "#f5f5f7"
        couleur_primaire = "#1a365d"
        couleur_texte_onglet = "#ffffff"
        self.configure(bg=couleur_fond)
        self.style.configure("TNotebook", background=couleur_fond, padding=5)
        self.style.configure(
            "TNotebook.Tab",
            font=("Helvetica", 10, "bold"),
            padding=[10, 5], background="#e2e8f0",
            foreground="#4a5568")
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", couleur_primaire)],
            foreground=[("selected", couleur_texte_onglet)])
        self.style.configure(
            "Treeview",
            font=("Helvetica", 10),
            rowheight=25,
            background="#ffffff",
            fieldbackground="#ffffff"
        )
        self.style.configure(
            "Treeview.Heading",
            font=("Helvetica", 10, "bold"),
            background="#edf2f7",
            foreground="#2d3748"
        )
        self.style.configure("MatchTermine.TLabel", foreground="#2f855a", font=("Helvetica", 10, "bold"))
        self.style.configure("MatchAJouer.TLabel", foreground="#dd6b20", font=("Helvetica", 10, "bold"))

    def _creer_structure_onglets(self):
        """initialise le composant Notebook et configure ses cinq sous-onglets requis"""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.onglet_configuration = ConfigurationView(self.notebook, controleur=self)
        self.onglet_calendrier = CalendrierView(self.notebook, controleur=self)
        self.onglet_classement = ClassementView(self.notebook, controleur=self)
        self.onglet_joueurs = JoueursView(self.notebook, controleur=self)
        self.onglet_analyses = AnalysesView(self.notebook, controleur=self)
        self.notebook.add(self.onglet_configuration, text=" Configuration ")
        self.notebook.add(self.onglet_calendrier, text=" Calendrier ")
        self.notebook.add(self.onglet_classement, text=" Classement ")
        self.notebook.add(self.onglet_joueurs, text=" Joueurs ")
        self.notebook.add(self.onglet_analyses, text=" Analyses ")

    def demarrer(self):
        """démarre l'application du tournoi"""
        self.mainloop()

    def rafraichir_classement(self):
        """rafraichisse le classement (màj)"""
        self.onglet_classement.rafraichir()
        print("[Contrôleur] Classement mis à jour")

    def afficher_match(self, match_id):
        """récupère les informations d'un match"""
        if not self.tournoi:
            messagebox.showwarning("Action impossible", "Aucun tournoi n'est actuellement chargé")
            return
        match_cible = None
        for liste_m in self.tournoi.matchs.values():
            for m in liste_m:
                if str(m.id) == str(match_id):
                    match_cible = m
                    break
            if match_cible:
                break
        if not match_cible:
            messagebox.showerror("Erreur", f"Le match ID {match_id} est introuvable")
            return
        if hasattr(match_cible, "est_termine") and match_cible.est_termine():
            messagebox.showwarning(
                "Match déjà joué",
                "Ce match est déjà terminé. Les résultats ne peuvent plus être modifiés."
            )
            return
        from views.SaisieResultatView import SaisieResultatView
        SaisieResultatView(parent=self, match=match_cible)

    def notifier_changement_donnees(self):
        """force la mise à jour visuelle complète de tous les onglets de l'application"""
        if self.tournoi:
            from managers.StatistiquesManager import StatistiquesManager
            self.stats = StatistiquesManager(self.tournoi)
        self.rafraichir_classement()

        if hasattr(self, "onglet_calendrier") and hasattr(self.onglet_calendrier, "rafraichir"):
            self.onglet_calendrier.rafraichir()

        if hasattr(self, "onglet_joueurs") and hasattr(self.onglet_joueurs, "rafraichir"):
            self.onglet_joueurs.rafraichir()

        if hasattr(self, "onglet_analyses") and hasattr(self.onglet_analyses, "rafraichir_listes_equipes"):
            self.onglet_analyses.rafraichir_listes_equipes()

    def au_moment_de_fermer(self):
        if self.tournoi and self.chemin_sauvegarde_actif is None:
            reponse = messagebox.askyesnocancel(
                "Quitter l'application",
                "Attention ! Votre tournoi actuel n'a jamais été sauvegardé.\n\n"
                "Voulez-vous l'enregistrer dans votre répertoire avant de quitter ?"
            )
            if reponse:
                if hasattr(self, "onglet_configuration") and hasattr(self.onglet_configuration,
                                                                     "_action_sauvegarder_json"):
                    self.onglet_configuration.sauvegarder_tournoi_manuel()
                self.destroy()
            elif reponse is False:
                self.destroy()
            else:
                return
        else:
            self.destroy()
