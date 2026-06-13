if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

import posixpath
import uuid
import requests
from hash import hash_sha256
from s3utils import put_object

output_prefix = "imports/html"


def get_html_bytes(target_url: str):
    session = requests.Session()
    response = session.get(target_url)
    response.raise_for_status()
    return response.content


def generate_filename() -> str:
    return f"nfce-{uuid.uuid7()}.html"


if __name__ == "__main__":
    filename = generate_filename()
    url = "http://www.sefaz.mt.gov.br/nfce/consultanfce?p=51260509477652008413651230002620731725445443|2|1|1|8D8C7A538544E4EF09D4749A4D5E4C70DA94863C"
    data = get_html_bytes(url)
    hash = hash_sha256(data)
    metadata = {
        "sha256": hash
    }
    key = posixpath.join(output_prefix, filename)
    put_object(key, data, metadata)
