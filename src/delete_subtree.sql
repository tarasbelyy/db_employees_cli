WITH RECURSIVE org AS (
  SELECT id, full_name, position, manager_id, 1 AS lvl, ARRAY[id] as pth
  FROM employees
  WHERE id = %s

  UNION ALL

  SELECT e.id, e.full_name, e.position, e.manager_id, org.lvl + 1, pth || e.id
  FROM employees e
  JOIN org ON e.manager_id = org.id
)
DELETE FROM employees 
WHERE id IN (
SELECT id
FROM org
ORDER BY lvl DESC);