import hydra
import omegaconf
import tqdm

from downloader import Downloader


@hydra.main(config_path=".", config_name="identity.yaml", version_base="1.2")
def main(cfg: omegaconf.DictConfig):
    downloader = Downloader(
        username=cfg["username"],
        password=cfg["password"],
        prefix=cfg["prefix"],
        file_size_limit=cfg["file_size_limit"],
        sync_docs=cfg["sync_docs"],
        sync_work=cfg["sync_work"],
        sync_submit=cfg["sync_submit"],
    )
    semester_id_list: list[str] = downloader.helper.get_semester_id_list()
    semesters: list[str] = cfg["semesters"] if cfg["semesters"] else semester_id_list
    for semester in tqdm.tqdm(
        iterable=semesters,
        desc="semesters",
        leave=False,
        dynamic_ncols=True,
        position=0,
    ):
        if semester in semester_id_list:
            downloader.sync_semester(semester_id=semester)
        else:
            print(f"{semester} not found")


if __name__ == "__main__":
    main()
