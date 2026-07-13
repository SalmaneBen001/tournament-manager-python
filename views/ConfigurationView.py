from tkinter import ttk, messagebox, filedialog
from pathlib import Path

class ConfigurationView(ttk.Frame):
    """la fenêtre gérant la manipulation des fichiers (JSON, CSV, TXT)"""
    def __init__(self, parent, controleur):
        super().__init__(parent)
        self.controleur = controleur
        self.cadre_gestion = ttk.LabelFrame(self, text=" Nouveau Tournoi ", padding=15)
        self.cadre_gestion.pack(fill="x", padx=20, pady=15)
        self.lbl_info = ttk.Label(
            self.cadre_gestion,
            text="Générez un nouveau calendrier et configurez vos équipes pas à pas :",
            font=("Helvetica", 10)
        )
        self.lbl_info.pack(anchor="w", pady=5)
        self.btn_wizard = ttk.Button(
            self.cadre_gestion,
            text="Lancer l'Assistant de Création",
            command=self._ouvrir_assistant_creation
        )
        self.btn_wizard.pack(anchor="w", pady=5)
        self.cadre_fichiers = ttk.LabelFrame(self, text=" Sauvegarde & Chargement (JSON) ", padding=15)
        self.cadre_fichiers.pack(fill="x", padx=20, pady=15)
        self.conteneur_boutons_json = ttk.Frame(self.cadre_fichiers)
        self.conteneur_boutons_json.pack(fill="x", pady=5)
        self.btn_charger = ttk.Button(
            self.conteneur_boutons_json,
            text="Charger un Tournoi (JSON)",
            command=self._action_charger_json
        )
        self.btn_charger.pack(side="left", padx=5)
        self.btn_sauvegarder = ttk.Button(
            self.conteneur_boutons_json,
            text="Enregistrer le Tournoi (JSON)",
            command=self._action_sauvegarder_json
        )
        self.btn_sauvegarder.pack(side="left", padx=5)
        self.cadre_exports = ttk.LabelFrame(self, text=" Exports & Rapports (CSV / TXT) ", padding=15)
        self.cadre_exports.pack(fill="x", padx=20, pady=15)
        self.conteneur_boutons_export = ttk.Frame(self.cadre_exports)
        self.conteneur_boutons_export.pack(fill="x", pady=5)
        self.btn_export_csv = ttk.Button(
            self.conteneur_boutons_export,
            text="Exporter les Statistiques (CSV)",
            command=self._action_exporter_csv
        )
        self.btn_export_csv.pack(side="left", padx=5)
        self.btn_export_txt = ttk.Button(
            self.conteneur_boutons_export,
            text="Générer le Rapport de Journée (TXT)",
            command=self._action_exporter_txt
        )
        self.btn_export_txt.pack(side="left", padx=5)
    def _ouvrir_assistant_creation(self):
        """Déclenche l'ouverture de la fenêtre de création du tournoi"""
        from views.CreationTournoiView import CreationTournoiView
        CreationTournoiView(parent=self.controleur)

    def _action_charger_json(self):
        """charge les fichiers json à l'aide du DataManager"""
        if not self.controleur.data_manager:
            messagebox.showwarning("Erreur", "Le module DataManager n'est pas initialisé")
            return
        chemin_complet = filedialog.askopenfilename(
            title="Choisir un fichier de tournoi",
            initialdir=self.controleur.data_manager.chemin_json,
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        if not chemin_complet:
            return
        nom_fichier = Path(chemin_complet).name
        try:
            donnees_dict = self.controleur.data_manager.charger_json(
                nom_fichier, chemin_complet=chemin_complet
            )
            if donnees_dict is None:
                messagebox.showerror("Erreur", f"Le fichier '{nom_fichier}' n'a pas pu être chargé (voir console)")
                return
            from managers.Tournoi import ChampionnatTournoi, CoupeTournoi, Tournoi
            type_tournoi = donnees_dict.get("type")
            if type_tournoi == "Coupe":
                self.controleur.tournoi = CoupeTournoi.from_dict(donnees_dict)
            elif type_tournoi == "Championnat":
                self.controleur.tournoi = ChampionnatTournoi.from_dict(donnees_dict)
            else:
                self.controleur.tournoi = Tournoi.from_dict(donnees_dict)
            self.controleur.chemin_sauvegarde_actif = nom_fichier
            if self.controleur.stats:
                self.controleur.stats.tournoi = self.controleur.tournoi
            self.controleur.notifier_changement_donnees()
            messagebox.showinfo("Succès", "Le tournoi a été chargé avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le tournoi.\nDétails : {str(e)}")

    def sauvegarder_tournoi_manuel(self):
        """passerelle publique permettant au contrôleur de déclencher la sauvegarde"""
        self._action_sauvegarder_json()

    def _action_sauvegarder_json(self):
        """sauvegarde automatiquement le fichier json sous le nom du tournoi avec confirmation si doublon"""
        if not self.controleur.data_manager or not self.controleur.tournoi:
            messagebox.showwarning("Action impossible", "Aucun tournoi actif à sauvegarder")
            return
        try:
            nom_tournoi = getattr(self.controleur.tournoi, "nom", "tournoi")
            nom_fichier_clean = f"{nom_tournoi.lower().replace(' ', '_').strip()}.json"
            dossier_json = Path(self.controleur.data_manager.chemin_json)
            fichier_cible = dossier_json / nom_fichier_clean
            if fichier_cible.exists():
                reponse = messagebox.askyesno(
                    "Fichier existant",
                    f"Un fichier de sauvegarde nommé '{nom_fichier_clean}' existe déjà dans le répertoire.\n\n"
                    f"Voulez-vous vraiment l'écraser et remplacer les données existantes ?"
                )
                if not reponse:
                    return
            donnees_dict = self.controleur.tournoi.to_dict()
            succes = self.controleur.data_manager.sauvegarder_json(nom_fichier_clean, donnees_dict)
            if succes:
                self.controleur.chemin_sauvegarde_actif = nom_fichier_clean
                messagebox.showinfo(
                    "Succès",
                    f"Le tournoi '{nom_tournoi}' a été sauvegardé avec succès !\n"
                    f"Fichier : {nom_fichier_clean}"
                )
            else:
                messagebox.showerror("Erreur", "La sauvegarde a échoué. Vérifiez la console.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde : {str(e)}")

    def _action_exporter_csv(self):
        """prépare et exporte les fichiers csv"""
        if not self.controleur.tournoi or not self.controleur.data_manager:
            messagebox.showwarning("Action impossible", "Aucun tournoi actif")
            return
        liste_joueurs_formatee = []
        for equipe in self.controleur.tournoi.equipes.values():
            for joueur in equipe.joueurs:
                jaunes = getattr(joueur, "cartons_jaunes", 0)
                rouges = getattr(joueur, "cartons_rouges", 0)
                liste_joueurs_formatee.append({
                    "Nom": joueur.nom,
                    "Buts": joueur.buts,
                    "Passes": joueur.passes,
                    "Cartons jaunes": jaunes,
                    "Cartons rouges": rouges
                })
        equipes_triees = self.controleur.tournoi.get_classement()
        num_journee = getattr(self.controleur.tournoi, "journee_courante", 1)
        structure_matchs = getattr(self.controleur.tournoi, "matchs", {})
        matchs_journee = structure_matchs.get(num_journee, [])
        try:
            self.controleur.data_manager.exporter_csv(
                liste_joueurs=liste_joueurs_formatee,
                equipes_triees=equipes_triees,
                liste_matchs=matchs_journee,
                numero_journee=num_journee
            )
            messagebox.showinfo("Succès", "Les fichiers CSV ont été exportés avec succès dans le dossier dédié !")
        except Exception as e:
            messagebox.showerror("Erreur export", f"Une erreur est survenue lors de l'exportation : {str(e)}")

    def _action_exporter_txt(self):
        """exporte dynamiquement le rapport de la journée active en fichier txt"""
        if not self.controleur.data_manager or not self.controleur.tournoi:
            messagebox.showwarning("Action impossible", "Aucun tournoi actif")
            return
        try:
            num_journee_active = getattr(self.controleur.tournoi, "journee_courante", 1)
            structure_matchs = getattr(self.controleur.tournoi, "matchs", {})
            matchs_journee = structure_matchs.get(num_journee_active, [])
            if not matchs_journee:
                messagebox.showwarning("Export impossible", f"Aucun match trouvé pour la Journée {num_journee_active}")
                return
            succes = self.controleur.data_manager.rapport_journee_txt(matchs_journee, numero_journee=num_journee_active)
            if succes:
                messagebox.showinfo(
                    "Rapport Généré",
                    f"Le fichier 'rapport_journee_{num_journee_active}.txt' a été créé avec succès !"
                )
            else:
                messagebox.showerror("Erreur", "La création du rapport TXT a échoué. Vérifiez la console.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de générer le rapport textuel : {str(e)}")
