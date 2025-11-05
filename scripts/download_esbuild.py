#!/usr/bin/env python3
"""
Download esbuild binary for the current platform.
Based on the shell script at https://esbuild.github.io/dl/v0.25.7
"""

from __future__ import annotations

import os
import platform
import stat
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

ESBUILD_VERSION = "0.25.7"


def get_platform_info() -> str:
    """Detect the current platform and architecture."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Map Python's platform names to esbuild's naming convention
    match (system, machine):
        case ("darwin", ("arm64" | "aarch64")):
            return "darwin-arm64"
        case ("darwin", _):
            return "darwin-x64"
        case ("linux", ("arm64" | "aarch64")):
            return "linux-arm64"
        case ("linux", _):
            return "linux-x64"
        case ("windows", ("arm64" | "aarch64")):
            return "win32-arm64"
        case ("windows", _):
            return "win32-x64"
        case _:
            raise RuntimeError(f"Unsupported platform: {system}-{machine}")


def download_esbuild():
    """Download and extract the esbuild binary for the current platform."""
    platform_name = get_platform_info()

    start_time = time.monotonic()

    # Construct the NPM registry URL
    package_name = f"@esbuild/{platform_name}"
    url = f"https://registry.npmjs.org/{package_name}/-/{platform_name}-{ESBUILD_VERSION}.tgz"

    print(f"Downloading esbuild {ESBUILD_VERSION} for {platform_name}...")
    print(f"URL: {url}")

    chunk_size = 512_000  # 500KB chunks - esbuild's around 10MB

    # Download to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".tgz", delete=False) as temp_file:
        try:
            with urllib.request.urlopen(url) as response:
                while chunk := response.read(chunk_size):
                    temp_file.write(chunk)
            temp_file_path = temp_file.name
        except Exception as e:
            raise RuntimeError(f"Failed to download esbuild: {e}")

    try:
        # Extract the binary from the tarball
        with tarfile.open(temp_file_path, "r:gz") as tar:
            # Find the esbuild binary in the package
            binary_name = (
                "esbuild.exe" if platform.system().lower() == "windows" else "esbuild"
            )
            binary_path_in_tar = f"package/bin/{binary_name}"

            try:
                binary_member = tar.getmember(binary_path_in_tar)
            except KeyError:
                raise RuntimeError(f"Binary {binary_path_in_tar} not found in package")

            # Extract to current directory
            script_dir = Path(__file__).parent.parent / "bin"
            output_path = script_dir / binary_name

            with tar.extractfile(binary_member) as binary_file:
                with output_path.open("wb") as output_file:
                    while chunk := binary_file.read(chunk_size):
                        output_file.write(chunk)

            # Make the binary executable
            output_path.chmod(output_path.stat().st_mode | stat.S_IEXEC)

            print(
                f"Successfully downloaded esbuild to '{output_path}'"
                f" in {time.monotonic() - start_time:.1f} seconds."
            )

    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)


if __name__ == "__main__":
    try:
        download_esbuild()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
