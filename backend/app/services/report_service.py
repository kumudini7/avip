from pathlib import Path


def build_report_filename(project_name: str, extension: str) -> str:
    safe_name = project_name.lower().replace(" ", "_")
    return f"{safe_name}.{extension}"


def report_output_path(base_dir: str, filename: str) -> Path:
    path = Path(base_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path / filename

