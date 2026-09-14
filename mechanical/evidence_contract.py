"""Shared fail-closed mechanical evidence checks; official pins from CAD_REPORT."""
import hashlib
from pathlib import Path

RENDER_TRANSLATION = (-70.947472, 106.31508, 4.085)
RENDER_SOURCES = {'official_radxa.stp': (0,0,0), **{name: RENDER_TRANSLATION for name in ('board.step','bottom.step','j4-current.step','c45.step')}}
RENDER_OUTPUTS = ('stack_4mm.png', 'stack_4mm_header_side.png')

MAX_ARCHIVE_BYTES = 16*1024*1024
MAX_STEP_BYTES = 64*1024*1024

def acquire_official(output):
    """Bound HTTPS reads and ZIP expansion; publish only the reviewed bytes."""
    import os
    import tempfile
    import time
    import urllib.request
    import zipfile
    output = Path(output)
    with tempfile.TemporaryDirectory(prefix='.official-', dir=output) as temporary:
        stage = Path(temporary)
        archive = stage/'official-current.zip'
        deadline = time.monotonic()+120
        with urllib.request.urlopen(OFFICIAL_URL, timeout=30) as response, archive.open('wb') as target:
            total = 0
            while True:
                require(time.monotonic() < deadline, 'official download deadline')
                chunk = response.read(1024*1024)
                if not chunk:
                    break
                total += len(chunk)
                require(total <= MAX_ARCHIVE_BYTES, 'official download size limit')
                target.write(chunk)
        require(sha(archive) == OFFICIAL_ZIP_SHA256, 'official ZIP hash differs from reviewed pin')
        with zipfile.ZipFile(archive) as z:
            members = [x for x in z.infolist() if x.filename.lower().endswith(('.stp','.step'))]
            require(len(members) == 1, 'official STEP inventory')
            require(0 < members[0].file_size <= MAX_STEP_BYTES, 'official STEP size limit')
            (stage/'official_radxa.stp').write_bytes(z.read(members[0]))
        verify_official(stage)
        for name in ('official-current.zip','official_radxa.stp'):
            os.replace(stage/name, output/name)

J4_MODEL_SHA256 = 'd5503fca60b62f7d24dcaec78bbc2f76d75032de7a299e5beee15c5749f0aad5'
J4_ROTATION = [-90,0,90]
J4_OFFSET = [0,-4.19905533063427,.302503373819]

def verify_j4(scratch, inputs, evidence=None):
    import json
    scratch = Path(scratch)
    metadata = json.loads((scratch/'j4-current-metadata.json').read_text())
    require(metadata['source_pcb_sha256'] == inputs['pcb_sha256'] == sha(inputs['source_pcb']), 'J4 binding: source PCB')
    require(Path(metadata['source_pcb']).resolve() == Path(inputs['source_pcb']).resolve(), 'J4 binding: source path')
    require(metadata['model_sha256'] == J4_MODEL_SHA256 == sha(metadata['model_file']), 'J4 binding: model')
    require(metadata['native_step_file'] == 'j4-current.step', 'J4 binding: export filename')
    require(metadata['native_step_sha256'] == sha(scratch/'j4-current.step'), 'J4 binding: export hash')
    require(metadata['source_unchanged'] is True, 'J4 binding: source changed')
    require(metadata['rotation_deg'] == J4_ROTATION and metadata['offset_mm'] == J4_OFFSET and metadata['scale'] == [1,1,1], 'J4 binding: transform')
    if evidence is not None:
        for key in ('source_pcb_sha256','model_sha256','native_step_sha256','native_step_file','rotation_deg','offset_mm','scale'):
            require(evidence[key] == metadata[key], f'J4 binding: analysis {key}')
    return metadata

OFFICIAL_URL = 'https://dl.radxa.com/zero3/docs/hw/3w/radxa_zero_3w_3d_stp.zip'
OFFICIAL_ZIP_SHA256 = '0dfc39db5f52665ef92bcab34781132aba399a4061dc2c869f757a00f446d2cf'
OFFICIAL_STEP_SHA256 = '1eac96aa8804f7270e08610ebd99bf0eccfd26d39d859fae76d119406694ded3'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def require(condition, message):
    if not condition:
        raise ValueError(message)

def verify_official(scratch, *records):
    scratch = Path(scratch)
    require(sha(scratch/'official-current.zip') == OFFICIAL_ZIP_SHA256, 'official ZIP hash differs from reviewed pin')
    require(sha(scratch/'official_radxa.stp') == OFFICIAL_STEP_SHA256, 'official STEP hash differs from reviewed pin')
    for row in records:
        require(row['zip_sha256'] == OFFICIAL_ZIP_SHA256, 'official ZIP metadata hash')
        require(row['step_sha256'] == OFFICIAL_STEP_SHA256, 'official STEP metadata hash')

def png_record(path, name=None):
    # verify() checks chunk CRCs; a separate load() fully decompresses pixels.
    from PIL import Image
    path = Path(path)
    try:
        require(0 < path.stat().st_size <= 32*1024*1024, 'PNG size limit')
        with Image.open(path) as image:
            require(image.format == 'PNG' and image.size == (1600,1000), 'PNG dimensions/format')
            image.verify()
        with Image.open(path) as image:
            image.load()
    except Exception as exc:
        raise ValueError(f'PNG integrity: {path.name}: {exc}') from exc
    return dict(file=name or path.name, sha256=sha(path), bytes=path.stat().st_size)

def verify_render_sources(scratch, metadata):
    rows = metadata['sources']
    names = [row['file'] for row in rows]
    require(len(names) == len(RENDER_SOURCES) and set(names) == set(RENDER_SOURCES), 'render source inventory')
    require(metadata['assumed_gap_mm'] == 4.0, 'render transform: assumed gap')
    for row in rows:
        name = row['file']
        require(tuple(row['translation_mm']) == RENDER_SOURCES[name], f'render transform: {name}')
        require(row['sha256'] == sha(Path(scratch)/name), f'render source hash: {name}')
        require(row['vertices'] > 0 and row['triangles'] > 0, f'render tessellation: {name}')

def verify_render(scratch, output, metadata):
    verify_render_sources(scratch, metadata)
    rows = metadata.get('outputs', [])
    names = [row['file'] for row in rows]
    require(len(names) == len(RENDER_OUTPUTS) and set(names) == set(RENDER_OUTPUTS), 'render output inventory')
    images = []
    for row in rows:
        path = Path(output)/row['file']
        require(row['sha256'] == sha(path), f'render output hash: {path.name}')
        actual = png_record(path)
        require(row == actual, f'render output record: {path.name}')
        images.append(actual)
    return images

def publish_render(scratch, output, metadata, render_image):
    """All fresh writes must decode before replacement; manifest commits last.

    A crash during individual replacements leaves old metadata/hash mismatch,
    never metadata claiming new sources with old or incomplete image bytes.
    """
    import json
    import os
    import tempfile
    output = Path(output)
    verify_render_sources(scratch, metadata)
    with tempfile.TemporaryDirectory(prefix='.render-', dir=output) as temporary:
        staging = Path(temporary)
        images = []
        for view, name in enumerate(RENDER_OUTPUTS):
            path = staging/name
            render_image(path, view)
            images.append(png_record(path))
        result = dict(metadata, outputs=images)
        verify_render(scratch, staging, result)
        manifest = staging/'render_evidence.json'
        manifest.write_text(json.dumps(result, indent=2))
        for name in RENDER_OUTPUTS:
            os.replace(staging/name, output/name)
        os.replace(manifest, output/manifest.name)
    return result
