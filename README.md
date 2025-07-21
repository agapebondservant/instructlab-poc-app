# Sample Generative / Agentic AI App

<img src="images/video.png" width="50%">


To run the app locally:
  1. Create an .env file with necessary environment variables for the app - use `.env-template` as a base template
  2. Set up a virtual environment: `python3 -m venv venv` (tested with python 3.11, 3.12)
  3. Install Rust: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
  4. Install dependencies: `pip install -r requirements.txt`
  5. Start the app: `python3 -m streamlit run app.py`
  
To run the app on Openshift:
  1. Create an .env file with necessary environment variables for the app - use `.env-template` as a base template
  2. Run the following script:

  ```
  APP_NAME=<fill in the name of your app>
  oc new-build --binary --strategy=docker --name $APP_NAME
  oc start-build $APP_NAME --from-dir . --follow
  oc new-app -i $APP_NAME:latest --env-file .env
  oc expose deploy $APP_NAME --port 8501
  oc expose svc $APP_NAME
  ```
  3. The app should be accessible at the FQDN below:
  
  ```
  echo http://$(oc get route -o json | jq -r '.items[0].spec.host')
  ```
  4. Troubleshooting:
  
  ```
  oc logs $(oc get pod -o name -l deployment=$APP_NAME)
  ```

For demonstrations:
1. Should support any type of logfile. For demonstration purposes, try to stick to smaller files; 
see the sample_logs directory for a good sample set.

OTHER NOTES:
* Tested with python 3.11, 3.12
