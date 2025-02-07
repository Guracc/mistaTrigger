import tkinter as tk
from tkinter import filedialog
import os
import glob
import numpy as np
import scipy.io.wavfile as wav

def normalizeVolume(data):
    if data.ndim > 1:
        for i in range(data.shape[1]):
            data[i] = data[i] / np.max(np.abs(data[i]))
    return data

def prepareForExport(data):
    for i in range(data.shape[1]):
        data = np.int16(normalizeVolume(data) * 32767)
    return data

def addTag(sample, f_s, tag, ft_s, interval, tag_volume):
    sample = normalizeVolume(sample)
    non_zero_indices = np.nonzero(tag)[0]
    if len(non_zero_indices) > 0:
        tag = tag[non_zero_indices[0]:non_zero_indices[-1] + 1]
    tag = np.concatenate([tag, np.zeros((interval * f_s) - len(tag))])
    tag = normalizeVolume(tag)
    tag_padded = tag
    while len(tag_padded) < len(sample):
        tag_padded = np.concatenate((tag_padded, tag))
    tag_padded = tag_padded[:len(sample)]
    tag_padded = tag_padded.astype(sample.dtype)
    if sample.ndim > 1:
        for i in range(sample.shape[1]):
            sample[:, i] += tag_padded
    else:
        sample += (tag_padded * tag_volume)
    return sample

def processFile(sample_file, tag_file, interval, tag_volume, output_folder):
    try:
        new_sample_file = sample_file.replace(" ", "_")
        if sample_file != new_sample_file:
            os.rename(sample_file, new_sample_file)
            sample_file = new_sample_file
        f_s, sample = wav.read(sample_file)
        ft_s, tag = wav.read(tag_file)
        if tag.ndim > 1:
            tag = np.mean(tag, axis=1)
        tag = (tag * tag_volume).astype(np.float32)
        processed_sample = addTag(sample, f_s, tag, ft_s, interval, tag_volume)
        processed_sample = prepareForExport(processed_sample)
        os.makedirs(output_folder, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(sample_file))[0]
        output_file = os.path.join(output_folder, f"{base_name}_tag.wav")
        wav.write(output_file, f_s, processed_sample)
        status_label.config(text=f"Processing completed! Output saved to {output_folder}")
    except Exception as e:
        status_label.config(text=f"Error: {e}")

def browseInputFile():
    files = filedialog.askopenfilenames(filetypes=[("WAV files", "*.wav")])
    if files:
        input_path_var.set(";".join(files))

def browseOutput():
    folder = filedialog.askdirectory()
    if folder:
        output_path_var.set(folder)

def startProcessing():
    input_paths = input_path_var.get().split(";")
    tag_file = tag_file_var.get()
    interval = int(interval_var.get())
    tag_volume = float(volume_var.get())
    output_folder = output_path_var.get()
    for sample_file in input_paths:
        processFile(sample_file, tag_file, interval, tag_volume, output_folder)

root = tk.Tk()
root.title("Mista Trigger")
root.configure(bg="#3a2f2f")

input_path_var = tk.StringVar()
tag_file_var = tk.StringVar()
interval_var = tk.StringVar(value="5")
volume_var = tk.DoubleVar(value=1.0)
output_path_var = tk.StringVar()

def create_label(text, row, column):
    tk.Label(root, text=text, bg="#3a2f2f", fg="#ff9800", font=("Arial", 10, "bold")).grid(row=row, column=column, padx=10, pady=5, sticky="w")

def create_entry(variable, row, column, width=40):
    return tk.Entry(root, textvariable=variable, width=width)

create_label("Input Files:", 0, 0)
create_entry(input_path_var, 0, 1).grid(row=0, column=1, padx=10, pady=5)
tk.Button(root, text="Select Files", bg="#ff9800", fg="#000", font=("Arial", 10, "bold"), command=browseInputFile).grid(row=0, column=2, padx=5, pady=5)

create_label("Tag File:", 1, 0)
create_entry(tag_file_var, 1, 1).grid(row=1, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", bg="#ff9800", fg="#000", font=("Arial", 10, "bold"), command=lambda: tag_file_var.set(filedialog.askopenfilename())).grid(row=1, column=2, padx=10, pady=5)

create_label("Interval (s):", 2, 0)
create_entry(interval_var, 2, 1, width=10).grid(row=2, column=1, padx=10, pady=5, sticky="w")

create_label("Tag Volume:", 3, 0)
tk.Scale(root, variable=volume_var, from_=0.5, to=2, resolution=0.1, orient=tk.HORIZONTAL, bg="#3a2f2f", fg="#ff9800", font=("Arial", 10, "bold"), length=200).grid(row=3, column=1, padx=10, pady=5, sticky="w")

create_label("Output Folder:", 4, 0)
create_entry(output_path_var, 4, 1).grid(row=4, column=1, padx=10, pady=5)
tk.Button(root, text="Browse", bg="#ff9800", fg="#000", font=("Arial", 10, "bold"), command=browseOutput).grid(row=4, column=2, padx=10, pady=5)

tk.Button(root, text="Start Processing", bg="#ff9800", fg="#000", font=("Arial", 12, "bold"), command=startProcessing).grid(row=5, column=0, columnspan=3, pady=10)

status_label = tk.Label(root, text="", bg="#3a2f2f", fg="#ff9800", font=("Arial", 10, "bold"))
status_label.grid(row=6, column=0, columnspan=3, pady=5)

root.mainloop()
