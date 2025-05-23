0) zorg ervoor dat Docker draait. Op windows: open Docker Desktop
1) open folder in VS code via een terminal met met `code .`
2) ctrl + shift + p -> 'rebuild and reopen in container'
je zal merken dat de containers worden gecreeerd en de devcontainer wordt geopend in vscode
3) nu kan je een terminal openen, zorg dat je in de workspace directory zit (normaal wordt deze standaard geopend) en dat je 'root@92383d3fe9ce:/workspace#' ziet.
Daarin kan je `python train_and_register_model.py` uitvoeren, het model wordt hiermee getraind en gelogd in MLflow.
