import os
import sys
import shutil
import json
import gzip


class App:
    def __init__(self) -> None:
        self.encoding = sys.getdefaultencoding()
        self.cwd = os.path.dirname(__file__)
        self.out_dir = os.path.join(self.cwd, 'Release')
        self.assets_dir = os.path.join(self.cwd, 'gdl-assets')
        if not os.path.isdir(self.assets_dir):
            raise FileNotFoundError(f'Could not found gdl-assets at {self.assets_dir}')
        if os.path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir)
        os.mkdir(self.out_dir)
        self.ball_json = {}
        self.ball = b''
        self.append_gdl_assets()
        self.append_gdl_binaries()
        self.write_out()

    def append_gdl_assets(self) -> None:
        self.ball_json['gdl-assets'] = []
        self.ball_json['gdl-assets-size'] = 0
        for fn in os.listdir(self.assets_dir):
            fp = os.path.join(self.assets_dir, fn)
            if fn.startswith('.') or not os.path.isfile(fp):
                continue
            f = open(fp, 'rb')
            content = f.read()
            f.close()
            self.ball_json['gdl-assets'].append({
                'fn': fn,
                'size': len(content)
            })
            self.ball_json['gdl-assets-size'] += len(content)
            self.ball += content

    def append_gdl_binaries(self) -> None:
        self.ball_json['gdl-binaries'] = []
        for fn in os.listdir(self.cwd):
            fp = os.path.join(self.cwd, fn)
            fext = fn.split('.')[-1].lower()
            if fn.startswith('.') or not os.path.isfile(fp) or fext in ('py', 'md'):
                continue
            f = open(fp, 'rb')
            content = f.read()
            f.close()
            self.ball_json['gdl-binaries'].append({
                'fn': fn,
                'size': len(content)
            })
            self.ball += content

    def write_out(self) -> None:
        compressed = gzip.compress(self.ball)
        self.ball_json['u-size'] = len(self.ball)
        self.ball_json['size'] = len(compressed)
        json_f = open(os.path.join(self.out_dir, 'gdl-binaries.json'), 'w', encoding=self.encoding)
        json_f.write(json.dumps(self.ball_json))
        json_f.close()
        gzip_f = open(os.path.join(self.out_dir, 'gdl-binaries.bin.gzip'), 'wb')
        gzip_f.write(compressed)
        gzip_f.close()
        self.print_stats(compressed)

    def print_stats(self, compressed: bytes) -> None:
        print(f'Uncompressed size: {round(len(self.ball) / 1024 / 1024 * 100) / 100}MB')
        print(f'Compressed size: {round(len(compressed) / 1024 / 1024 * 100) / 100}MB')
        print(f'[{round(len(compressed) / len(self.ball) * 100)}% of 100%] or', end=' ')
        print(f'[100% of {round(len(self.ball) / len(compressed) * 100)}%]')


if __name__ == '__main__':
    App()
