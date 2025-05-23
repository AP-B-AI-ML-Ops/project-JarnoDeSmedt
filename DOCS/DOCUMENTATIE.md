<mark>
For instructions on how to run and set up the project, please check the README.md. This is rather documentation about the project for myself.
</mark>

# devcontainer

`.devcontainer` folder toevoegen met daarin `devcontainer.json` file erin:
````
// python slim base image
{
  "name": "mlops-project-jarno",
  "image": "python:3.10-slim",

  // post create command voor het installeren van GIT in de devcontainer want hierin zit geen git, enkel op mijn lokale machine. Het kan zijn dat git bij in de image zit maar omdat het gaat om de slim variant is het de meest basic versie zonder extra dingen.

  "postCreateCommand": "apt-get update && apt-get install -y git && pip install --no-cache-dir -r requirements.txt",
  "extensions": [
    "ms-python.python",
    "ms-vscode.remote-repositories" // enkele custom extentions
  ],
  "forwardPorts": [5000], // poorten forwarden die je nodig hebt
  "settings": {
    "python.formatting.provider": "black"
  }
}

````
more info: https://xebia.com/blog/how-to-create-a-devcontainer-for-your-python-project/

# git

via postcreate command in devcontainer.json wordt git geinstalleerd in de container zelf, je kan niet verwijzen naar de installatie op de windows machine omdat er vanuit de container zelf connectie wordt gemaakt. de standaard python:slim image bevat geen standaard git installatie

in de docker workspace terminal:
````
git config --global user.email "jarno.desmedt@live.be"
git config --global user.name "Jarno De Smedt"
````
om te kunnen committen vanuit de terminal of vscode extention

# tracking URI uitleg

## What Do These URIs Actually Mean?

sqlite:///mlflow.db vs http://localhost:5001

### 🔹 `sqlite:///mlflow.db`
This refers to a **local SQLite database file** and is used as a **backend store** for MLflow — *by the MLflow server*, not your training script.

> **This URI is set in your `mlflow` Docker service.**
> It's not for clients like `train_streamlined.py`, but for configuring how MLflow stores run metadata.

Example in `docker-compose.yml`:
```yaml
mlflow:
  command: mlflow server \
           --backend-store-uri sqlite:///mlflow.db \
           --default-artifact-root /mlflow/mlruns \
           --host 0.0.0.0
```

🧠 It tells **MLflow server**:
> "Store metadata (runs, experiments, etc.) in a local SQLite file."

---

### 🔹 `http://localhost:5001`
This is the **tracking URI for clients** (like your training script).
It tells the script:
> “Send all tracking data to the MLflow server running on `localhost:5001`.”

So in your Python code:
```python
mlflow.set_tracking_uri("http://localhost:5001")
```

Means:
> “Connect to the MLflow server on that address and log the run there.”

---

## ✅ Summary of Roles

| URI                            | Used Where             | Purpose                                      |
|--------------------------------|------------------------|----------------------------------------------|
| `sqlite:///mlflow.db`         | In `mlflow` container  | Backend storage (metadata DB)                |
| `http://localhost:5001`       | In training scripts    | Client → Server communication for tracking   |

---

## 🚫 When *Not* to Use `sqlite:///mlflow.db` in Code

- If you set this **in your script**, it will attempt to use a **local file DB** (in your dev container or host), and **bypass** your running MLflow server.
- You'll end up with **two separate tracking stores** and a very confusing UI experience.

---

## ✅ TL;DR

- Use `mlflow.set_tracking_uri("http://localhost:5001")` in your Python code.
- Use `sqlite:///mlflow.db` in Docker Compose (for the MLflow service backend).
- Never use `sqlite:///mlflow.db` in your script unless you're running MLflow in-process and locally (not via the server).


# prefect

> Veel problemen gehad bij het installeren en configureren van prefect, grotendeels door versies die niet compatieble waren. Uiteindelijk werkt het door de docker compose file juist te zetten met zelfde versies als in de requirements.txt.

Wanneer de devcontainer wordt opgestart, zal prefect ook beschikbaar zijn op http://localhost:4200/dashboard

![dashboard](image-8.png)

Als de prefect.yaml, zoompool nog niet bestaat of de pipeline flow nog niet is geregistreerd op prefect:

````
prefect init -> kies local in het keuzemenu
prefect worker start --pool "zoompool"
prefect deploy train_and_register_model.py:training_pipeline -n cars1 -p zoompool
````

LET OP!: wanneer je manueel uitvoert (dus niet met docker-compose) vergeet dan de PREFECT_API_URL niet te zetten. Maar is in docker-compose.yaml gezet dus dit zou normaal in orde moeten zijn.
Als dit toch moet gebeuren kan dit met:

````
export PREFECT_API_URL=http://prefect:4200/api
prefect config set PREFECT_API_URL=$PREFECT_API_URL
````

Wanneer je nu het script uitvoert lokaal of via de prefect UI zie je de details:

![prefect run details](image-7.png)

runnen vanuit de Prefect UI, klik op `Flows` > `main-flow` > `Deployments` > `cars1` en dan op `Quick run` via de 3 dots rechts

LET OP!: worker "zoompool" moet runnen!

> Ik heb nu ook een prefect folder met eigen dockerfile toegevoegd omdat ik errors kreeg als ik een flow wou runnen via de Prefect UI, de agent-python omgeving had geen MLflow,... geinstalleerd en kon daarom het script niet runnen. We voegen de requirements.txt toe aan de prefect python omgeving. Zo kan je nu dus de flow runnen vanuit de UI via de agent alsook vanuit de train-dev python omgeving.

# flask app

````python
    #when using a stage, use models:/<model_name>/<stage> Just make sure MODEL_STAGE is exactly one of:
    # "None" (literally this string, if you don't want to use a stage)
    # "Production"
    # "Staging"
    # "Archived"
    #model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/{MODEL_STAGE}")

    #When using a version number, use model_uri parameter models:/<model_name>/<version_number>
    print(f"Loading model from: models:/{MODEL_NAME}/versions/1")
    model = mlflow.pyfunc.load_model(model_uri="models:/car-price-model/1")
    print("✅ Model loaded successfully!")

    # or with alias if you have set it in the MLflow UI
    #print(f"Loading model from: models:/{MODEL_NAME}/champion")
    #model = mlflow.pyfunc.load_model(f"models:/{MODEL_NAME}/champion")
````

To run the app locally, use the command: python app.py (maar is niet nodig via docker compose want runt al vanzelf)

Send a request like this to /predict (http://localhost:5000/predict):
````json
{
  "features": [2016, 120000, 1.6, 5]
}
````
=> werkt nog niet helemaal want de make column wordt geencodeerd in de model training, en geeft errors in het infer schema.

Hierdoor dus een volledige json nodig met alle makes, zoals hieronder:
````json
{
  "features": [
    {
      "year": 2016,
      "condition": 1,
      "odometer": 120000,
      "mmr": 5000,
      "make_acura": false,
      "make_airstream": false,
      "make_aston martin": false,
      "make_audi": false,
      "make_bentley": false,
      "make_bmw": false,
      "make_buick": false,
      "make_cadillac": false,
      "make_chevrolet": false,
      "make_chrysler": false,
      "make_daewoo": false,
      "make_dodge": false,
      "make_dot": false,
      "make_ferrari": false,
      "make_fiat": false,
      "make_fisker": false,
      "make_ford": false,
      "make_geo": false,
      "make_gmc": false,
      "make_honda": false,
      "make_hummer": false,
      "make_hyundai": false,
      "make_infiniti": false,
      "make_isuzu": false,
      "make_jaguar": false,
      "make_jeep": false,
      "make_kia": false,
      "make_lamborghini": false,
      "make_landrover": false,
      "make_lexus": false,
      "make_lincoln": false,
      "make_lotus": false,
      "make_maserati": false,
      "make_mazda": false,
      "make_mercedes": false,
      "make_mercury": false,
      "make_mini": false,
      "make_mitsubishi": false,
      "make_nissan": false,
      "make_oldsmobile": false,
      "make_plymouth": false,
      "make_pontiac": false,
      "make_porsche": false,
      "make_ram": false,
      "make_rolls-royce": false,
      "make_saab": false,
      "make_saturn": false,
      "make_scion": false,
      "make_smart": false,
      "make_subaru": false,
      "make_suzuki": false,
      "make_tesla": false,
      "make_toyota": false,
      "make_volkswagen": false,
      "make_volvo": true
    }
  ]
}
````

![prediction post request](image.png)

# testing

voer `pytest` uit in de terminal van de root directory van het project (workspace)
`pytest -p no:warnings`

MLflow schema warning:
It’s warning about possible issues if your model receives missing values in integer columns. Not critical, but good to be aware of — you can leave this for now unless you’re deploying this to production.

![unit test results](image-1.png)

# pre-commits
1) add the following to requirements.txt and install it:
````
pre-commit==4.2.0
black==25.1.0
````
2) create a .pre-commit-config.yaml file
````yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-added-large-files

````
3) installeer de hook
`pre-commit install`

nu worden de pre-commit hooks telkens uitgevoerd bij het committen

LET OP: telkens je een aanpassing doet in de pre-commit.yaml file moet je opnieuw installeren met `pre-commit install`

optioneel: Run hooks manueel voor staging om te kijken wat er veranderd voor de commit:

`pre-commit run --all-files`

FIX warning ivm setlocale: mag genegeerd worden, maar `export LC_ALL=C.UTF-8` in terminal om het te stoppen

![uitvoeren git commit -m "..."](image-3.png)

je merkt dat pre-commit hooks dingen hebben aangepast en je nu dus opnieuw de wijzigingen moet stagen en committen.

bijvoorbeeld hier zie je in de working tree dat isort een aantal dingen heeft gewijzigd in de imports
![isort working tree results](image-4.png)

als je dan opnieuw add en commit zie je:

![passed pre-commit hooks](image-5.png)

of bijvoorbeeld uitvoeren van `pre-commit run pylint --all-files`

![output pylint](image-9.png)

stel er lukt iets niet en je wil committen zonder precommit checks: `git commit -m "opkuisen en verder uitwerken" --no-verify` (not recommended)

# evidently AI
Er zal door een task in de prefect workflow een html file worden gecreerd in de reports folder. De HTML file kan je openen in een webbrowser om te kijken of er datadrift optreedt in de nieuwe data.
