def pipeline_main():
    import dlt
    from dlt.sources.helpers.rest_client import RESTClient
    from dlt.sources.helpers.rest_client.paginators import PageNumberPaginator

    @dlt.resource(name="arts_details")
    def artist_retrieval():
        client = RESTClient(
            base_url="https://api.artic.edu/api",
            paginator=PageNumberPaginator(
                base_page=1,
                total_path="$.pagination.total_pages",
                maximum_page=10
            )
        )
        for page in client.paginate("v1/artists?page"):
            yield page

    pipeline = dlt.pipeline(
        pipeline_name='pg_pipeline',
        destination='postgres',
        dataset_name='chicago_arts_dataset'
    )

    load_info = pipeline.run(artist_retrieval, write_disposition="replace")

    print("Pipeline loaded data to Postgres!")
    print(load_info)

# Optional: test locally
if __name__ == "__main__":
    pipeline_main()
