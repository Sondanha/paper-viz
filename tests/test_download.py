import requests
import zipfile
import io
import os

# 클라우드타입 배포 주소
BASE_URL = "https://port-0-paper-viz-mc3ho385f405b6d9.sel5.cloudtype.app"

arxiv_id = "1506.02640"
url = f"{BASE_URL}/api/viz-api/generate-zip/{arxiv_id}"

# zip 요청
resp = requests.post(url)
resp.raise_for_status()  # 에러 나면 예외 발생

# 저장할 폴더
out_dir = f"./slides_{arxiv_id}"
os.makedirs(out_dir, exist_ok=True)

# zip 풀기
with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
    z.extractall(out_dir)

print(f"✅ PNG 파일들이 {out_dir} 폴더에 풀림")

