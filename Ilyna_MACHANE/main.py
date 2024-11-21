from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
import os

# Initialize credentials
credential = "V...." 
account_name = "cinearchiveilm"  # Add your storage account name here
account_url = f"https://{account_name}.blob.core.windows.net"
blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)

# Define containers
raw_container = "raw-images-ilm"  # Update xyz
final_container = "edited-images-ilm"  # Update xyz


def create_container(container_name: str):
    """
    Creates a container if it does not exist.
    """
    try:
        container_client = blob_service_client.get_container_client(container_name)
        container_client.create_container()
        print(f"Container '{container_name}' created.")
    except Exception as e:
        print(f"Container '{container_name}' already exists or an error occurred: {e}")


def upload_file(container_name: str, blob_name: str, file_path: str):
    """
    Uploads a file to the specified container. Complete this function.
    """
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)
        print(f"File '{file_path}' uploaded to container '{container_name}' as '{blob_name}'.")
    except Exception as e:
        print(f"Error uploading file: {e}")


def download_file(container_name: str, blob_name: str, download_path: str):
    """
    Downloads a file from the specified container. Complete this function.
    """
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        print(f"Blob '{blob_name}' downloaded to '{download_path}'.")
    except Exception as e:
        print(f"Error downloading file: {e}")


def copy_blob(source_container: str, source_blob: str, dest_container: str, dest_blob: str):
    """
    Copies a blob from one container to another. Complete this function.
    """
    try:
        source_blob_client = blob_service_client.get_blob_client(container=source_container, blob=source_blob)
        destination_blob_client = blob_service_client.get_blob_client(container=dest_container, blob=dest_blob)
        copy_source = source_blob_client.url
        destination_blob_client.start_copy_from_url(copy_source)
        print(f"Blob '{source_blob}' copied from '{source_container}' to '{dest_container}' as '{dest_blob}'.")
    except Exception as e:
        print(f"Error copying blob: {e}")


def delete_containers(containers: list[str]):
    """Deletes containers from a given list of container names."""
    try:
        for container_name in containers:
            container_client = blob_service_client.get_container_client(container_name)
            container_client.delete_container()
        print(f"Containers {containers} deleted.")
    except Exception as e:
        print(f"An error occurred while deleting containers: {e}")


# DO NOT EDIT THE ORDER OF FUNCTIONS WHEN SUBMITTING YOUR ASSIGNMENT
# ONLY UPDATE THE VIDEO INPUT NAME FOR YOUR TESTS.
# Example usage of the functions
def main():
    # Step 1: Create containers if they don't exist
    create_container(raw_container)
    create_container(final_container)


    # Step 2: Upload a file to raw footage container
    upload_file(raw_container, "footage.mp4", r"C:\Users\ilyna\OneDrive\Bureau\cloud\footage.mp4")

    # Step +
    upload_file(final_container, "finalcut.mp4", r"C:\Users\ilyna\OneDrive\Bureau\cloud\footage.mp4")

    # Step 3: Download a file from final edits container
    download_file(final_container, "finalcut.mp4", r"C:\Users\ilyna\OneDrive\Bureau\cloud\finalcut.mp4")

    # Step 4: Copy a file from raw footage to final edits
    copy_blob(raw_container, "footage.mp4", final_container, "editedfootage.mp4")

    # Step 5: Delete the containers
    delete_containers([raw_container, final_container])



if __name__ == "__main__":
    main()

 
