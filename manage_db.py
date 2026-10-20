from tabulate import tabulate

from src import actions
from src.parsing import build_parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        match args.cmd:
            case 'init-db':
                actions.init_db()
                print('База данных employees инициализированна')
            case 'drop-db':
                actions.drop_db()
                print('База данных employees удалена')
            case 'add':
                new_id = actions.add_employee(
                    full_name=args.full_name,
                    position=args.position,
                    hire_date=args.hire_date,
                    salary=args.salary,
                    manager_id=args.manager_id
                )
                print(f'Добавлен новый сотрудник, id = {new_id}')
            case 'update':
                vacancy_id, position = actions.update_employee(
                    id=args.id,
                    full_name=args.full_name,
                    position=args.position,
                    hire_date=args.hire_date,
                    salary=args.salary,
                    manager_id=args.manager_id
                )
                print(f'Обновлена информация о сотруднике с id = {args.id}')
                if vacancy_id is not None:
                    print(f'Oткрыта вакансия {position} с id = {vacancy_id}')
            case 'delete':
                vacancy_id, position = actions.remove_employee(id=args.id)
                print(f'Сотрудник с id = {args.id} удален из базы данных')
                if vacancy_id is not None:
                    print(f'Oткрыта вакансия {position} с id = {vacancy_id}')
            case 'tree':
                rows = actions.show_tree()
                for row in rows:
                    s = ' '*2*(row[4]-1) + f'{row[1]} - {row[2]}, id: {row[0]}'
                    print(s)
            case 'subtree':
                rows = actions.show_subtree(id=args.id)
                for row in rows:
                    s = ' '*2*(row[4]-1) + f'{row[1]} - {row[2]}, id: {row[0]}'
                    print(s)
            case 'list':
                rows = actions.show_employees(
                    sort_field=args.sort,
                    sort_order=args.order,
                    position=args.position,
                    min_salary=args.min_salary,
                    max_salary=args.max_salary,
                    min_id=args.min_id,
                    max_id=args.max_id,
                    first_hire_date=args.first_hire_date,
                    last_hire_date=args.last_hire_date,
                    limit=args.limit
                )
                print(
                    tabulate(
                        rows,
                        headers=["id", "full_name", "position", "salary"],
                        tablefmt="github"
                    )
                )
            case 'delete-subtree':
                actions.remove_subtree(id=args.id)
                print(f'Поддерево с корневым id = {args.id} удалено')
            case 'seed':
                id_first = actions.seed_db(number=args.n)
                print(
                    'В базу данных добавлены новые сотрудники, '
                    f'количество = {args.n}, первый id = {id_first}'
                )
    except Exception as e:
        print(f'При выполнении запроса к базе данных произошла ошибка:\n{e}')
        return


if __name__ == '__main__':
    main()
