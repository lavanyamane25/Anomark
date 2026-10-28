SELECT
    COUNT(*) AS total_records,
    COUNT(unique_key) AS records_with_id,
    COUNT(created_date) AS records_with_created_date,
    COUNT(agency) AS records_with_agency,
    COUNT(complaint_type) AS records_with_complaint_type
FROM public."311_service_requests";

SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT unique_key) AS unique_request_ids,
    COUNT(*) - COUNT(DISTINCT unique_key) AS duplicate_id_count
FROM public."311_service_requests";

SELECT
    unique_key,
    COUNT(*) AS occurrences
FROM public."311_service_requests"
GROUP BY unique_key
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;

SELECT
    COUNT(*) FILTER (WHERE unique_key IS NULL) AS missing_ids,
    COUNT(*) FILTER (WHERE created_date IS NULL) AS missing_created_dates,
    COUNT(*) FILTER (WHERE agency IS NULL) AS missing_agencies,
    COUNT(*) FILTER (WHERE complaint_type IS NULL) AS missing_complaint_types,
    COUNT(*) FILTER (WHERE borough IS NULL) AS missing_boroughs,
    COUNT(*) FILTER (WHERE status IS NULL) AS missing_statuses,
    COUNT(*) FILTER (WHERE incident_zip IS NULL) AS missing_zip_codes
FROM public."311_service_requests";

SELECT
    status,
    COUNT(*) AS record_count,
    ROUND(
        COUNT(*) * 100.0 / NULLIF(SUM(COUNT(*)) OVER (), 0),
        2
    ) AS percentage
FROM public."311_service_requests"
GROUP BY status
ORDER BY record_count DESC;

SELECT
    complaint_type,
    COUNT(*) AS request_count
FROM public."311_service_requests"
WHERE complaint_type IS NOT NULL
GROUP BY complaint_type
ORDER BY request_count DESC
LIMIT 10;

SELECT
    COALESCE(NULLIF(TRIM(borough), ''), 'UNKNOWN') AS borough,
    COUNT(*) AS request_count
FROM public."311_service_requests"
GROUP BY COALESCE(NULLIF(TRIM(borough), ''), 'UNKNOWN')
ORDER BY request_count DESC;

SELECT
    DATE(created_date::timestamp) AS request_date,
    COUNT(*) AS daily_records
FROM public."311_service_requests"
WHERE created_date IS NOT NULL
GROUP BY DATE(created_date::timestamp)
ORDER BY request_date;

SELECT
    unique_key,
    created_date,
    closed_date
FROM public."311_service_requests"
WHERE created_date IS NOT NULL
  AND closed_date IS NOT NULL
  AND closed_date::timestamp < created_date::timestamp
ORDER BY created_date
LIMIT 100;

SELECT
    COUNT(*) AS total_records,

    COUNT(*) FILTER (
        WHERE unique_key IS NULL
    ) AS missing_ids,

    COUNT(*) FILTER (
        WHERE created_date IS NULL
    ) AS missing_created_dates,

    COUNT(DISTINCT unique_key) AS distinct_request_ids,

    COUNT(*) FILTER (
        WHERE agency IS NULL
           OR complaint_type IS NULL
           OR status IS NULL
    ) AS records_missing_key_fields,

    ROUND(
        COUNT(*) FILTER (
            WHERE unique_key IS NULL
               OR created_date IS NULL
               OR agency IS NULL
               OR complaint_type IS NULL
               OR status IS NULL
        ) * 100.0 / NULLIF(COUNT(*), 0),
        2
    ) AS critical_missing_percentage

FROM public."311_service_requests";