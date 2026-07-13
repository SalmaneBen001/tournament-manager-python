import tkinter as tk
from tkinter import ttk

class ClassementView(ttk.Frame):
    """l'affichage de l'onglet classement"""

    def __init__(self, parent, controleur):
        super().__init__(parent)
        self.controleur = controleur
        self._creer_vue_classement()

    def _creer_vue_classement(self):
        """création de vue Treeview"""
        self.colonnes_classement = (
            "Rang", "Equipe", "J", "V", "N", "D", "BP", "BC", "Diff", "Pts"
        )
        self.tree_classement = ttk.Treeview(
            self,
            columns=self.colonnes_classement,
            show="headings"
        )
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree_classement.yview
        )
        self.tree_classement.configure(yscrollcommand=scrollbar.set)
        self.scrollbar_classement = scrollbar
        self.scrollbar_classement.pack(side="right", fill="y")
        self.tree_classement.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        largeurs_colonnes = {
            "Rang": 50, "Equipe": 180, "J": 50, "V": 50, "N": 50,
            "D": 50, "BP": 60, "BC": 60, "Diff": 60, "Pts": 70
        }
        for col in self.colonnes_classement:
            self.tree_classement.heading(col, text=col, anchor="center")
            self.tree_classement.column(
                col,
                width=largeurs_colonnes[col],
                minwidth=largeurs_colonnes[col],
                anchor="center" if col != "Equipe" else "w"
            )
        self.cadre_tableau = ttk.Frame(self, padding=8)
        self.canvas_tableau = tk.Canvas(self.cadre_tableau, bg="#ffffff", height=300)
        self.canvas_tableau.pack(fill="both", expand=True)
        self.canvas_tableau.bind("<Configure>", lambda e: self._dessiner_tableau_coupe(self.controleur.tournoi) if getattr(self.controleur, 'tournoi', None) else None)

    def rafraichir(self):
        """Efface et remplit dynamiquement le Treeview avec les données métiers"""
        for item in self.tree_classement.get_children():
            self.tree_classement.delete(item)
        if not self.controleur.tournoi:
            return
        self.controleur.tournoi.mettre_a_jour_classement(generer_tour_suivant=False)
        tournoi = self.controleur.tournoi
        is_coupe = getattr(tournoi, "type", None) == "Coupe"
        if is_coupe:
            try:
                self.tree_classement.pack_forget()
            except Exception:
                pass
            try:
                self.scrollbar_classement.pack_forget()
            except Exception:
                pass
            if not self.cadre_tableau.winfo_ismapped():
                self.cadre_tableau.pack(fill="both", expand=True, padx=5, pady=5)
            try:
                self._dessiner_tableau_coupe(tournoi)
            except Exception as e:
                print(f"[ClassementView] Erreur dessin tableau coupe: {e}")
        else:
            try:
                self.cadre_tableau.pack_forget()
            except Exception:
                pass
            if not self.tree_classement.winfo_ismapped():
                self.tree_classement.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            if not getattr(self, 'scrollbar_classement', None) is None and not self.scrollbar_classement.winfo_ismapped():
                self.scrollbar_classement.pack(side="right", fill="y")
            equipes_triees = [{"equipe": equipe} for equipe in tournoi.get_classement()]
            for index, data in enumerate(equipes_triees, start=1):
                equipe = data["equipe"]
                diff_buts = equipe.buts_pour - equipe.buts_contre
                self.tree_classement.insert(
                    "",
                    "end",
                    values=(
                        index,
                        equipe.nom,
                        equipe.matchs_joues,
                        equipe.victoires,
                        equipe.nuls,
                        equipe.defaites,
                        equipe.buts_pour,
                        equipe.buts_contre,
                        diff_buts,
                        equipe.points
                    )
                )

    def _dessiner_tableau_coupe(self, tournoi):
        """Dessine un tableau simple (colonnes par tour) sur le canvas pour les coupes"""
        try:
            self.canvas_tableau.update_idletasks()
        except Exception:
            pass

        self.canvas_tableau.delete("all")
        matchs_raw = getattr(tournoi, "matchs", {}) if tournoi else {}
        if not matchs_raw:
            print("[ClassementView] Aucun match présent pour le tournoi")
            return
        matchs = {}
        for k, v in matchs_raw.items():
            try:
                ik = int(k)
            except Exception:
                ik = k
            matchs[ik] = v or []
        rounds = sorted(matchs.keys())
        n_rounds = len(rounds)
        width = max(self.canvas_tableau.winfo_width(), 800)
        height = max(self.canvas_tableau.winfo_height(), 300)
        col_w = width // max(1, n_rounds)
        final_round = max(rounds) if rounds else None
        left_pad = 20
        top_pad = 20

        centers = {}
        for r_i, r in enumerate(rounds):
            match_list = matchs.get(r, []) or []
            m_count = max(1, len(match_list))
            col_x = left_pad + r_i * col_w + col_w // 2
            centers[r] = []
            spacing = (height - 2 * top_pad) / m_count
            for m_i in range(m_count):
                y = top_pad + (m_i + 0.5) * spacing
                centers[r].append((col_x, int(y)))

        box_w = min(160, int(col_w * 0.7))
        box_h = 26
        
        for r_i, r in enumerate(rounds):
            match_list = matchs.get(r, []) or []
            col_x = centers[r][0][0] if centers[r] else left_pad + r_i * col_w + col_w // 2
            round_label = tournoi.obtenir_nom_tour(r) if hasattr(tournoi, "obtenir_nom_tour") else f"Tour {r}"
            self.canvas_tableau.create_text(
                (col_x, 8),
                text=round_label,
                font=("Helvetica", 9, "bold"),
                anchor="n"
            )
            
            for m_i, match in enumerate(match_list):
                if m_i >= len(centers[r]):
                    continue
                cx, cy = centers[r][m_i]
                x0 = cx - box_w // 2
                y0 = cy - box_h // 2
                x1 = cx + box_w // 2
                y1 = cy + box_h // 2
                
                home_name = match.equipe_dom.nom if match.equipe_dom else "—"
                away_name = match.equipe_ext.nom if match.equipe_ext else "Bye"

                self.canvas_tableau.create_rectangle(x0, y0, x1, y1, outline="#2d3748", fill="#f8fafc")

                if match.est_termine():
                    text = f"{home_name} {match.score_dom}-{match.score_ext} {away_name}"
                else:
                    text = f"{home_name} vs {away_name}"
                
                self.canvas_tableau.create_text((cx, cy), text=text, font=("Helvetica", 8), anchor="center")

        for r_i in range(len(rounds) - 1):
            r = rounds[r_i]
            r_next = rounds[r_i + 1]
            for m_i in range(len(matchs.get(r, []) or [])):
                if m_i >= len(centers[r]):
                    continue
                cx, cy = centers[r][m_i]
                target_idx = m_i // 2
                if target_idx < len(centers[r_next]):
                    tx, ty = centers[r_next][target_idx]
                    self.canvas_tableau.create_line(cx + box_w // 2, cy, tx - box_w // 2, ty, fill="#4a5568")

        final_match, _ = tournoi.obtenir_matchs_specials_coupe() if hasattr(tournoi, "obtenir_matchs_specials_coupe") else (None, None)
        if final_match and final_match.est_termine():
            if final_match.score_dom > final_match.score_ext:
                winner_name = final_match.equipe_dom.nom if final_match.equipe_dom else "—"
            elif final_match.score_ext > final_match.score_dom:
                winner_name = final_match.equipe_ext.nom if final_match.equipe_ext else "—"
            else:
                winner_name = None
            
            if winner_name:
                winner_y = height - 20
                self.canvas_tableau.create_text(
                    (width // 2, winner_y),
                    text=f"VAINQUEUR: {winner_name}",
                    font=("Helvetica", 12, "bold"),
                    anchor="center",
                    fill="#dc2626"
                )

    def _construire_classement_coupe(self, tournoi):
        """gestion du classement d'une coupe selon les éliminations"""
        infos = {}
        for equipe in tournoi.equipes.values():
            infos[equipe.id] = {
                "equipe": equipe,
                "phase": "Bye" if hasattr(tournoi, "equipes_exemptees") and equipe in tournoi.equipes_exemptees else "En lice",
                "matchs": equipe.matchs_joues,
                "victoires": equipe.victoires,
                "defaites": equipe.defaites,
                "elimine": False,
                "derniere_phase": None,
                "ordre": 0
            }

        for num_journee in sorted(getattr(tournoi, "matchs", {}).keys()):
            phase = tournoi.obtenir_nom_tour(num_journee) if hasattr(tournoi, "obtenir_nom_tour") else f"Tour {num_journee}"
            for match in tournoi.matchs.get(num_journee, []):
                if match.equipe_dom:
                    infos[match.equipe_dom.id]["matchs"] += 1
                if match.equipe_ext:
                    infos[match.equipe_ext.id]["matchs"] += 1

                if not match.est_termine():
                    continue

                if match.score_dom > match.score_ext:
                    gagnant = match.equipe_dom
                    perdant = match.equipe_ext
                elif match.score_ext > match.score_dom:
                    gagnant = match.equipe_ext
                    perdant = match.equipe_dom
                else:
                    gagnant = None
                    perdant = None

                if gagnant is not None:
                    infos[gagnant.id]["victoires"] += 1
                    infos[gagnant.id]["derniere_phase"] = phase
                    if infos[gagnant.id]["phase"] == "Bye":
                        infos[gagnant.id]["phase"] = phase
                    if infos[perdant.id]["phase"] != "Bye":
                        infos[perdant.id]["phase"] = f"Éliminé en {phase}"
                    infos[perdant.id]["defaites"] += 1
                    infos[perdant.id]["elimine"] = True

        dernier_tour = max(getattr(tournoi, "matchs", {}).keys(), default=0)
        final_termine = False
        if dernier_tour and tournoi.matchs.get(dernier_tour):
            final_termine = all(m.est_termine() for m in tournoi.matchs[dernier_tour])

        for info in infos.values():
            if not info["elimine"] and info["phase"] not in ("Bye", "En lice"):
                if final_termine and info["derniere_phase"] == "Finale":
                    info["phase"] = "Vainqueur"
                    info["ordre"] = 100
                else:
                    info["phase"] = info["derniere_phase"] or info["phase"]
                    info["ordre"] = 80
            elif info["phase"] == "Bye":
                info["ordre"] = 10
            elif info["phase"] == "En lice":
                info["ordre"] = 60
            elif info["phase"].startswith("Éliminé en "):
                phase_name = info["phase"].replace("Éliminé en ", "")
                stade_valeur = {
                    "Finale": 50,
                    "Demi-finale": 40,
                    "Quart de finale": 30,
                    "Huitième de finale": 20,
                    "Seizième de finale": 10,
                    "Trente-deuxième de finale": 5
                }.get(phase_name, 0)
                info["ordre"] = stade_valeur
            else:
                info["ordre"] = 0

            if info["ordre"] == 0:
                info["ordre"] = info["victoires"]

        return sorted(infos.values(), key=lambda item: (item["ordre"], item["victoires"], item["matchs"]), reverse=True)
