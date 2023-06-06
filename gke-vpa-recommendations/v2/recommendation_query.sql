SELECT *
FROM (
WITH data_deduped as (
SELECT
  *
FROM
  `${project_id}.${table_dataset}.${table_id}`
WHERE
  1=1 
QUALIFY ROW_NUMBER() OVER (PARTITION BY metric, project_id, location, cluster_name, namespace_name, controller_name, container_name ORDER BY metric_timestamp DESC) = 1
  )
SELECT
  DATE(TIMESTAMP_TRUNC(TIMESTAMP(metric_timestamp), DAY)) AS run_date,
  project_id,
  cluster_name,
  controller_name,
  container_name,
  MAX(metric_timestamp) AS metric_timestamp,
  MAX(CASE WHEN metric = 'replica_count'  THEN point_value ELSE 1 END) AS replica_count,
  
  # CPU METRICS
  MAX(CASE WHEN metric = 'cpu_mcore_usage'  THEN ROUND(point_value, 1) ELSE 0 END) AS cpu_mcore_usage,
  MAX(CASE WHEN metric = 'cpu_requested_mcores'  THEN point_value ELSE 0 END) AS cpu_requested_mcores,
  MAX(CASE WHEN metric = 'cpu_limit_mcores'  THEN point_value ELSE 0 END) AS cpu_limit_mcores,
  MAX(CASE WHEN metric = 'cpu_request_utilization_mean'  THEN ROUND(point_value, 1) ELSE 0 END) AS cpu_request_utilization_mean,
  MAX(CASE WHEN metric = 'cpu_limit_utilization_max'  THEN ROUND(point_value, 1) ELSE 0 END) AS cpu_limit_utilization_max,

  # CPU RECOMMENDATION
  ROUND((SAFE_DIVIDE(MAX(IF(metric = 'cpu_mcore_usage', point_value, 0)),MAX(IF(metric = 'replica_count', point_value, 0))) / 0.70) * (1 + 0.2), 1) AS cpu_request_recommendations,
 ROUND(((SAFE_DIVIDE(MAX(IF(metric = 'cpu_mcore_usage', point_value, 0)),MAX(IF(metric = 'replica_count', point_value, 0))) / 0.70) * (1 + 0.2)) * (
    SAFE_DIVIDE(MAX(CASE WHEN metric = 'cpu_limit_mcores'  THEN point_value ELSE 1 END),MAX(CASE WHEN metric = 'cpu_requested_mcores'  THEN point_value ELSE 1 END))
  ),1)
  
  AS cpu_limit_recommendations,

  # MEMORY METRICS
  MAX(CASE WHEN metric = 'memory_max_used_mib'  THEN ROUND(point_value, 1)  ELSE 0 END) AS memory_max_used_mib,
  MAX(CASE WHEN metric = 'memory_requested_mib'  THEN ROUND(point_value, 1)  ELSE 0 END) AS memory_requested_mib,
  MAX(CASE WHEN metric = 'memory_limit_mib'  THEN ROUND(point_value, 1)  ELSE 0 END) AS memory_limit_mib,
  MAX(CASE WHEN metric = 'memory_limit_utilization_max'  THEN ROUND(point_value, 1)  ELSE 0 END) AS memory_limit_utilization_max,
  MAX(CASE WHEN metric = 'memory_request_utilization_max'  THEN ROUND(point_value, 1)  ELSE 0 END) AS memory_request_utilization_max,

  # MEMORY RECOMMENDATION
  ROUND(MAX(IF(metric = 'memory_max_used_mib', point_value, 0)) *  (1 + 0.25), 1) AS memory_request_recommendations,
  ROUND(MAX(IF(metric = 'memory_max_used_mib', point_value, 0)) *  (1 + 0.25), 1) AS memory_limit_recommendations
FROM
  data_deduped 
GROUP BY 1,2,3,4,5
) WHERE cpu_mcore_usage > 0 AND memory_max_used_mib > 0