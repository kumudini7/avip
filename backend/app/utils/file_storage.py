from pathlib import Path


def save_uploaded_file(base_dir: str, filename: str, content: bytes) -> Path:
    target_dir = Path(base_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename
    target_path.write_bytes(content)
    return target_path

