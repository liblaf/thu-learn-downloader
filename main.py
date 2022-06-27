import argparse


from downloader import Downloader


parser = argparse.ArgumentParser(
    add_help="Automatically download files from THU Web Learning."
)
parser.add_argument("--username", required=True)
parser.add_argument("--password", required=True)
parser.add_argument(
    "--semesters",
    nargs="+",
    default=None,
    required=False,
    help="semesters to be synced. If you want to sync all semesters, do not pass this argument",
)
parser.add_argument(
    "--prefix", default=None, required=False, help="location to save downloaded files",
)
parser.add_argument(
    "--file_size_limit",
    default=None,
    type=float,
    required=False,
    help="files exceed limit will not be downloaded",
)
parser.add_argument(
    "--no_sync_docs",
    action="store_true",
    default=False,
    required=False,
    help="pass this argument to skip syncing files",
)
parser.add_argument(
    "--no_sync_work",
    action="store_true",
    default=False,
    required=False,
    help="pass this argument to skip syncing homework",
)
parser.add_argument(
    "--no_sync_submit",
    action="store_true",
    default=False,
    required=False,
    help="pass this argument to skip syncing your submission & grade and everything personal",
)


def main(args: argparse.Namespace):
    downloader = Downloader(
        prefix=args.prefix,
        file_size_limit=args.file_size_limit,
        sync_docs=(not args.no_sync_docs),
        sync_work=(not args.no_sync_work),
        sync_submit=(not args.no_sync_submit),
    )
    downloader.login(username=args.username, password=args.password)
    semester_id_list = downloader.get_semester_id_list()
    semesters = args.semesters if args.semesters else semester_id_list
    for semester in semesters:
        if semester in semester_id_list:
            downloader.SyncSemester(semester_id=semester)
        else:
            print(f"{semester} not found")


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
