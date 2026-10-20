from mimesis import Field, Schema


JOB_LIST = ['CEO', 'Manager', 'Team Lead', 'Senior Developer', 'Developer', 'Intern']


def create_type(
        number,
        manager_id_start=0,
        manager_id_end=0,
        salary_coefficient=1,
        hire_date_start=2000
):
    field = Field()
    schema_definition = lambda : {
        'full_name': field('person.full_name'),
        'hire_date': field(
            'datetime.formatted_date',
            fmt='%Y-%m-%d',
            start=hire_date_start,
            end=2025
            ),
        'salary': field(
            'numeric.integer_number',
            start=round(700000*salary_coefficient),
            end=round(1000000*salary_coefficient)
            ),
        'manager_id': field(
            'numeric.integer_number',
            start=manager_id_start,
            end=manager_id_end
            )
    }
    return Schema(schema=schema_definition, iterations=number)


def create_personnel(total_number, id_first):
    job_titles = JOB_LIST[1:]
    job_percantages = [5, 10, 25, 50, 10]
    salary_coefficients = [0.8, 0.6, 0.4, 0.2, 0.05]
    hire_date_starts = [2000, 2005, 2010, 2020, 2025]
    personnel = dict()
    manager_id_start = id_first
    manager_id_end = id_first
    remaining_number = total_number
    data = zip(job_titles, job_percantages, salary_coefficients, hire_date_starts)
    for job_title, job_percantage, salary_coefficient, hire_date_start in data:
        current_number = max(1, round(job_percantage*total_number/100))
        current_number = min(current_number, remaining_number)
        if current_number == 0:
            break
        personnel[job_title] = create_type(
            current_number,
            manager_id_start,
            manager_id_end,
            salary_coefficient,
            hire_date_start
        )
        manager_id_start = manager_id_end + 1
        manager_id_end = manager_id_start + current_number - 1
        remaining_number -= current_number
    return personnel


if __name__ == '__main__':
    personnel = create_personnel(30, 2)
    for job_title, employees in personnel.items():
        print(job_title)
        for employee in employees:
            print(employee)
