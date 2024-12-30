import glob
import os
import tarfile
import argparse
import shutil
from datetime import datetime
import logging
import stat

# Suppress debug logs from libraries
logging.basicConfig(level=logging.WARNING)

def extract_tar_auto(tar_path, extract_dir):
    """
    Automatically detect the compression format and extract the tar file.
    """
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=extract_dir)
            return
    except tarfile.ReadError:
        pass

    try:
        with tarfile.open(tar_path, "r:") as tar:
            tar.extractall(path=extract_dir)
            return
    except tarfile.ReadError as e:
        raise Exception(f"Failed to extract '{tar_path}'. Error: {e}")

def run_moss_folder(userid, base_folder, target_folder, student_dir, report_dir):
    """
    Run Moss plagiarism detection for Verilog files in folder mode.
    """
    m = mosspy.Moss(userid, "verilog")

    if base_folder is not None:
        base_files = glob.glob(os.path.join(base_folder, "*.v"))

        for base_file in base_files:
            m.addBaseFile(base_file)

    extracted_dirs = []

    for student_tar in glob.glob(os.path.join(student_dir, "**", "*.tar.gz"), recursive=True):
        extract_dir = os.path.join(
            os.path.dirname(student_tar),
            os.path.basename(student_tar).replace(".tar.gz", "")
        )

        try:
            os.chmod(student_tar, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        except Exception as e:
            print(f"Warning: Failed to set permissions for '{student_tar}'. Error: {e}")
            continue
            
        try:
            extract_tar_auto(student_tar, extract_dir)
            extracted_dirs.append(extract_dir)
        except Exception as e:
            print(f"Warning: Failed to extract '{student_tar}'. Error: {e}")
            continue

        for root, _, files in os.walk(extract_dir):
            if os.path.basename(root) == target_folder:
                for file in files:
                    if file.endswith(".v"):
                        file_path = os.path.join(root, file)
                        try:
                            m.addFile(file_path)
                        except Exception as e:
                            print(f"Warning: Failed to add file '{file_path}'. Error: {e}")
                            continue

    return m, extracted_dirs

def run_moss_single(userid, base_file, target_file, student_dir):
    """
    Run Moss plagiarism detection for a single Verilog file.
    """
    m = mosspy.Moss(userid, "verilog")

    if base_file is not None:
        if os.path.exists(base_file):
            m.addBaseFile(base_file)
        else:
            raise FileNotFoundError(f"Base file '{base_file}' not found!")

    extracted_dirs = []

    for student_tar in glob.glob(os.path.join(student_dir, "**", "*.tar.gz"), recursive=True):
        extract_dir = os.path.join(
            os.path.dirname(student_tar),
            os.path.basename(student_tar).replace(".tar.gz", "")
        )

        try:
            os.chmod(student_tar, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
        except Exception as e:
            print(f"Warning: Failed to set permissions for '{student_tar}'. Error: {e}")
            continue

        try:
            extract_tar_auto(student_tar, extract_dir)
            extracted_dirs.append(extract_dir)
        except Exception as e:
            print(f"Warning: Failed to extract '{student_tar}'. Error: {e}")
            continue

        for root, _, files in os.walk(extract_dir):
            for file in files:
                if file.endswith(target_file):
                    file_path = os.path.join(root, file)
                    try:
                        m.addFile(file_path)
                    except Exception as e:
                        print(f"Warning: Failed to add file '{file_path}'. Error: {e}")
                        continue

    return m, extracted_dirs

def save_moss_report(m, extracted_dirs, report_dir):
    """
    Save Moss report and clean up extracted directories.
    """
    url = m.send()
    print("Report URL:", url)

    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    timestamped_report_dir = os.path.join(report_dir, f"{timestamp}")
    os.makedirs(timestamped_report_dir, exist_ok=True)

    report_file = os.path.join(timestamped_report_dir, "report.html")
    m.saveWebPage(url, report_file)
    mosspy.download_report(url, timestamped_report_dir, connections=8)

    if os.path.exists(report_file):
        print(f"Report saved successfully at {report_file}")
    else:
        print("Report saving failed.")

    for dir_path in extracted_dirs:
        if os.path.exists(dir_path):
            try:
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        os.chmod(file_path, stat.S_IWUSR)
                shutil.rmtree(dir_path)
            except Exception as e:
                print(f"Warning: Failed to delete '{dir_path}'. Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Moss plagiarism detection script for Verilog files.")
    parser.add_argument("--mode", type=str, choices=['folder', 'single'], required=True,
                      help="Mode of operation: 'folder' for checking entire folders, 'single' for single file")
    parser.add_argument("--userid", type=int, required=True, help="Your Moss user ID")
    parser.add_argument("--student_dir", type=str, required=True, help="Directory containing student submissions")
    parser.add_argument("--report_dir", type=str, default="report", help="Directory to save the report")
    
    # Folder mode arguments
    parser.add_argument("--base_folder", type=str, help="Path to the base folder containing all reference files.")
    parser.add_argument("--target_folder", type=str, help="Folder that contains the files to be compared.")
    
    # Single file mode arguments
    parser.add_argument("--base_file", type=str, help="Path to the base file (single mode)")
    parser.add_argument("--target_file", type=str, help="Target file name to check (single mode)")

    args = parser.parse_args()

    if args.mode == 'folder':
        if not all([args.target_folder]):
            parser.error("Folder mode requires --base_folder and --target_folder")
        m, extracted_dirs = run_moss_folder(
            userid=args.userid,
            base_folder=args.base_folder,
            target_folder=args.target_folder,
            student_dir=args.student_dir,
            report_dir=args.report_dir
        )
    else:  # single mode
        if not all([args.target_file]):
            parser.error("Single mode requires --base_file and --target_file")
        m, extracted_dirs = run_moss_single(
            userid=args.userid,
            base_file=args.base_file,
            target_file=args.target_file,
            student_dir=args.student_dir
        )

    save_moss_report(m, extracted_dirs, args.report_dir)

if __name__ == "__main__":
    try:
        import mosspy
    except ImportError:
        raise ImportError("mosspy is not installed. Please install it using 'pip install mosspy'")
    main()