import os
import edid


def read_edid(path) -> edid.Edid:
    with open(path, "rb") as f:
        content = f.read()
        monitor_info = edid.Edid(content)
        return monitor_info

    return None


def scan_monitors():
    # DRM altındaki tüm edid dosyalarını ara
    monitors = []

    drm_paths = "/sys/class/drm"
    for drm_path in os.listdir(drm_paths):
        try:
            edid_path = os.path.join(drm_paths, drm_path, "edid")

            if not os.path.isfile(edid_path):
                continue

            # Bağlantı noktası adını yoldan çıkar (örn: card0-HDMI-A-1)
            connector_name = edid_path.split("/")[-2]

            edid_info = read_edid(edid_path)

            if edid_info:
                edid_info = edid_info.to_dict()
                edid_info["system_path"] = edid_path
                edid_info["connector"] = connector_name

                monitors.append(edid_info)

        except PermissionError:
            print(
                f"Permission denied: {drm_path}.",
            )
        except Exception as e:
            print(f"Error reading {drm_path}: {e}")

    return monitors
