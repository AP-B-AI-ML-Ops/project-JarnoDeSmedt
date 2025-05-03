# Project MLops Jarno De Smedt
https://apwt.gitbook.io/ba-tiai-ml-ops/projects/project-1

## problem that is being solved with this ML application
~~`well described project and clear what project solves`~~

~~Explain which datasets you will use, how you will get training, validation and test data, and how you will get new data to use your service.~~

~~What does your service actually do?~~
~~Explain what your project will do/predict. What kind of application are you making? What is the goal of this project?~~

## train model on the dataset and track the experiments (with mlflow)
~~`both tracking and registry are used`~~

## create model training pipeline (orchestration with Prefect)
``workflow orchestration: fully worked out and deployed workflow`
...TODO: enkel nog Prefect runnen, tasks en flows zijn wel al klaargemaakt

## deploy model as a web-service
`The model deployment code is containerized and could be deployed to cloud`
...TODO: basic webapp staat al klaar

## monitor performance of the model (evidently, grafana)
`Comprehensive model monitoring that sends alerts or runs a conditional workflow (e.g. retraining, switching to a different model, ...) if the defined metrics threshold is violated`

## reproducability in README.md
`Instructions are clear, it's easy to run the code, and it works. The versions for all the dependencies are specified.`

## follow best practises
- unit tests
- coding guidelines
- use pre-commit hooks
> The pre-commit hook is run first, before you even type in a commit message. It's used to inspect the snapshot that's about to be committed, to see if you've forgotten something, to make sure tests run, or to examine whatever you need to inspect in the code.

- peer evaluation!

--------------------------------------------------------------

## Dataset(s)

[](https://www.kaggle.com/datasets/jayaantanaath/student-habits-vs-academic-performance)

**size**: 73.66 kB, 1000 lijnen
**algoritme**: logistic regression, nb, descision trees, ...

https://www.kaggle.com/datasets/ethancratchley/email-phishing-dataset

**size**: 11.81 MB, 525000 lijnen
**algoritme**: logistic regression, nb, descision trees, ...


https://www.kaggle.com/datasets/bhupendram/carprices

**size**: 88.05 MB, 550298 lijnen
**algoritme**: lineair regression

Omdat ik zeer geinteresseerd ben in auto's sprak deze dataset me aan. 

De dataset zal worden opgesplitst in een training- en testset, verder kan er ook getest worden door manuele input volgens wat er op 2ehands te vinden is.

Nieuwe data om te hertrainen in de toekomst kan eventueel bekomen worden door scraping van 2ehands sites of manuele input


## Project Explanation

Aan de hand van een aantal belangrijke kerngegevens van een auto zal het machine learning algoritme een gerichte prijs adviseren op basis van de trainingsdata. De service wordt via een webapplicatie ter beschikking gesteld aan het publiek. 

Deze geschatte prijs kan de verkoper gebruiken bij het bepalen van de vraagprijs of een potentiele koper gebruiken om te weten of het een realistische prijs is. Zo weet je als consument of je niet teveel zal betalen. 


## Flows & Actions
Which flows & actions will you need to work out?

Work out which flows and actions you will need, for your project to complete successfully.


Er moeten een aantal stappen worden doorlopen zoals:
~~- data exploratie~~ 
~~- eventueel data cleaning~~
~~- opzetten van een development omgeving met een devcontainer~~
~~- ml algoritme implementeren~~
~~- ml experiments tracken ~~
- orchestreren met prefect 
- unit tests
- pre-commit hooks
- readme docs how to run
- flask webapp
- visualiseren met grafana en tresholds + triggers/alerts implementeren