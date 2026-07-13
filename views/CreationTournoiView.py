import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

class CreationTournoiView(tk.Toplevel):
    """Assistant pour la configuration d'une tournoi"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Assistant de création de tournoi")
        self.geometry("650x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.etape_actuelle = 0
        self.nom_tournoi_final = "Mon Tournoi"
        self.format_final = "Championnat"
        self.couleur_selectionnee = "#2196F3"
        self.equipes_creees = []
        self.couleurs_par_equipe = {}
        self.joueurs_par_equipe = {}
        self.cadre_etape = ttk.Frame(self, padding=20)
        self.cadre_etape.pack(fill="both", expand=True)
        self.cadre_boutons = ttk.Frame(self, padding=10)
        self.cadre_boutons.pack(fill="x", side="bottom")
        self.btn_precedent = ttk.Button(self.cadre_boutons, text="⬅ Précédent", command=self._etape_precedente)
        self.btn_precedent.pack(side="left", padx=5)
        self.btn_suivant = ttk.Button(self.cadre_boutons, text="Suivant ➡", command=self._etape_suivante)
        self.btn_suivant.pack(side="right", padx=5)
        self._afficher_etape()

    def _afficher_etape(self):
        """affiche l'étape active"""
        for widget in self.cadre_etape.winfo_children():
            widget.destroy()
        self.btn_precedent.pack_forget() if self.etape_actuelle == 0 else self.btn_precedent.pack(side="left", padx=5)
        texte_bouton_fin = "Générer le Calendrier" if self.etape_actuelle == 3 else "Suivant ➡"
        self.btn_suivant.config(text=texte_bouton_fin)

        if self.etape_actuelle == 0:
            self._dessiner_etape_infos()
        elif self.etape_actuelle == 1:
            self._dessiner_etape_equipes()
        elif self.etape_actuelle == 2:
            self._dessiner_etape_joueurs()
        elif self.etape_actuelle == 3:
            self._dessiner_etape_generation()

    def _dessiner_etape_infos(self):
        """dessine le formulaire des informations de base du tournoi"""
        lbl_titre = ttk.Label(self.cadre_etape, text="Étape 1 : Informations Générales", font=("Helvetica", 12, "bold"))
        lbl_titre.pack(anchor="w", pady=10)
        ttk.Label(self.cadre_etape, text="Nom du Tournoi :").pack(anchor="w", pady=5)
        self.ent_nom_tournoi = ttk.Entry(self.cadre_etape, width=40)
        self.ent_nom_tournoi.pack(anchor="w", pady=5)
        self.ent_nom_tournoi.insert(0, self.nom_tournoi_final)
        ttk.Label(self.cadre_etape, text="Format de la Compétition :").pack(anchor="w", pady=5)
        self.combo_format = ttk.Combobox(self.cadre_etape, values=["Championnat", "Coupe"], state="readonly", width=20)
        self.combo_format.pack(anchor="w", pady=5)
        self.combo_format.set(self.format_final)

    def _dessiner_etape_equipes(self):
        """dessine l'interface d'ajout des équipes"""
        lbl_titre = ttk.Label(self.cadre_etape, text="Étape 2 : Inscription des Équipes",
                              font=("Helvetica", 12, "bold"))
        lbl_titre.pack(anchor="w", pady=10)
        cadre_saisie = ttk.Frame(self.cadre_etape)
        cadre_saisie.pack(fill="x", pady=5)
        ttk.Label(cadre_saisie, text="Nom :").pack(side="left", padx=2)
        self.ent_nom_equipe = ttk.Entry(cadre_saisie, width=20)
        self.ent_nom_equipe.pack(side="left", padx=5)
        self.ent_nom_equipe.bind("<Return>", lambda e: self._ajouter_equipe_liste())
        ttk.Label(cadre_saisie, text="Couleur :").pack(side="left", padx=2)
        self.lbl_apercu_couleur = tk.Label(cadre_saisie, width=3, bg=self.couleur_selectionnee, relief="ridge")
        self.lbl_apercu_couleur.pack(side="left", padx=2)
        btn_choisir_couleur = ttk.Button(cadre_saisie, text="Choisir...", command=self._ouvrir_selecteur_couleur)
        btn_choisir_couleur.pack(side="left", padx=5)
        btn_ajouter = ttk.Button(cadre_saisie, text="Ajouter", command=self._ajouter_equipe_liste)
        btn_ajouter.pack(side="left", padx=5)
        self.listbox_equipes = tk.Listbox(self.cadre_etape, width=50, height=10, font=("Helvetica", 10))
        self.listbox_equipes.pack(pady=10)
        for eq in self.equipes_creees:
            couleur_eq = self.couleurs_par_equipe.get(eq, "#2196F3")
            self.listbox_equipes.insert(tk.END, f"{eq} ({couleur_eq})")

    def _ajouter_equipe_liste(self):
        """ajoute le nom et la couleur dans les structures locales"""
        nom = self.ent_nom_equipe.get().strip()
        couleur = self.couleur_selectionnee
        if not nom:
            return
        if nom in self.equipes_creees:
            messagebox.showwarning("Doublon", "Cette équipe est déjà inscrite")
            return
        self.equipes_creees.append(nom)
        self.couleurs_par_equipe[nom] = couleur
        self.joueurs_par_equipe[nom] = []
        self.listbox_equipes.insert(tk.END, f"{nom} ({couleur})")
        self.ent_nom_equipe.delete(0, tk.END)
        self.ent_nom_equipe.focus_set()

    def _ouvrir_selecteur_couleur(self):
        """ouverture du colorchooser"""
        resultat = colorchooser.askcolor(initialcolor=self.couleur_selectionnee)

        if resultat is not None:
            rgb, code_hex = resultat
            if isinstance(code_hex, str):
                self.couleur_selectionnee = code_hex
                self.lbl_apercu_couleur.config(bg=self.couleur_selectionnee)

    def _dessiner_etape_joueurs(self):
        """dessine l'espace pour affecter des joueurs aux équipes créées"""
        lbl_titre = ttk.Label(self.cadre_etape, text="Étape 3 : Effectifs des Joueurs", font=("Helvetica", 12, "bold"))
        lbl_titre.pack(anchor="w", pady=10)
        if not self.equipes_creees:
            ttk.Label(self.cadre_etape, text="Veuillez revenir à l'étape précédente pour ajouter des équipes").pack()
            return
        ttk.Label(self.cadre_etape, text="Sélectionnez une équipe :").pack(anchor="w")
        self.combo_choix_equipe = ttk.Combobox(self.cadre_etape, values=self.equipes_creees, state="readonly", width=25)
        self.combo_choix_equipe.pack(anchor="w", pady=5)
        self.combo_choix_equipe.bind("<<ComboboxSelected>>", self._changer_equipe_automatique)
        self.derniere_equipe_selectionnee = self.equipes_creees[0]
        self.combo_choix_equipe.set(self.derniere_equipe_selectionnee)
        ttk.Label(self.cadre_etape, text="Noms des joueurs :").pack(anchor="w",
                                                                                                       pady=5)
        self.txt_joueurs = tk.Text(self.cadre_etape, width=55, height=8, font=("Helvetica", 10))
        self.txt_joueurs.pack(pady=5)
        self._charger_effectif_dans_widget(self.derniere_equipe_selectionnee)

    def _changer_equipe_automatique(self, event):
        """sauvegarde l'ancienne équipe et charge la nouvelle"""
        if not hasattr(self, 'combo_choix_equipe'):
            return
        if hasattr(self, 'derniere_equipe_selectionnee') and self.derniere_equipe_selectionnee:
            self._sauvegarder_effectif_local(equipe_cible=self.derniere_equipe_selectionnee, afficher_pop_up=False)
        nouvelle_equipe = self.combo_choix_equipe.get()
        self.derniere_equipe_selectionnee = nouvelle_equipe
        self._charger_effectif_dans_widget(nouvelle_equipe)

    def _charger_effectif_dans_widget(self, nom_equipe):
        """remplit le widget de texte avec les joueurs déjà stockés"""
        self.txt_joueurs.delete("1.0", tk.END)
        joueurs = self.joueurs_par_equipe.get(nom_equipe, [])
        if joueurs:
            lignes = []
            for j in joueurs:
                if isinstance(j, (tuple, list)) and len(j) > 0:
                    lignes.append(str(j[0]))
                else:
                    lignes.append(str(j))
            self.txt_joueurs.insert(tk.END, "\n".join(lignes))
        else:
            self.txt_joueurs.insert(tk.END, f"Joueur 1\nJoueur 2")

    def _sauvegarder_effectif_local(self, equipe_cible=None, afficher_pop_up=False):
        """extraire le nom, le numéro et le poste de chaque joueur"""
        equipe_active = equipe_cible if equipe_cible else self.combo_choix_equipe.get()
        if not equipe_active:
            return
        contenu_brut = self.txt_joueurs.get("1.0", "end").strip()
        liste_joueurs_extraits = []
        for ligne in contenu_brut.split("\n"):
            if not ligne.strip():
                continue
            elements = [e.strip() for e in ligne.split("|") if e.strip()]
            if len(elements) == 3:
                nom_j, num_j, poste_j = elements
                liste_joueurs_extraits.append((nom_j, num_j, poste_j))
            else:
                nom_j = elements[0] if elements else "Joueur Anonyme"
                num_j = "99"
                poste_j = "Inconnu"
                liste_joueurs_extraits.append((nom_j, num_j, poste_j))

        self.joueurs_par_equipe[equipe_active] = liste_joueurs_extraits
        if afficher_pop_up:
            messagebox.showinfo(
                "Effectif enregistré",
                f"L'effectif de '{equipe_active}' ({len(liste_joueurs_extraits)} joueurs) a été mis en mémoire locale"
            )

    def _dessiner_etape_generation(self):
        """affiche le récapitulatif avant le calcul final du calendrier"""
        lbl_titre = ttk.Label(self.cadre_etape, text="Étape 4 : Validation du Calendrier",
                              font=("Helvetica", 12, "bold"))
        lbl_titre.pack(anchor="w", pady=10)
        lbl_recap = ttk.Label(
            self.cadre_etape,
            text=f"Résumé de la configuration :\n\n"
                 f"• Nom du Tournoi : {self.nom_tournoi_final}\n"
                 f"• Format : {self.format_final}\n"
                 f"• Nombre d'équipes validées : {len(self.equipes_creees)} clubs.\n\n"
                 f"Cliquez sur le bouton ci-dessous pour lancer\n"
                 f"la génération de calendrier des journées",
            font=("Helvetica", 10),
            justify="left"
        )
        lbl_recap.pack(anchor="w", pady=20)

    def _etape_suivante(self):
        """contrôle la validité des champs et incrémente l'étape"""
        if self.etape_actuelle == 0:
            nom_saisi = self.ent_nom_tournoi.get().strip()
            if not nom_saisi:
                messagebox.showwarning("Champ requis", "Le nom du tournoi ne peut pas être vide")
                return
            self.nom_tournoi_final = nom_saisi
            self.format_final = self.combo_format.get()
        elif self.etape_actuelle == 1:
            if len(self.equipes_creees) < 2:
                messagebox.showwarning("Équipes insuffisantes", "Il faut au moins 2 équipes pour créer un tournoi")
                return
        elif self.etape_actuelle == 2:
            if hasattr(self, 'derniere_equipe_selectionnee'):
                self._sauvegarder_effectif_local(equipe_cible=self.derniere_equipe_selectionnee, afficher_pop_up=False)
            total_joueurs = sum(len(liste) for liste in self.joueurs_par_equipe.values())
            messagebox.showinfo(
                "Effectifs enregistrés",
                f"Tous les effectifs ont été mis en mémoire avec succès !\n"
                f"Nombre total de joueurs enregistrés : {total_joueurs} joueurs."
            )
        elif self.etape_actuelle == 3:
            self._finaliser_et_generer_tournoi()
            return
        self.etape_actuelle += 1
        self._afficher_etape()

    def _etape_precedente(self):
        """recule d'une étape dans l'assistant"""
        if self.etape_actuelle == 2 and hasattr(self, 'derniere_equipe_selectionnee'):
            self._sauvegarder_effectif_local(equipe_cible=self.derniere_equipe_selectionnee, afficher_pop_up=False)
        if self.etape_actuelle > 0:
            self.etape_actuelle -= 1
            self._afficher_etape()

    def _finaliser_et_generer_tournoi(self):
        """instancie les classes, génère le calendrier et ferme l'assistant"""
        try:
            sport_defaut = "Football"
            matchs_initials = {}
            journee_depart = 1
            equipes_initiales = {}
            from models.Equipe import Equipe
            from models.Joueur import Joueur
            for nom_eq in self.equipes_creees:
                couleur_choisie = self.couleurs_par_equipe.get(nom_eq, "Bleu")
                nouvelle_eq = Equipe(nom=nom_eq, couleur=couleur_choisie)
                id_du_club = getattr(nouvelle_eq, "id", 0)
                liste_tuples_joueurs = self.joueurs_par_equipe.get(nom_eq, [])
                for nom_j, num_j, poste_j in liste_tuples_joueurs:
                    nouveau_j = Joueur(nom_j, num_j, poste_j, id_du_club)
                    nouvelle_eq.ajouter_joueur(nouveau_j)
                equipes_initiales[nouvelle_eq.id] = nouvelle_eq
            if self.format_final == "Championnat":
                from managers.Tournoi import ChampionnatTournoi
                nouveau_tournoi = ChampionnatTournoi(
                    self.nom_tournoi_final,
                    sport_defaut,
                    equipes_initiales,
                    journee_depart,
                    matchs_initials
                )
            else:
                from managers.Tournoi import CoupeTournoi
                nouveau_tournoi = CoupeTournoi(
                    self.nom_tournoi_final,
                    sport_defaut,
                    equipes_initiales,
                    journee_depart,
                    matchs_initials
                )

            if hasattr(nouveau_tournoi, "generer_calendrier"):
                nouveau_tournoi.generer_calendrier()
            self.parent.tournoi = nouveau_tournoi
            self.parent.chemin_sauvegarde_actif = None
            self.parent.notifier_changement_donnees()
            self.destroy()
            messagebox.showinfo("Succès", f"Le tournoi '{self.nom_tournoi_final}' a été généré avec succès !")

        except Exception as e:
            messagebox.showerror(
                "Erreur de génération",
                f"Impossible d'initialiser le tournoi.\nDétails : {str(e)}"
            )
