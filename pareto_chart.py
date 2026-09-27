"""
Pareto Chart Utility

This module provides functions for creating a Pareto chart from tabular data
using pandas and Matplotlib.

The module can be used in two ways:

1. As a reusable module
   Import `aggregate_data()` and `create_pareto_chart()` into another
   application, such as a Tkinter dashboard.

   Example:

       from pareto_chart import aggregate_data, create_pareto_chart

       result = aggregate_data(df, "alarm_name")
       fig = create_pareto_chart(result, "alarm_name")

   The `create_pareto_chart()` function returns a Matplotlib Figure object,
   which can be embedded in a Tkinter application using FigureCanvasTkAgg.

2. As a standalone application
   Run this file directly:

       python pareto_chart.py

   A file selection dialog will open. Select a CSV file, then choose the
   column to analyze by entering its column number in the terminal.

   The program will:
   - Load the selected CSV file.
   - Display the available columns.
   - Aggregate the selected column by occurrence count.
   - Calculate the cumulative percentage.
   - Display the aggregation result in the terminal.
   - Show the Pareto chart in a Matplotlib window.

Requirements:
    pandas
    matplotlib
    tkinter
"""
import tkinter as tk
from tkinter import filedialog

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd


# ================================================
#   Settings
# ================================================
BAR_COLOR = "pink"

plt.rcParams["font.family"] = "Yu Gothic"
plt.rcParams["axes.unicode_minus"] = False


# ================================================
#   Aggregate data
# ================================================
def aggregate_data(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    result = (
        df[column_name]
        .value_counts()
        .rename_axis(column_name)
        .reset_index(name="count")
    )

    result["cumulative_percent"] = (
        result["count"].cumsum()
        / result["count"].sum()
        * 100
    )

    return result


def create_pareto_chart(df: pd.DataFrame, column_name: str) -> Figure:
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # X positions
    x = range(len(df))

    # Bar chart
    bars = ax1.bar(
        x,
        df["count"],
        width=1.0,
        align="edge",
        color=BAR_COLOR,
        edgecolor="black",
    )

    ax1.set_xticks(
        [i + 0.5 for i in x],
        df[column_name],
        rotation=90,
    )

    ax1.set_xlabel("")          # Set as needed.
    ax1.set_ylabel("カウント")
    ax1.set_title("パレート図")

    ax1.bar_label(bars, padding=3)

    # ================================================
    #   Cumulative percentage
    # ================================================
    ax2 = ax1.twinx()

    cumulative_percent = [0] + df["cumulative_percent"].tolist()
    line_x = range(len(df) + 1)

    ax2.plot(
        line_x,
        cumulative_percent,
        color="black",
        marker="o",
    )

    # Display cumulative percentage
    for x_pos, percent in zip(line_x[1:], cumulative_percent[1:]):
        ax2.annotate(
            f"{percent:.0f}",
            (x_pos, percent),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
        )

    ax2.set_ylabel("累積比率 (%)")
    ax2.set_ylim(0, 100)

    # Remove left and right margins
    ax1.set_xlim(0, len(df))

    # Make the first cumulative point match
    # the upper-right corner of the first bar.
    first_count = df["count"].iloc[0]
    first_percent = df["cumulative_percent"].iloc[0]

    left_axis_max = first_count / (first_percent / 100)

    ax1.set_ylim(0, left_axis_max)

    # 80% line
    ax2.axhline(
        80,
        color="red",
        linestyle="--",
    )

    fig.tight_layout()

    return fig


# ================================================
#   Main
# ================================================
def main() -> None:
    # Select CSV File
    root = tk.Tk()
    root.withdraw()

    csv_path = filedialog.askopenfilename(
        title="CSVファイルを選択",
        filetypes=[
            ("CSV files", "*.csv"),
            ("All files", "*.*"),
        ]
    )

    root.destroy()

    if not csv_path:
        print("キャンセルしました。")
        return

    try:
        df = pd.read_csv(csv_path)

    except Exception as e:
        print(f"Error: {e}")
        return

    # Display columns
    print()
    print("Columns")
    print("=" * 50)

    for i, column in enumerate(df.columns, start=1):
        print(f"{i}: {column}")

    print()

    # Select column
    try:
        column_number = int(
            input("集計する列番号を入力してください: ")
        )

        if not 1 <= column_number <= len(df.columns):
            raise ValueError

    except ValueError:
        print("正しい列番号を入力してください。")
        return

    column_name = df.columns[column_number - 1]

    # Aggregate
    result = aggregate_data(df, column_name)

    print()
    print("Summary")
    print("=" * 50)
    print(result.to_string(index=False))
    print()

    fig = create_pareto_chart(result, column_name)

    plt.show()


if __name__ == "__main__":
    main()