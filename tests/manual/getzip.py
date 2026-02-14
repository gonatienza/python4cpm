import zipfile
import os


def get_zip_release():
    _current_dir = os.path.dirname(__file__)
    _tests_dir =  os.path.dirname(_current_dir)
    repo_dir = os.path.dirname(_tests_dir)
    src_folder = os.path.join(repo_dir, "src")
    plugin_folder = os.path.join(src_folder, "plugin")
    python4cpm_folder = os.path.join(src_folder, "python4cpm")
    pol_ini_file = os.path.join(plugin_folder, "Policy-Python4CPM.ini")
    pol_xml_file = os.path.join(plugin_folder, "Policy-Python4CPM.xml")
    process_file = os.path.join(plugin_folder, "Python4CPMProcess.ini")
    prompts_file = os.path.join(plugin_folder, "Python4CPMPrompts.ini")
    python4cpm_file = os.path.join(python4cpm_folder, "python4cpm.py")
    files_to_zip = [
        pol_ini_file,
        pol_xml_file,
        process_file,
        prompts_file,
        python4cpm_file
    ]
    dist_dir = os.path.join(repo_dir, "dist")
    os.makedirs(dist_dir, exist_ok=True)
    build_path = os.path.join(dist_dir, "python4cpm.zip")
    with zipfile.ZipFile(build_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filepath in files_to_zip:
            filename = os.path.basename(filepath)
            zipf.write(filepath, arcname=filename)
    print(f"Successfully created zip -> {build_path}")


if __name__ == "__main__":
    get_zip_release()
