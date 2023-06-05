SELECT
    date,
    COUNT(*) AS number_of_workloads_analyzed,
    SAFE_DIVIDE(COUNT(CASE WHEN memory_request_utilization_max_percentage >= 100.0  THEN 1 END), COUNT(CASE WHEN memory_request_utilization_max_percentage != 0  THEN 1 END)) AS count_mem_utilization,
    SAFE_DIVIDE(COUNT(CASE WHEN memory_requested_mib = 0  THEN 1 END), COUNT(*)) AS best_effort_mem,
    SAFE_DIVIDE(COUNT(CASE WHEN cpu_requested_mcores = 0  THEN 1 END), COUNT(*)) AS best_effort_cpu,
    SAFE_DIVIDE(COUNT(CASE WHEN memory_request_utilization_max_percentage >= 100.0  THEN 1 END),COUNT(CASE WHEN memory_request_utilization_max_percentage != 0  THEN 1 END)) AS count_mem_utilization,
    SAFE_DIVIDE(COUNT(CASE WHEN cpu_request_utilization_mean_percentage >= 100.0  THEN 1 END),COUNT(CASE WHEN cpu_request_utilization_mean_percentage != 0  THEN 1 END)) AS count_cpu_utilization
FROM
    `${project_id}.${table_dataset}.${table_id}`
GROUP BY
    date;