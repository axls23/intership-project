# Expense Tracker Application

This project is an Expense Tracker application that allows users to manage their expenses through a graphical user interface (GUI) built with Tkinter and a web interface using FastAPI. The application stores expense data in a CSV file and provides functionalities to add, view, filter, and export expenses.

## Project Structure

- **expense.py**: Contains the Tkinter-based GUI application for managing expenses.
- **auto_categorize.py**: Contains the machine learning functionality for auto-categorizing expenses.
- **main.py**: Contains the FastAPI application for the web interface.
- **static/**: Directory for static files like CSS and JavaScript.
- **templates/**: Directory for HTML templates used by FastAPI.

## Class and Function Overview

### `ExpenseTrackerApp` Class (in `expense.py`)

This class is the main component of the Tkinter GUI application. It inherits from `tk.Tk` and provides a window for users to interact with.

- **Attributes**:
  - `categories`: A list of predefined categories for expenses.
  - `expenses`: An in-memory list of expenses loaded from the CSV file.
  - `data_file`: The CSV file used for storing expenses.
  - `categorizer`: An instance of the `ExpenseCategorizer` class for auto-categorization.

- **Methods**:
  - `__init__`: Initializes the application, loads expenses, and sets up the GUI components.
  - `load_expenses`: Loads expenses from the CSV file into memory.
  - `save_expenses`: Saves the current list of expenses to the CSV file.
  - `create_menu`: Sets up the menu bar with options for exporting data, machine learning, and showing an about dialog.
  - `create_tabs`: Creates the tabbed interface for adding, viewing, and summarizing expenses.
  - `create_add_tab`: Sets up the interface for adding new expenses.
  - `auto_categorize`: Automatically categorizes an expense based on its description using machine learning.
  - `add_expense`: Handles the logic for adding a new expense, including validation and saving.
  - `create_view_tab`: Sets up the interface for viewing and filtering expenses.
  - `update_filter_options`: Updates the filter options based on user selection.
  - `apply_filter`: Applies the selected filter to the list of expenses and updates the display.
  - `create_summary_tab`: Sets up the interface for displaying a summary of expenses.
  - `update_summary`: Updates the summary display with total expenses and category breakdowns.
  - `export_data`: Exports the list of expenses to a user-specified CSV file.
  - `show_about`: Displays an about dialog with information about the application.
  - `train_model`: Trains the machine learning model using the current expense data.
  - `test_predictions`: Tests the machine learning model with sample descriptions.

### `ExpenseCategorizer` Class (in `auto_categorize.py`)

This class provides machine learning functionality to automatically categorize expenses based on their descriptions.

- **Attributes**:
  - `model_path`: The path to save or load the trained model.
  - `categories`: A list of predefined categories for expenses.
  - `model`: The trained machine learning model.

- **Methods**:
  - `__init__`: Initializes the categorizer and loads an existing model if available.
  - `train`: Trains the model using expense data from a CSV file.
  - `predict_category`: Predicts the category for a given expense description.
  - `get_confidence`: Gets the confidence score for the prediction.

### FastAPI Application (in `main.py`)

The FastAPI application provides a web interface for managing expenses.

- **Endpoints**:
  - `GET /`: Renders the main page with options to add, view, and summarize expenses.
  - `POST /add_expense`: Adds a new expense based on form data submitted by the user.
  - `GET /export`: Exports the list of expenses as a CSV file.
  - `GET /summary`: Displays a summary of expenses by category.

- **Functions**:
  - `init_csv`: Initializes the CSV file if it doesn't exist.
  - `load_expenses`: Loads expenses from the CSV file.
  - `save_expense`: Saves a new expense to the CSV file.
  - `filter_expenses`: Filters expenses based on user-selected criteria.
  - `get_summary_data`: Generates summary data for expenses.

## Machine Learning for Auto-Categorization

The application uses machine learning to automatically categorize expenses based on their descriptions. It combines two algorithms:

1. **Naive Bayes**: A probabilistic classifier that applies Bayes' theorem with strong independence assumptions between features.
2. **Support Vector Machine (SVM)**: A supervised learning model that analyzes data for classification.

The two algorithms are combined using a voting classifier to improve prediction accuracy. The model is trained on the existing expense data and can be retrained as more data becomes available.

### Auto-Categorization Workflow:

1. **Training**: The model is trained using the descriptions and categories from the existing expense data.
2. **Prediction**: When a user enters a description for a new expense, the model predicts the most likely category.
3. **Confidence**: The model provides a confidence score for its prediction, which is displayed to the user.
4. **Fallback**: If the confidence is too low, the category defaults to "Other".

## Running the Application

To run the Tkinter GUI application, execute `expense.py`:
```bash
python expense.py
```

To run the FastAPI web application, execute `main.py` using Uvicorn:
```bash
uvicorn expense_tracker.main:app --reload
```

Access the web application at `http://localhost:8000/`.

## Dependencies

- Python 3.x
- Tkinter (included with Python)
- FastAPI
- Uvicorn
- pandas
- numpy
- scikit-learn
- joblib

Install the required packages using pip:
```bash
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License. 