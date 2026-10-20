CREATE TABLE IF NOT EXISTS employees (
  id          BIGSERIAL PRIMARY KEY,
  full_name   TEXT NOT NULL,
  position    TEXT NOT NULL,
  hire_date   DATE NOT NULL,
  salary      INTEGER NOT NULL CHECK (salary >= 0),
  manager_id  BIGINT REFERENCES employees(id)
);

CREATE INDEX IF NOT EXISTS idx_employees_manager_id ON employees(manager_id);
CREATE INDEX IF NOT EXISTS idx_employees_position   ON employees(position);
CREATE INDEX IF NOT EXISTS idx_employees_hire_date  ON employees(hire_date);
CREATE INDEX IF NOT EXISTS idx_employees_salary     ON employees(salary);