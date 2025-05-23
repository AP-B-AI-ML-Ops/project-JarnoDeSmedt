#Zou de het probleem moeten oplossen dat de agent onmiddellijk stopt, wel nog toevoegen aan postcreate command. Getest maar werkte niet
#!/bin/bash

# Wait until Prefect UI is reachable
until curl -s http://localhost:4200 > /dev/null; do
  echo "Waiting for Prefect server..."
  sleep 3
done

# Now start the agent
prefect worker start --pool zoompool
