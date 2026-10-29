"""Install the checksummed portable Java/JMeter/BC versions in tools-lock.json."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import requests

PERF = Path(__file__).resolve().parent
TOOLS = PERF.parents[1] / '.local-tools'


def download(url, destination, algorithm, expected):
    if not destination.exists() or hashlib.new(algorithm, destination.read_bytes()).hexdigest() != expected:
        temporary = destination.with_suffix(destination.suffix + '.part')
        with requests.get(url, stream=True, timeout=90) as response:
            response.raise_for_status()
            with temporary.open('wb') as handle:
                for chunk in response.iter_content(1024 * 1024):
                    handle.write(chunk)
        if hashlib.new(algorithm, temporary.read_bytes()).hexdigest() != expected:
            raise RuntimeError('Checksum mismatch: ' + destination.name)
        temporary.replace(destination)
    print('Verified', destination.name)


def main():
    TOOLS.mkdir(exist_ok=True)
    lock = json.loads((PERF / 'tools-lock.json').read_text(encoding='utf-8'))
    for tool in ['java', 'jmeter']:
        entry = lock[tool]
        algorithm = 'sha256' if tool == 'java' else 'sha512'
        archive = TOOLS / (tool + '.zip')
        download(entry['url'], archive, algorithm, entry[algorithm])
        with ZipFile(archive) as z:
            # Extract only entries within the intended tools directory.
            for name in z.namelist():
                if not (TOOLS / name).resolve().is_relative_to(TOOLS.resolve()):
                    raise RuntimeError('Archive path escapes tools directory')
            z.extractall(TOOLS)
    bc = lock['bcprov']
    target = TOOLS / ('apache-jmeter-' + lock['jmeter']['version']) / 'lib' / ('bcprov-jdk18on-' + bc['version'] + '.jar')
    download(bc['url'], target, 'sha256', bc['sha256'])
    print('Portable tools ready; no system PATH changes required.')


if __name__ == '__main__':
    main()
