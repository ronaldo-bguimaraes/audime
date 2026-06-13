import tempfile
from pathlib import Path

from s3utils import download_file, head_object


def ler_csv_do_r2(key: str) -> str:
    tmp = Path(tempfile.mkdtemp()) / "fatura.csv"
    download_file(key, str(tmp))
    return tmp.read_text(encoding="utf-8")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    key = "raw/Fatura_2026-06-10.csv"
    meta = head_object(key)
    print("ETag:", meta.get("ETag"))
    print("ContentType:", meta.get("ContentType"))
    print("ContentLength:", meta.get("ContentLength"))
    print("LastModified:", meta.get("LastModified"))
    print("Metadata:", meta.get("Metadata"))
    print("-" * 40)
    csv = ler_csv_do_r2(key)
    print(csv)
