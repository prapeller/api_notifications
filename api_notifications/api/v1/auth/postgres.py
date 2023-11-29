import os
import subprocess

import fastapi as fa

from core.config import BASE_DIR
from core.enums import EnvEnum

router = fa.APIRouter()


@router.post("/dump", status_code=fa.status.HTTP_201_CREATED)
def postgres_dump(
        env: EnvEnum = EnvEnum.local,
):
    script_path = BASE_DIR / 'scripts/postgres/dump.sh'
    assert os.path.isfile(script_path)
    result = subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={'ENV': env})
    return {
        'stderr': f'{result.stderr.decode("utf-8", "ignore")}',
        'stdout': f'{result.stdout.decode("utf-8", "ignore")}',
    }


@router.get("/check-dumps")
def postgres_check_dumps():
    script_path = BASE_DIR / 'scripts/postgres/check_dumps.sh'
    assert os.path.isfile(script_path)
    result = subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        'stderr': f'{result.stderr.decode("utf-8", "ignore")}',
        'stdout': f'{result.stdout.decode("utf-8", "ignore")}',
    }


@router.get("/download-last-dump")
def postgres_download_last_dump():
    file_path = BASE_DIR / 'staticfiles/backups/dump_last'
    assert os.path.isfile(file_path)
    headers = {'Content-Disposition': 'attachment',
               'Content-Type': 'application/octet-stream'}
    return fa.responses.FileResponse(path=file_path, headers=headers, filename='dump_last')


@router.post("/restore-from-dump", status_code=fa.status.HTTP_201_CREATED)
async def postgres_restore(
        dump_file: fa.UploadFile,
        env: EnvEnum = EnvEnum.local,
):
    script_path = BASE_DIR / 'scripts/postgres/restore_from_dump.sh'
    assert os.path.isfile(script_path)

    contents = await dump_file.read()
    uploaded_file_path = BASE_DIR / 'staticfiles/backups/uploaded_dump'
    with open(uploaded_file_path, 'wb') as uploaded:
        uploaded.write(contents)

    subprocess.Popen(script_path, env={'ENV': env})
    return {'message': 'ok'}
