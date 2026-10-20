import argparse


def build_parser():
    p = argparse.ArgumentParser(prog="employees")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init-db")
    sub.add_parser("drop-db")

    seed = sub.add_parser("seed")
    seed.add_argument("--n", type=int, default=50_000)

    lst = sub.add_parser("list")
    lst.add_argument("--sort", default="id")
    lst.add_argument("--order", default="asc")
    lst.add_argument("--position")
    lst.add_argument("--min-salary", type=int)
    lst.add_argument("--max-salary", type=int)
    lst.add_argument("--min-id", type=int)
    lst.add_argument("--max-id", type=int)
    lst.add_argument("--first-hire-date")
    lst.add_argument("--last-hire-date")
    lst.add_argument("--limit", type=int, default=50)

    insrt = sub.add_parser("add")
    insrt.add_argument("--full-name")
    insrt.add_argument("--salary", type=int)
    insrt.add_argument("--hire-date")
    insrt.add_argument("--manager-id", type=int)
    insrt.add_argument("--position")

    updt = sub.add_parser("update")
    updt.add_argument("--id", type=int)
    updt.add_argument("--full_name")
    updt.add_argument("--salary", type=int)
    updt.add_argument("--hire-date")
    updt.add_argument("--manager-id", type=int)
    updt.add_argument("--position")

    dlt = sub.add_parser("delete")
    dlt.add_argument("--id", type=int)

    sub.add_parser("tree")

    sbtr = sub.add_parser("subtree")
    sbtr.add_argument("--id", type=int)

    dlt_sbtr = sub.add_parser("delete-subtree")
    dlt_sbtr.add_argument("--id", type=int)
    return p


if __name__ == '__main__':
    parser = build_parser()
    args = parser.parse_args()
    print(args.cmd)
