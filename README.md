# Moss Verilog Plagiarism Detection Script

This Python script automates running **[Moss (Measure of Software Similarity)](https://theory.stanford.edu/~aiken/moss/)** for Verilog files. It identifies plagiarized or suspiciously similar submissions by comparing students' code to a set of _base_ files (template files).

## Table of Contents
1. [Features](#features)  
2. [How to Register for a Moss User ID](#how-to-register-for-a-moss-user-id)  
3. [Requirements](#requirements)  
4. [Usage](#usage)  
    - [Command-line Arguments](#command-line-arguments)  
    - [Examples](#examples)  
    - [Output](#output)  
5. [Troubleshooting](#troubleshooting)  
6. [Acknowledgments](#acknowledgments)  

---

## Features
- Detects Verilog code similarities using the official Moss service.
- **Two modes** of operation:
  - **folder**: Compare entire folders (submissions must match a specific folder structure).
  - **single**: Compare a single Verilog file (e.g., `my_module.v`).
- Automatically extracts `*.tar.gz` student submissions.
- Compares student submissions against base files/folders in a specified location.
- Saves a detailed report (including code diffs) to a timestamped directory.

---

## How to Register for a Moss User ID

In order to use Moss, you need a personal **Moss user ID**. If you haven't obtained one yet, follow these steps:

1. **Write an email** to: `moss@moss.stanford.edu`  
2. **Subject** (title) can be left blank.  
3. **Email Content** (replace the email address with your own):
 ```
 registeruser
 mail abc1234567@gmail.com
 ```
4. **Send** the email.  
5. You should receive a **reply** from Moss shortly with your **user ID**.

Once you have your user ID, you can use it with this script by passing it to the `--userid` parameter.

---

## Requirements

- **Python 3.6+**  
- [**mosspy**](https://pypi.org/project/mosspy/) (install via `pip install mosspy`)
- Other modules used (included in standard Python library):
  - `glob`
  - `os`
  - `tarfile`
  - `argparse`
  - `shutil`
  - `datetime`
  - `logging`

---

## Usage

1. **Clone** or **Download** this repository.
2. Install the required `mosspy` module:
```bash
pip install mosspy
```
3. Run the script from the command line, choosing a mode:

### Folder Mode
```bash
python main.py \
    --mode folder \
    --userid 123456789 \
    --base_folder /path/to/base_folder \
    --target_folder folder_name \
    --student_dir /path/to/student_submissions \
    --report_dir /path/to/save_report
 ```

### Single File Mode
```bash
python main.py \
    --mode single \
    --userid 123456789 \
    --base_file /path/to/base_file.v \
    --target_file target_file.v \
    --student_dir /path/to/student_submissions \
    --report_dir /path/to/save_report
 ```

---

### Command-line Arguments

| **Argument** | **Description** | **Required** | **Example** |
|----------------------|---------------------------------------------------------------------------------|------------------------------------------------|-----------------------------------------------------------|
| `--mode`             | Operation mode: `folder` or `single`.                                           | Yes                                            | `--mode folder`                                           |
| `--userid`           | Your Moss user ID. Obtain from the Moss registration process.                   | Yes                                            | `--userid 123456789`                                      |
| `--student_dir`      | Directory containing the student submissions (Download and extract by E3)       | Yes                                            | `--student_dir ./submissions`                             |
| `--report_dir`       | Directory to save the Moss report (default: `report`).                          | No                                             | `--report_dir ./report_output`                            |
| **Folder mode only** |                                                                                 |                                                |                                                           |
| `--base_folder`      | Path to the base folder containing `target_folder`.                             | Required when `--mode folder` is used          | `--base_folder ./reference_solutions`                     |
| `--target_folder`    | Subfolder of `base_folder` that will serve as base files.                       | Required when `--mode folder` is used          | `--target_folder lab1`                                    |
| **Single mode only** |                                                                                 |                                                |                                                           |
| `--base_file`        | Path to the base Verilog file (e.g., `reference_module.v`).                     | Required when `--mode single` is used          | `--base_file ./reference_module.v`                        |
| `--target_file`      | **Exact filename** in student submissions to compare.                           | Required when `--mode single` is used          | `--target_file my_module.v`                               |


---

## Examples
Assume you have:
```
.
├── base_folder/
│   └── lab1/
│       ├── build
│       ├── imuldiv
|       |   ├── imuldiv-IntDivIterative.v
|       |   ├── imuldiv-IntMulIterative.v
|       |   └── ... 
|       └── build
|       
├── submissions/
│   ├── studentA/
│   │   └── studentA-lab1.tar.gz
│   └── studentB/
│       └── studentB-lab1.tar.gz
└── main.py
```
### 1. Folder Mode Example
If you only want to compare one Verilog file in a specificed folder:
Run:
```bash
python main.py \
    --mode folder \
    --userid 123456789 \
    --base_folder ./base_folder/lab1 \
    --target_folder imuldiv \
    --student_dir ./submissions \
    --report_dir ./report_output
```
The script will:
- Treat everything in `./base_folder/lab1/imuldiv/` as "base" files.
- Extract all `*.tar.gz` under `./submissions` recursively.
- Compare each `.v` file in `imuldiv` folders from student submissions with the base files.
- Generate a Moss report at `./report_output/YYYY_MM_DD_HH_MM_SS/`.

### 2. Single File Mode Example

If you only want to compare one Verilog file, say `my_module.v`, you can do:

```bash
python main.py \
    --mode single \
    --userid 123456789 \
    --base_file ./base_folder/lab1/imuldiv-IntDivIterative.v \
    --target_file imuldiv-IntDivIterative.v \
    --student_dir ./submissions \
    --report_dir ./report_output
```

The script will:
- Use `/base_folder/lab1/imuldiv-IntDivIterative.v ` as the base reference file.
- Extract all `*.tar.gz` under `./submissions` recursively.
- In each extracted submission, look for files exactly named `imuldiv-IntDivIterative.v`.
- Compare them against your base reference file and generate a Moss report.

---

## Output

- After running, the script will print out a Moss report URL to the console.
- It will then download the entire Moss report (including individual diffs) into a timestamped directory:
 ```
 ./report_output/YYYY_MM_DD_HH_MM_SS/
 ├── report.html
 ├── diff1.html
 ├── diff2.html
 └── ...
 ```
- Open the `report.html` file in a browser to see the detailed results.

---

## Troubleshooting

1. **mosspy not installed**  
 Make sure to install `mosspy` via:
```bash
pip install mosspy
```

2. **No `.v` files found in base folder**  
 Check your `--base_folder` and `--target_folder` paths in folder mode, or your `--base_file` in single mode.

3. **No `.tar.gz` found in student submissions**  
 Confirm your `--student_dir` path and ensure the `.tar.gz` files exist there.

4. **Permission issues on `.tar.gz` files**  
 The script attempts to set the necessary permissions before extracting. If you still encounter issues, manually adjust file permissions or run the script with elevated privileges.

---

## Acknowledgments

We gratefully acknowledge the reference and additional guidance provided by  
[this article](https://hackmd.io/@GjP3NF8qT0SXa2TjRxSKeQ/HJvqIGerE).
