{{
    config(
        materialized='table'
    )
}}

with

    source as (select * from {{ source("staging", "vaccination_data_raw") }}),

    renamed as (

        select
            location,
            iso_code,
        FORMAT_DATE('%d-%m-%y', DATE(`date`)) AS vaccination_date,  -- Date formatted as DD-MM-YY
        extract (day from DATE(`date`)) AS day , -- Extract the day
        EXTRACT(QUARTER FROM DATE(`date`)) AS quarter,  -- Extract the quarter
        EXTRACT(YEAR FROM DATE(`date`)) AS year,  -- Extract the year
            {{ fill_nulls("total_vaccinations", "float") }},
            {{ fill_nulls("people_vaccinated", "bigint") }},
            {{ fill_nulls("people_fully_vaccinated", "float") }},
            {{ fill_nulls("total_boosters", "bigint") }},
            daily_vaccinations_raw,
            {{ fill_nulls("daily_vaccinations", "bigint") }},
            {{ fill_nulls("total_vaccinations_per_hundred", "float") }},
            {{ fill_nulls("people_vaccinated_per_hundred", "float") }},
            people_fully_vaccinated_per_hundred,
            total_boosters_per_hundred,
            daily_vaccinations_per_million,
            {{ fill_nulls("daily_people_vaccinated", "bigint") }},
            {{ daily_difference('daily_people_vaccinated') }} AS new_vaccinated,
            {{ fill_nulls("daily_people_vaccinated_per_hundred", "float") }}

        from source

    )

select *
from renamed
