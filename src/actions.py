from .connection import get_conn
from .personnel_generator import create_type, create_personnel, JOB_LIST


ALLOWED_SORT_FIELDS = {"id", "full_name", "hire_date", "salary"}

ALLOWED_SORT_ORDERS = {'asc', 'desc'}

JOB_RANKS = {JOB_LIST[i]: i for i in range(len(JOB_LIST))}


def init_db(file_path='src/schema.sql'):
    with open(file_path, 'r', encoding='utf-8') as f:
        ddl = f.read()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)


def drop_db():
    sql = 'DROP TABLE employees;'

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def add_employee(full_name, position, hire_date, salary, manager_id):
    sql = """
    INSERT INTO employees(full_name, position, hire_date, salary, manager_id)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    sql_search = 'SELECT position FROM employees WHERE id = %s'
    if position not in JOB_RANKS:
        raise ValueError(f'Выберете название должности из списка:\n{list(JOB_RANKS.keys())}')
    if position == JOB_LIST[0] and manager_id is not None:
        raise ValueError(f'{position} - старшая позиция компании, manager-id не указывается')
    if manager_id is None and position != JOB_LIST[0]:
        employee_rank = JOB_RANKS[position]
        manager_rank = employee_rank - 1
        manager_position = JOB_LIST[manager_rank]
        raise ValueError(
            f'Для позиции {position} нужно указать руководителя с позицией {manager_position}'
        )
    if manager_id is not None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_search, (manager_id,))
                result = cur.fetchall()
        if not result:
            raise ValueError(f'Сотрудник с id = {manager_id} отсутствует')
        manager_position = result[0][0]
        manager_rank = JOB_RANKS[manager_position]
        employee_rank = JOB_RANKS[position]
        if manager_rank+1 != employee_rank:
            manager_rank = employee_rank - 1
            manager_position = JOB_LIST[manager_rank]
            raise ValueError(
                f'Для позиции {position} руководитель должен иметь позицию {manager_position}'
            )

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (full_name, position, hire_date, salary, manager_id))
            return cur.fetchone()[0]


def update_employee(id, full_name, position, hire_date, salary, manager_id):
    columns = []
    params = []
    sql_search = 'SELECT position, manager_id, salary FROM employees WHERE id = %s'
    next_manager_rank = None
    if manager_id is not None:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_search, (manager_id,))
                result = cur.fetchall()
        if not result:
            raise ValueError(f'Сотрудник с id = {manager_id} отсутствует')
        next_manager_position = result[0][0]
        next_manager_rank = JOB_RANKS[next_manager_position]
    if id is None:
        raise ValueError('Укажите id сотрудника для изменения данных')
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_search, (id,))
            result = cur.fetchall()
    if not result:
        raise ValueError(f'Сотрудник с id = {id} отсутствует')
    prev_position = result[0][0]
    prev_manager_id = result[0][1]
    prev_salary = result[0][2]
    prev_rank = JOB_RANKS[prev_position]
    next_rank = prev_rank
    if position:
        if position not in JOB_RANKS:
            raise ValueError(f'Выберете название должности из списка:\n{list(JOB_RANKS.keys())}')
        next_rank = JOB_RANKS[position]
    else:
        position = prev_position
    if next_manager_rank is not None:
        if (prev_rank == 0 and next_rank is None) or next_rank == 0:
            raise ValueError(f'{position} - старшая позиция компании, manager-id не указывается')
        if next_manager_rank != next_rank - 1:
            raise ValueError(
                f'Для позиции {position} руководитель должен иметь позицию {JOB_LIST[next_rank-1]}'
            )
    else:
        if next_rank != 0 and prev_rank != next_rank:
            raise ValueError(
                f'Для позиции {position} нужно указать руководителя с позицией {JOB_LIST[next_rank-1]}'
            )

    if prev_rank != next_rank:
        sql_subordinates = 'SELECT id FROM employees WHERE manager_id = %s'
        sql_update = 'UPDATE employees SET manager_id = %s WHERE id IN (%s'
        params_2 = []
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_subordinates, (id,))
                result = cur.fetchall()
        vacancy_id = None
        if result:
            vacancy_id = add_employee(
                'Vacancy',
                prev_position,
                '2000-01-01',
                prev_salary,
                prev_manager_id
            )
            params_2.append(vacancy_id)
            for row in result:
                params_2.append(row[0])
            sql_update += ', %s'*(len(result)-1) + ')'
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql_update, tuple(params_2))

    if full_name:
        columns.append('full_name = %s')
        params.append(full_name)

    if position:
        columns.append('position = %s')
        params.append(position)

    if hire_date:
        columns.append('hire_date = %s')
        params.append(hire_date)

    if salary is not None:
        columns.append('salary = %s')
        params.append(salary)

    if manager_id is not None or next_rank == 0:
        columns.append('manager_id = %s')
        params.append(manager_id)

    sql = 'UPDATE employees SET ' + ', '.join(columns) + ' WHERE id = %s'
    params.append(id)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
    return vacancy_id, prev_position


def remove_employee(id):
    sql = 'DELETE FROM employees WHERE id = %s'
    sql_search = 'SELECT position, manager_id, salary FROM employees WHERE id = %s'
    sql_update = 'UPDATE employees SET manager_id = %s WHERE id IN (%s'
    params = []
    if id is None:
        raise ValueError('Укажите id сотрудника для удаления из базы данных')
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_search, (id,))
            result = cur.fetchall()
    if not result:
        raise ValueError(f'Сотрудник с id = {id} отсутствует')
    position = result[0][0]
    manager_id = result[0][1]
    salary = result[0][2]
    sql_subordinates = 'SELECT id FROM employees WHERE manager_id = %s'
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_subordinates, (id,))
            result = cur.fetchall()
    vacancy_id = None
    if result:
        vacancy_id = add_employee('Vacancy', position, '2000-01-01', salary, manager_id)
        params.append(vacancy_id)
        for row in result:
            params.append(row[0])
        sql_update += ', %s'*(len(result)-1) + ')'
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_update, tuple(params))

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (id,))
    return vacancy_id, position


def show_tree(file_path='src/tree.sql'):
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            return cur.fetchall()


def show_subtree(id, file_path='src/subtree.sql'):
    if id is None:
        raise ValueError('Укажите корневой id сотрудника')
    sql_search = 'SELECT position, manager_id, salary FROM employees WHERE id = %s'
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_search, (id,))
            result = cur.fetchall()
    if not result:
        raise ValueError(f'Сотрудник с id = {id} отсутствует')
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (id,))
            return cur.fetchall()


def remove_subtree(id, file_path='src/delete_subtree.sql'):
    if id is None:
        raise ValueError('Укажите корневой id сотрудника')
    sql_search = 'SELECT position, manager_id, salary FROM employees WHERE id = %s'
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_search, (id,))
            result = cur.fetchall()
    if not result:
        raise ValueError(f'Сотрудник с id = {id} отсутствует')
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (id,))


def make_order_by(sort_field, sort_order):
    if sort_field not in ALLOWED_SORT_FIELDS:
        sort_field = 'id'
    if sort_order not in ALLOWED_SORT_ORDERS:
        sort_order = 'asc'
    sql = f' ORDER BY {sort_field} {sort_order.upper()}'
    return sql


def show_employees(
        sort_field,
        sort_order,
        position,
        min_salary,
        max_salary,
        min_id,
        max_id,
        first_hire_date,
        last_hire_date,
        limit
):
    columns = []
    params = []

    if position:
        columns.append('position = %s')
        params.append(position)

    if min_salary is not None:
        columns.append('salary >= %s')
        params.append(min_salary)

    if max_salary is not None:
        columns.append('salary <= %s')
        params.append(max_salary)

    if min_id is not None:
        columns.append('id >= %s')
        params.append(min_id)

    if max_id is not None:
        columns.append('id <= %s')
        params.append(max_id)

    if first_hire_date is not None:
        columns.append('hire_date >= %s')
        params.append(first_hire_date)

    if last_hire_date is not None:
        columns.append('hire_date <= %s')
        params.append(last_hire_date)

    sql = 'SELECT id, full_name, position, salary FROM employees'
    if columns:
        sql += " WHERE " + " AND ".join(columns)
    sql += make_order_by(sort_field, sort_order)
    sql += " LIMIT %s"
    params.append(limit)

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchall()


def seed_db(number):
    if number < 5:
        raise ValueError('Число позиций для генерации должно быть больше 4')
    first = create_type(1).__next__()
    id_first = add_employee(
        first['full_name'],
        JOB_LIST[0],
        first['hire_date'],
        first['salary'],
        None
    )
    personnel = create_personnel(number-1, id_first)
    sql = 'INSERT INTO employees(full_name, position, hire_date, salary, manager_id) VALUES '
    sql += '(%s, %s, %s, %s, %s), '*(number-2)
    sql += '(%s, %s, %s, %s, %s)'
    params = []
    for job_title, employees in personnel.items():
        for employee in employees:
            params.append(employee['full_name'])
            params.append(job_title)
            params.append(employee['hire_date'])
            params.append(employee['salary'])
            params.append(employee['manager_id'])

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(params))
    return id_first
