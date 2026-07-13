from pathlib import Path
from datetime import datetime
import json
import csv


class DataManager:
    """gestion du data"""

    def __init__(self):
        project_dir = Path(__file__).resolve().parent.parent
        self.chemin_json = project_dir / "data"
        self.chemin_csv = project_dir / "exports"

    def _assurer_dossier_existe(self, repertoire):
        """crée le dossier cible si nécessaire avant d'écrire des fichiers"""
        repertoire.mkdir(parents=True, exist_ok=True)

    def sauvegarder_json(self, nom_fichier, donnees_dict):
        """sauvegarde du dictionnaire de données dans un fichier json"""
        fichier_cible = self.chemin_json / nom_fichier
        try:
            self._assurer_dossier_existe(self.chemin_json)
            with open(fichier_cible, "w", encoding="utf-8") as f:
                json.dump(donnees_dict, f, indent=4, ensure_ascii=False)
            print(f"Données sauvegardées avec succès dans : {fichier_cible}")
            return True
        except PermissionError:
            print(
                f"Erreur d'accès : Impossible d'écrire dans '{nom_fichier}'. Le fichier est peut-être verrouillé ou ouvert ailleurs")
            return False
        except (IOError, OSError) as e:
            print(f"Erreur matérielle ou système lors de l'enregistrement de '{nom_fichier}' : {e}")
            return False
        except Exception as e:
            print(f"Erreur imprévue lors de la sauvegarde : {e}")
            return False

    def charger_json(self, nom_fichier, chemin_complet=None):
        """chargement du fichier json depuis data/ ou depuis un chemin absolu"""
        if chemin_complet is not None:
            fichier_cible = Path(chemin_complet)
            libelle_erreur = str(fichier_cible)
        else:
            fichier_cible = self.chemin_json / nom_fichier
            libelle_erreur = nom_fichier
        try:
            with open(fichier_cible, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erreur : Le fichier '{libelle_erreur}' est introuvable")
            return None
        except json.JSONDecodeError as jde:
            print(
                f"Erreur : Le fichier '{libelle_erreur}' est corrompu ou n'est pas au format JSON valide. Détails : {jde}")
            return None
        except PermissionError:
            print(f"Erreur d'accès : Droits insuffisants pour lire le fichier '{libelle_erreur}'")
            return None
        except Exception as e:
            print(f"Erreur imprévue lors du chargement : {e}")
            return None

    def exporter_csv(self, liste_joueurs, equipes_triees, liste_matchs, numero_journee):
        """export des données en format csv"""
        self._assurer_dossier_existe(self.chemin_csv)
        # statistiques des joueurs :
        try:
            fichier_stats = self.chemin_csv / "statistiques_joueurs.csv"
            colonnes = ["Nom", "Buts", "Passes", "Cartons jaunes", "Cartons rouges"]
            with open(fichier_stats, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=colonnes, delimiter=";", extrasaction="ignore")
                writer.writeheader()
                writer.writerows(liste_joueurs)
        except (IOError, PermissionError) as e:
            print(f"Erreur lors de l'export des statistiques joueurs : {e}")
        except Exception as e:
            print(f"Erreur imprévue (statistiques joueurs) : {e}")
        # classement :
        try:
            fichier_classement = self.chemin_csv / "classement.csv"
            data = [
                {
                    "Position": pos,
                    "Équipe": eq.nom,
                    "Points": eq.points,
                    "Buts Pour": eq.buts_pour,
                    "Buts Contre": eq.buts_contre,
                    "Différence": eq.buts_pour - eq.buts_contre,
                }
                for pos, eq in enumerate(equipes_triees, start=1)
            ]
            if data:
                with open(fichier_classement, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter=";")
                    writer.writeheader()
                    writer.writerows(data)
        except AttributeError as ae:
            print(f"Erreur : Un objet Équipe possède des attributs invalides : {ae}")
        except (IOError, PermissionError) as e:
            print(f"Erreur lors de l'export du classement : {e}")
        except Exception as e:
            print(f"Erreur imprévue (classement) : {e}")
        # résultats de journée :
        try:
            fichier_resultats_journee = self.chemin_csv / f"resultats_journee_{numero_journee}.csv"
            resultats_journee = []
            for match in liste_matchs:
                score_dom = match.score_dom if match.est_termine() else "-"
                score_ext = match.score_ext if match.est_termine() else "-"
                resultats_journee.append({
                    "Journée": numero_journee,
                    "Équipe domicile": match.equipe_dom.nom,
                    "Score dom": score_dom,
                    "Score ext": score_ext,
                    "Équipe extérieure": match.equipe_ext.nom,
                    "Statut": match.statut
                })
            if resultats_journee:
                with open(fichier_resultats_journee, "w", encoding="utf-8-sig", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=resultats_journee[0].keys(), delimiter=";")
                    writer.writeheader()
                    writer.writerows(resultats_journee)
            else:
                print(f"Aucun match trouvé pour la journée {numero_journee}")
        except (IOError, PermissionError) as e:
            print(f"Erreur lors de l'export des résultats de la journée {numero_journee} : {e}")
        except Exception as e:
            print(f"Erreur imprévue (résultats journée) : {e}")

    def rapport_journee_txt(self, liste_matchs, numero_journee):
        """export du rapport d'une journée spécifique en format txt"""
        if not liste_matchs:
            print(f"Aucun match trouvé pour la journée {numero_journee}")
            return False

        fichier_txt = self.chemin_csv / f"rapport_journee_{numero_journee}.txt"
        try:
            self._assurer_dossier_existe(self.chemin_csv)
            with open(fichier_txt, "w", encoding="utf-8") as f:
                # En-tête principal du rapport
                f.write("=========================================================\n")
                f.write(f"           RAPPORT DE LA JOURNÉE {numero_journee}           \n")
                f.write("=========================================================\n\n")
                total_buts_j = 0
                total_jaunes_j = 0
                total_rouges_j = 0
                matchs_joues_j = 0

                f.write("╔═══════════════════════════════════════════════════════╗\n")
                f.write("║                 RÉSULTATS DES MATCHS                  ║\n")
                f.write("╚═══════════════════════════════════════════════════════╝\n\n")

                for index, match in enumerate(liste_matchs, start=1):
                    f.write(f"MATCH #{index} : ")
                    if match.est_termine():
                        matchs_joues_j += 1
                        total_buts_j += (match.score_dom + match.score_ext)
                        f.write(
                            f"{match.equipe_dom.nom}  {match.score_dom} - {match.score_ext}  {match.equipe_ext.nom}\n")
                        f.write(f"   Statut : Terminé\n")

                        buteurs = match.buteurs
                        if buteurs:
                            f.write("   [Buts] ➔ ")
                            buteurs_textes = [f"{j.nom if hasattr(j, 'nom') else str(j)} ({nb}x)" for j, nb in
                                              buteurs.items()]
                            f.write(", ".join(buteurs_textes) + "\n")
                        else:
                            if (match.score_dom + match.score_ext) > 0:
                                f.write("   [Buts] ➔ Score validé (détails buteurs non saisis)\n")
                            else:
                                f.write("   [Buts] ➔ Aucun but inscrit\n")

                        passeurs = match.passeurs
                        if passeurs:
                            f.write("   [Passes] ➔ ")
                            passeurs_textes = [f"{j.nom if hasattr(j, 'nom') else str(j)} ({nb}x)" for j, nb in
                                               passeurs.items()]
                            f.write(", ".join(passeurs_textes) + "\n")

                        cartons = match.cartons
                        if isinstance(cartons, dict):
                            jaunes = cartons.get("jaunes", {})
                            rouges = cartons.get("rouges", {})
                            if jaunes:
                                total_jaunes_j += sum(jaunes.values())
                                f.write("   [🟨 Jaunes] ➔ ")
                                jaunes_textes = [f"{j.nom if hasattr(j, 'nom') else str(j)}" for j in jaunes.keys()]
                                f.write(", ".join(jaunes_textes) + "\n")
                            if rouges:
                                total_rouges_j += sum(rouges.values())
                                f.write("   [🟥 Rouges] ➔ ")
                                rouges_textes = [f"{j.nom if hasattr(j, 'nom') else str(j)}" for j in rouges.keys()]
                                f.write(", ".join(rouges_textes) + "\n")
                    else:
                        f.write(f"{match.equipe_dom.nom}  VS  {match.equipe_ext.nom}\n")
                        f.write(f"   Statut : À venir / Non joué\n")

                    f.write("   " + "-" * 49 + "\n\n")

                f.write("╔═══════════════════════════════════════════════════════╗\n")
                f.write("║             BILAN STATISTIQUE DE LA JOURNÉE           ║\n")
                f.write("╚═══════════════════════════════════════════════════════╝\n")
                f.write(f"  • Matchs disputés          : {matchs_joues_j} / {len(liste_matchs)}\n")
                f.write(f"  • Total de buts inscrits   : {total_buts_j} buts")
                if matchs_joues_j > 0:
                    f.write(f" (Moyenne : {total_buts_j / matchs_joues_j:.2f} buts / match)\n")
                else:
                    f.write("\n")
                f.write(f"  • Cartons jaunes distribués : {total_jaunes_j}\n")
                f.write(f"  • Cartons rouges distribués : {total_rouges_j}\n")
                f.write("=========================================================\n")
                date_aujourdhui = datetime.now().strftime("%d/%m/%Y")
                f.write(
                    f"Généré automatiquement par le système le {date_aujourdhui}\n"
                )
            return True
        except (IOError, PermissionError) as e:
            print(f"Erreur d'écriture du fichier TXT : {e}")
            return False
