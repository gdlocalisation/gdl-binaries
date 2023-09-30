import shutil
import json
import gzip
import pathlib


class App:
    def __init__(self) -> None:
        self.cwd = pathlib.Path(__file__).parent.resolve()
        self.parent_cwd = self.cwd.parent.resolve()
        self.out_dir = self.parent_cwd.joinpath('Release')
        self.assets_dir = self.parent_cwd.joinpath('gdl-assets')
        if not self.assets_dir.is_dir():
            raise FileNotFoundError(
                f'Could not find gdl-assets at {self.assets_dir}'
            )
        if self.out_dir.is_dir():
            shutil.rmtree(self.out_dir)
        self.out_dir.mkdir()
        self.ball_json = json.loads(open(
            self.parent_cwd.joinpath('template.json'), 'r', encoding='utf-8'
        ).read())
        self.ball = b''
        self.append_gdl_assets()
        self.append_gdl_binaries()
        self.write_out()

    def append_gdl_assets(self) -> None:
        self.ball_json['gdl-assets'] = []
        self.ball_json['gdl-assets-size'] = 0
        for fn in self.assets_dir.iterdir():
            if not fn.is_file():
                continue

            with open(fn, 'rb') as f:
                content = f.read()

            self.ball_json['gdl-assets'].append({
                'fn': fn.name,
                'size': len(content)
            })

            self.ball_json['gdl-assets-size'] += len(content)
            self.ball += content

    def append_gdl_binaries(self) -> None:
        self.ball_json['gdl-binaries'] = []
        for fn in list(self.cwd.iterdir()) + [self.parent_cwd.joinpath("ru_ru.json")]:
            if not fn.is_file() or fn.suffix.lower() in ['.py', '.md']:
                continue

            with open(fn, 'rb') as f:
                content = f.read()

            self.ball_json['gdl-binaries'].append({
                'fn': fn.name,
                'size': len(content)
            })

            self.ball += content

    def write_out(self) -> None:
        compressed = gzip.compress(self.ball)

        self.ball_json['u-size'] = len(self.ball)
        self.ball_json['size'] = len(compressed)

        with open(self.out_dir.joinpath('gdl-binaries.json'), 'w', encoding='utf-8') as f:
            json.dump(self.ball_json, f, ensure_ascii=False, indent=4)

        with open(self.out_dir.joinpath('gdl-binaries.bin.gzip'), 'wb') as f:
            f.write(compressed)

        self.print_stats(compressed)

    def print_stats(self, compressed: bytes) -> None:
        print(
            f'Uncompressed size: {round(len(self.ball) / 1024 / 1024 * 100) / 100}MB'
        )
        print(
            f'Compressed size: {round(len(compressed) / 1024 / 1024 * 100) / 100}MB'
        )
        print(
            f'[{round(len(compressed) / len(self.ball) * 100)}% of 100%] or', end=' '
        )
        print(f'[100% of {round(len(self.ball) / len(compressed) * 100)}%]')


if __name__ == '__main__':
    App()
