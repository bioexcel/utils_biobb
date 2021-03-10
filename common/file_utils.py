from pathlib import Path


def get_file_path_list(dir_path=None, extension="json", remove_dir_name=True, exclude_test_dir=True):
    if not dir_path:
        dir_path = Path.cwd()

    dir_path = Path(dir_path).absolute()
    if not dir_path.exists():
        raise FileNotFoundError(str(dir_path))
    if not dir_path.is_dir():
        raise NotADirectoryError(str(dir_path))

    list_paths = list(dir_path.glob(f'**/*.{extension}'))

    if exclude_test_dir:
        list_paths = list(
            filter(lambda file_path: not str(Path(dir_path.name).joinpath('test')) in str(file_path), list_paths))

    if remove_dir_name:
        list_paths = list(
            filter(lambda file_path: not str(file_path).endswith(f'{Path(dir_path.name)}.{extension}'), list_paths))

    return list_paths






