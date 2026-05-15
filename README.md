# Professional To-Do List

A modern, visually appealing To-Do list desktop application built using Python and the "customtkinter" library. 

## Features

- **Modern GUI**: A clean and sleek user interface featuring a scrollable task list.
- **Task Management**: Easily add new tasks, mark them as done, and delete them when no longer needed.
- **Visual Cues**: Tasks change text color and display a green tick mark when marked as completed.
- **Persistent Storage**: Your tasks are automatically saved to a local `tasks.json` file, so they persist between sessions.
- **Motivational Quotes**: Displays a changing motivational quote at the bottom of the window to keep you inspired.

## Prerequisites

- Python 3.x installed on your system.
- The `customtkinter` library.

## Installation

1. Clone or download the repository to your local machine.
2. Install the required dependency using `pip`:
   ```bash
   pip install customtkinter
   ```

## Usage

Run the Python script to launch the application:

```bash
python Todolist.py
```

- Type your task in the input field and press **Enter** or click **Add New Task**.
- Click **Mark as Done** to complete a task (you can click **Undo** to revert it).
- Click **Delete Task** to remove a task from the list permanently.
