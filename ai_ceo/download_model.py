from huggingface_hub import snapshot_download
from constants import PROJECT_ROOT

snapshot_download(
    repo_id="BAAI/bge-small-en-v1.5",
    local_dir=PROJECT_ROOT / "models" / "BAAI__bge-small-en-v1.5",
    local_dir_use_symlinks=False
)