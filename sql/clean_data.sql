
-- Anomark: NYC 311 Data Cleaning
-- Creates a cleaned table while preserving the raw table.

DROP TABLE IF EXISTS public.service_requests_clean;

CREATE TABLE public.service_requests_clean AS
SELECT
    unique_key,
    created_date,
    closed_date,
    NULLIF(TRIM(agency), '') AS agency,
    NULLIF(TRIM(complaint_type), '') AS complaint_type,
    NULLIF(UPPER(TRIM(borough)), '') AS borough,
    NULLIF(TRIM(status), '') AS status,
    NULLIF(TRIM(incident_zip), '') AS incident_zip,

    (
        closed_date IS NOT NULL
        AND created_date IS NOT NULL
        AND closed_date < created_date
    ) AS invalid_date_order,

    (
        UPPER(TRIM(status)) = 'CLOSED'
        AND closed_date IS NULL
    ) AS closed_without_closed_date

FROM public."311_service_requests";
