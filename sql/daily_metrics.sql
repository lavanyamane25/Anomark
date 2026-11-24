DROP VIEW IF EXISTS public.daily_quality_summary;
DROP TABLE IF EXISTS public.daily_quality_metrics;

DROP TABLE IF EXISTS public.daily_quality_metrics;

CREATE TABLE public.daily_quality_metrics AS
SELECT
    DATE(created_date) AS request_date,
    COUNT(*) AS total_requests,
    COUNT(DISTINCT unique_key) AS unique_requests,
    COUNT(*) FILTER (
        WHERE invalid_date_order = TRUE
    ) AS invalid_date_records,
    COUNT(*) FILTER (
        WHERE closed_without_closed_date = TRUE
    ) AS closed_missing_date_records
FROM public.service_requests_clean
GROUP BY DATE(created_date)
ORDER BY request_date;

CREATE OR REPLACE VIEW public.daily_quality_summary AS
SELECT
    *,
    ROUND(invalid_date_records * 100.0 /
        NULLIF(total_requests, 0), 2) AS invalid_date_percentage,
    ROUND(closed_missing_date_records * 100.0 /
        NULLIF(total_requests, 0), 2) AS closed_missing_date_percentage
FROM public.daily_quality_metrics;