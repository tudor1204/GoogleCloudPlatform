SELECT
  controller_name,
  container_name,
  MAX(IF(metric = 'cpu_requested_mcores', point_value, 0)) AS cpu_requested_mcores,
  MAX(IF(metric = 'cpu_limit_mcores', point_value, 0)) AS cpu_limit_mcores,
  MAX(IF(metric = 'cpu_mcore_usage', point_value, 0)) AS cpu_mcore_usage,
  MAX(IF(metric = 'cpu_request_utilization_mean_percentage', point_value, 0)) AS cpu_request_utilization_mean_percentage,
  MAX(IF(metric = 'cpu_request_utilization_max_percentage', point_value, 0)) AS cpu_request_utilization_max_percentage,
  MAX(IF(metric = 'cpu_limit_utilization_max_percentage', point_value, 0)) AS cpu_limit_utilization_max_percentage,
  MAX(IF(metric = 'cpu_request_recommendations_mean_mcores', point_value, 0)) AS cpu_request_recommendations_mean_mcores,
  MAX(IF(metric = 'cpu_request_recommendations_max_mcores', point_value, 0)) AS cpu_request_recommendations_max_mcores,
  MAX(IF(metric = 'memory_requested_mib', point_value, 0)) AS memory_requested_mib,
  MAX(IF(metric = 'memory_limit_mib', point_value, 0)) AS memory_limit_mib,
  MAX(IF(metric = 'memory_max_used_mib', point_value, 0)) AS memory_max_used_mib,
  MAX(IF(metric = 'memory_request_utilization_mean_percentage', point_value, 0)) AS memory_request_utilization_mean_percentage,
  MAX(IF(metric = 'memory_request_utilization_max_percentage', point_value, 0)) AS memory_request_utilization_max_percentage,
  MAX(IF(metric = 'memory_limit_utilization_max_percentage', point_value, 0)) AS memory_limit_utilization_max_percentage,
  MAX(IF(metric = 'memory_request_max_recommendations_mib', point_value, 0)) AS memory_request_max_recommendations_mib,
  MAX(IF(metric = 'memory_request_max_recommendations_mib', point_value, 0)) AS memory_limit_max_recommendations_mib,
  MAX(metric_timestamp) AS metric_timestamp
FROM (
  SELECT
    metric_timestamp,
    controller_name,
    container_name,
    metric,
    point_value,
    ROW_NUMBER() OVER (PARTITION BY controller_name, metric ORDER BY metric_timestamp DESC) AS rn
  FROM
    `${project_id}.${table_dataset}.${table_id}` )
WHERE
  rn = 1
GROUP BY
  1,2
ORDER BY
  1