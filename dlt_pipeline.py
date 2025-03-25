import os
import dlt
from dlt.sources.helpers.rest_client import RESTClient
from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator
from datetime import datetime
from google.cloud import storage
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    '/C:/Users/User/Downloads/service-account-key.json'
)

client = storage.Client(credentials=credentials)


GCS_BUCKET='chicago_bucket'

print("Script is running...")

# ----------------------------
# Resource for artist details
# ----------------------------
@dlt.resource(name="artists_details")
def artist_retrieval():
    client = RESTClient(
        base_url="https://api.artic.edu/api",
        paginator=PageNumberPaginator(
            base_page=1,
            total_path="$.pagination.total_pages",
            maximum_page=10  # Adjust as needed
        )
    )
    for page in client.paginate("v1/artists?page"):
        yield page

# -----------------------------
# Resource for artworks details
# -----------------------------
@dlt.resource(name="artworks_details")
def artwork_retrieval():
    client = RESTClient(
        base_url="https://api.artic.edu/api",
        paginator=PageNumberPaginator(
            base_page=1,
            total_path="$.pagination.total_pages",
            maximum_page=10  # Adjust as needed
        )
    )
    for page in client.paginate("v1/artworks?page"):
        yield page

# ----------------------------
# Function to upload files to GCS with partitioning
# ----------------------------
def upload_to_gcs(local_folder, partition=""):
    """
    Upload all parquet files from the local folder to a GCS bucket.
    Files are uploaded under a folder structure: raw_data/<partition>/date=<RUN_DATE>/<filename>  """
    

    # Get the bucket name from the environment variable (or use a default)
    bucket_name = os.getenv("GCS_BUCKET", "your-default-bucket")
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Use current date as partition date (or override with RUN_DATE env variable)
    run_date = os.getenv("RUN_DATE", datetime.today().strftime("%Y-%m-%d"))

    for root, dirs, files in os.walk(local_folder):
        for file in files:
            if file.endswith(".parquet"):
                local_path = os.path.join(root, file)
                # Create a destination path: e.g., raw_data/artists/date=2025-03-24/<file>
                blob_path = f"{partition}/date={run_date}/{file}"
                full_blob_path = f"raw_data/{blob_path}"
                blob = bucket.blob(full_blob_path)
                blob.upload_from_filename(local_path)
                print(f"Uploaded {local_path} to gs://{bucket_name}/{full_blob_path}")

# ----------------------------
# Main pipeline function
# ----------------------------
def pipeline_main():
    # Create a pipeline that writes data to the local filesystem as Parquet files
    pipeline = dlt.pipeline(
        pipeline_name='gcs_pipeline',
        destination='filesystem',
        dataset_name='raw_data'
    )

    # Run the artists resource (this should create files in a folder typically named 'arts_details')
    load_info_artists = pipeline.run(
        artist_retrieval, 
        loader_file_format="parquet", 
        write_disposition="replace"
    )

    # Run the artworks resource (files in 'artworks_details')
    load_info_artworks = pipeline.run(
        artwork_retrieval, 
        loader_file_format="parquet", 
        write_disposition="replace"
    )

    print("Artists data loaded:")
    print(load_info_artists)
    print("Artworks data loaded:")
    print(load_info_artworks)

    # Get the base local folder where DLT writes files
    local_output_path = pipeline.pipeline_filesystem_path
    print("Local pipeline output path:", local_output_path)

    # Define subfolders for each resource (adjust if needed based on your actual structure)
    local_artists_path = os.path.join(local_output_path, "arts_details")
    local_artworks_path = os.path.join(local_output_path, "artworks_details")

    # Upload each resource's files to GCS in separate partition folders
    print("Uploading artists data from:", local_artists_path)
    upload_to_gcs(local_artists_path, partition="artists")
    print("Uploading artworks data from:", local_artworks_path)
    upload_to_gcs(local_artworks_path, partition="artworks")
    print("Upload to GCS complete!")

# ----------------------------
# Run the pipeline when executing directly
# ----------------------------
if __name__ == "__main__":
    pipeline_main()