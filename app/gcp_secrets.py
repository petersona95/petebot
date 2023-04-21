# Import the Secret Manager client library.
from google.cloud import secretmanager

def get_secret_contents(secretName):
    # GCP project in which to store secrets in Secret Manager.
    project_id = "885066695413"

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the parent name from the project.
    resource_name = f"projects/{project_id}/secrets/{secretName}/versions/latest"

    # Access the secret version.
    response = client.access_secret_version(request={"name": resource_name})

    # Print the secret payload.
    #
    # WARNING: Do not print the secret in a production environment - this
    # snippet is showing how to access the secret material.
    payload = response.payload.data.decode("UTF-8")
    return payload