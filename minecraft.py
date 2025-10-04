import os
import subprocess
import sys
from pathlib import Path


def find_prism_exe():
    """Auto-detect PrismLauncher executable location (Windows, Linux, Flatpak)."""
    possible_paths = []

    if sys.platform == "win32":
        possible_paths = [
            Path.home() / "AppData/Local/Programs/PrismLauncher/prismlauncher.exe",
            Path("C:/Program Files/PrismLauncher/prismlauncher.exe"),
            Path("C:/Program Files (x86)/PrismLauncher/prismlauncher.exe"),
        ]
    else:
        # Native Linux and Flatpak locations
        possible_paths = [
            Path("/usr/bin/prismlauncher"),
            Path("/usr/local/bin/prismlauncher"),
            Path.home() / ".local/bin/prismlauncher",
            Path("/var/lib/flatpak/exports/bin/org.prismlauncher.PrismLauncher"),
            Path.home() / ".local/share/flatpak/exports/bin/org.prismlauncher.PrismLauncher",
        ]

    # Check known paths
    for path in possible_paths:
        if path.exists():
            return path

    # Fallback: check PATH
    binary_name = "prismlauncher.exe" if sys.platform == "win32" else "prismlauncher"
    result = subprocess.run(["where" if sys.platform == "win32" else "which", binary_name],
                            capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip().split("\n")[0])

    # Fallback: detect Flatpak install if binary not exported
    result = subprocess.run(["flatpak", "info", "--show-location", "org.prismlauncher.PrismLauncher"],
                            capture_output=True, text=True)
    if result.returncode == 0:
        install_path = Path(result.stdout.strip())
        flatpak_bin = install_path / "files/bin/prismlauncher"
        if flatpak_bin.exists():
            return flatpak_bin

    return None


def find_instances_dir():
    """Auto-detect PrismLauncher instances directory (Windows, Linux, macOS, Flatpak)."""
    possible_paths = [
        # Windows
        Path.home() / "AppData/Roaming/PrismLauncher/instances",
        # Linux (native)
        Path.home() / ".local/share/PrismLauncher/instances",
        # macOS
        Path.home() / "Library/Application Support/PrismLauncher/instances",
        # Flatpak (user install)
        Path.home() / ".var/app/org.prismlauncher.PrismLauncher/data/PrismLauncher/instances",
        # Flatpak (system install, rare)
        Path("/var/lib/flatpak/app/org.prismlauncher.PrismLauncher/data/PrismLauncher/instances"),
    ]

    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path

    return None


def get_instances(instances_dir):
    """Get list of valid instance directories."""
    return [d.name for d in instances_dir.iterdir() if d.is_dir()]


def display_instances(instances):
    """Display numbered list of instances with formatting."""
    print(f"Available Minecraft Instances ({len(instances)}):")
    print("-" * 50)
    for i, inst in enumerate(instances, 1):
        print(f"{i}. {inst}")
    print("-" * 50)
    print(f"Total: {len(instances)} instances")


def get_user_choice(instances):
    """Get and validate user's instance choice."""
    try:
        choice = input("\nEnter a number to launch an instance: ").strip()
        idx = int(choice) - 1
        if 0 <= idx < len(instances):
            return instances[idx]
    except ValueError:
        print("Invalid input. Please enter a number.")
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    return None


def launch_instance(prism_exe, instance_name):
    """Launch the selected Minecraft instance."""
    print(f"Launching {instance_name}...")
    subprocess.Popen([str(prism_exe), "--launch", instance_name])


def main():
    print("PrismLauncher Instance Selector")
    print("=" * 50)

    prism_exe = find_prism_exe()
    instances_dir = find_instances_dir()

    if not prism_exe:
        print("Error: Could not find PrismLauncher executable.")
        return

    if not instances_dir:
        print("Error: Could not find instances directory.")
        return

    print(f"Found PrismLauncher at: {prism_exe}")
    print(f"Found instances at: {instances_dir}\n")

    instances = get_instances(instances_dir)
    if not instances:
        print("No instances found.")
        return

    display_instances(instances)
    selected = get_user_choice(instances)

    if selected:
        launch_instance(prism_exe, selected)


if __name__ == "__main__":
    main()
