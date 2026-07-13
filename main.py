from managers.DataManager import DataManager
from managers.StatistiquesManager import StatistiquesManager
from views.TournoiApp import TournoiApp

def main() -> None:
    print("[Système] Initialisation des briques logiques métiers...")
    data_manager = DataManager()
    stats_manager = StatistiquesManager(None)
    print("[Système] Lancement de l'interface graphique...")
    app = TournoiApp(
        tournoi=None,
        stats_manager=stats_manager,
        data_manager=data_manager,
    )
    app.demarrer()

if __name__ == "__main__":
    main()